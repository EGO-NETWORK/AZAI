import asyncio
import random
import time
import uuid
from datetime import datetime

import pytz
from telethon import Button, events

from AloneX import database, font, prefix_cmds, tbot
from config import ALONE_OWNER_ID, OWNER_ID

IST = pytz.timezone("Asia/Kolkata")
BRAND = font("EGO Network - EST. 2026")
CURRENCY = "EC"
REWARD_EC = 150
REWARD_XP = 15
QUIZ_TIMEOUT_SECONDS = 180
AUTO_INTERVAL_SECONDS = 30 * 60
AUTO_CHECK_SECONDS = 60

questions_db = database["azai_anime_quiz_questions_clean"]
sessions_db = database["azai_anime_quiz_sessions_clean"]
scores_db = database["azai_anime_quiz_scores_clean"]
auto_db = database["azai_anime_quiz_auto_clean"]
wallet_db = database["azai_wallets"]


def now_ist() -> str:
    return datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S")


def owner_ids() -> set[int]:
    ids = set()
    for value in (ALONE_OWNER_ID, OWNER_ID):
        try:
            value = int(value)
            if value:
                ids.add(value)
        except Exception:
            pass
    return ids


async def is_owner(event) -> bool:
    sender = await event.get_sender()
    return bool(sender and int(sender.id) in owner_ids())


def level_from_xp(xp: int) -> int:
    if xp >= 900:
        return 5
    if xp >= 500:
        return 4
    if xp >= 250:
        return 3
    if xp >= 100:
        return 2
    return 1


async def add_wallet_reward(user, ec: int, xp: int):
    user_id = int(user.id)
    row = await wallet_db.find_one({"user_id": user_id}) or {}
    new_xp = int(row.get("xp", 0)) + int(xp)
    await wallet_db.update_one(
        {"user_id": user_id},
        {
            "$inc": {"balance": int(ec), "xp": int(xp)},
            "$set": {
                "user_id": user_id,
                "name": getattr(user, "first_name", None) or getattr(user, "username", None) or "Unknown User",
                "username": getattr(user, "username", None),
                "level": level_from_xp(new_xp),
                "updated_at": now_ist(),
            },
        },
        upsert=True,
    )


async def update_score(user, correct: bool):
    user_id = int(user.id)
    await scores_db.update_one(
        {"user_id": user_id},
        {
            "$inc": {"attempts": 1, "correct": 1 if correct else 0, "wrong": 0 if correct else 1},
            "$set": {
                "user_id": user_id,
                "name": getattr(user, "first_name", None) or getattr(user, "username", None) or "Unknown User",
                "username": getattr(user, "username", None),
                "updated_at": now_ist(),
            },
        },
        upsert=True,
    )


def parse_question(raw_text: str):
    text = (raw_text or "").split(maxsplit=1)
    if len(text) < 2:
        return None
    parts = [part.strip() for part in text[1].split("|")]
    if len(parts) != 5 or any(not part for part in parts):
        return None
    answer = parts[0]
    options = parts[1:]
    if answer.lower() not in {item.lower() for item in options}:
        return None
    return answer, options


def question_panel_text(qid: str, added: int = 0) -> str:
    return (
        font("ANIME QUIZ SAVED") + "\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Question ID:") + f" {qid}\n"
        + font("Total Questions:") + f" {added}\n"
        + font("Mode:") + " Image quiz only\n"
        + font("Play:") + " /animeguess"
    )


async def addanimeq_handler(event):
    if not await is_owner(event):
        await event.reply(font("Owner only."))
        return
    reply = await event.get_reply_message()
    if not reply or not reply.media:
        await event.reply(font("Reply to quiz image first."))
        return
    parsed = parse_question(event.raw_text or "")
    if not parsed:
        await event.reply(font("Use: /addanimeq answer | option1 | option2 | option3 | option4\nAnswer must be one of the options."))
        return
    answer, options = parsed
    qid = uuid.uuid4().hex[:8]
    await questions_db.insert_one(
        {
            "qid": qid,
            "answer": answer,
            "options": options,
            "media_chat_id": int(reply.chat_id),
            "media_msg_id": int(reply.id),
            "active": True,
            "created_at": now_ist(),
        }
    )
    total = await questions_db.count_documents({"active": True})
    await event.reply(question_panel_text(qid, total))
    raise events.StopPropagation


async def get_active_session(chat_id: int):
    session = await sessions_db.find_one({"chat_id": int(chat_id), "active": True})
    if not session:
        return None
    if int(time.time()) > int(session.get("expires_at", 0)):
        await sessions_db.update_one({"_id": session["_id"]}, {"$set": {"active": False, "expired_at": now_ist()}})
        return None
    return session


async def pick_question():
    total = await questions_db.count_documents({"active": True})
    if total <= 0:
        return None
    skip = random.randint(0, total - 1)
    cursor = questions_db.find({"active": True}).skip(skip).limit(1)
    async for row in cursor:
        return row
    return None


def quiz_caption() -> str:
    return (
        font("ANIME QUIZ") + "\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Guess the anime / character from this image.") + "\n\n"
        + font("Reward:") + f" {REWARD_EC} {CURRENCY}\n"
        + font("One attempt per user.")
    )


def option_buttons(options: list[str]):
    rows = []
    for idx, option in enumerate(options):
        rows.append([Button.inline(font(option[:30]), f"azq_ans:{idx}".encode())])
    return rows


async def create_session(chat_id: int, question: dict) -> dict:
    options = list(question.get("options", []))
    random.shuffle(options)
    correct_index = next((i for i, opt in enumerate(options) if opt.lower() == str(question.get("answer", "")).lower()), 0)
    session = {
        "session_id": uuid.uuid4().hex[:10],
        "chat_id": int(chat_id),
        "qid": question["qid"],
        "answer": question["answer"],
        "options": options,
        "correct_index": correct_index,
        "answered_users": [],
        "active": True,
        "created_at": now_ist(),
        "expires_at": int(time.time()) + QUIZ_TIMEOUT_SECONDS,
    }
    await sessions_db.update_many({"chat_id": int(chat_id), "active": True}, {"$set": {"active": False}})
    await sessions_db.insert_one(session)
    return session


async def send_quiz_to_chat(chat_id: int, question: dict):
    session = await create_session(chat_id, question)
    media = None
    try:
        msg = await tbot.get_messages(int(question["media_chat_id"]), ids=int(question["media_msg_id"]))
        media = msg.media if msg else None
    except Exception:
        media = None
    if media:
        await tbot.send_file(chat_id, media, caption=quiz_caption(), buttons=option_buttons(session["options"]))
    else:
        await tbot.send_message(chat_id, quiz_caption(), buttons=option_buttons(session["options"]))


async def animeguess_handler(event):
    existing = await get_active_session(event.chat_id)
    if existing:
        await event.reply(font("One anime quiz is already active. Answer it first or wait for timeout."))
        return
    question = await pick_question()
    if not question:
        await event.reply(font("No anime quiz questions added yet."))
        return
    await send_quiz_to_chat(event.chat_id, question)
    raise events.StopPropagation


async def quiz_answer_callback(event):
    data = event.data.decode()
    try:
        index = int(data.split(":", 1)[1])
    except Exception:
        await event.answer("Invalid answer.", alert=True)
        return
    session = await get_active_session(event.chat_id)
    if not session:
        await event.answer("This quiz has expired.", alert=True)
        return
    user = await event.get_sender()
    user_id = int(user.id)
    answered = [int(x) for x in session.get("answered_users", [])]
    if user_id in answered:
        await event.answer("One attempt only.", alert=True)
        return
    await sessions_db.update_one({"_id": session["_id"]}, {"$addToSet": {"answered_users": user_id}})
    correct = index == int(session.get("correct_index", -1))
    await update_score(user, correct)
    if correct:
        await add_wallet_reward(user, REWARD_EC, REWARD_XP)
        await sessions_db.update_one({"_id": session["_id"]}, {"$set": {"active": False, "winner_id": user_id, "closed_at": now_ist()}})
        winner = getattr(user, "first_name", None) or getattr(user, "username", None) or "User"
        text = (
            font("CORRECT ANSWER") + "\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            + font("Winner:") + f" {winner}\n"
            + font("Answer:") + f" {session.get('answer')}\n"
            + font("Reward:") + f" {REWARD_EC} {CURRENCY} + {REWARD_XP} XP"
        )
        await event.edit(text, buttons=None)
        await event.answer(f"Correct! +{REWARD_EC} {CURRENCY}", alert=True)
        return
    await event.answer("Wrong answer. One attempt used.", alert=True)


async def quizstats_handler(event):
    user = await event.get_sender()
    row = await scores_db.find_one({"user_id": int(user.id)}) or {}
    text = (
        font("ANIME QUIZ STATS") + "\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Correct:") + f" {int(row.get('correct', 0))}\n"
        + font("Wrong:") + f" {int(row.get('wrong', 0))}\n"
        + font("Attempts:") + f" {int(row.get('attempts', 0))}"
    )
    await event.reply(text)
    raise events.StopPropagation


async def quiztop_handler(event):
    rows = await scores_db.find({}).sort("correct", -1).to_list(length=10)
    text = font("ANIME QUIZ TOP") + "\n━━━━━━━━━━━━━━━━━━━━\n\n"
    if not rows:
        text += font("No scores yet.")
    else:
        for i, row in enumerate(rows, 1):
            name = row.get("name") or row.get("username") or str(row.get("user_id"))
            text += f"{i}. {name} - {int(row.get('correct', 0))}\n"
    await event.reply(text)
    raise events.StopPropagation


async def quizlist_handler(event):
    if not await is_owner(event):
        await event.reply(font("Owner only."))
        return
    rows = await questions_db.find({"active": True}).sort("created_at", -1).to_list(length=30)
    text = font("ANIME QUIZ QUESTIONS") + "\n━━━━━━━━━━━━━━━━━━━━\n\n"
    if not rows:
        text += font("No active questions.")
    else:
        for row in rows:
            text += f"{row.get('qid')} - {row.get('answer')}\n"
    await event.reply(text)
    raise events.StopPropagation


async def delanimeq_handler(event):
    if not await is_owner(event):
        await event.reply(font("Owner only."))
        return
    parts = (event.raw_text or "").split(maxsplit=1)
    if len(parts) < 2:
        await event.reply(font("Use: /delanimeq question_id"))
        return
    qid = parts[1].strip()
    res = await questions_db.update_one({"qid": qid}, {"$set": {"active": False, "deleted_at": now_ist()}})
    await event.reply(font("Deleted." if res.modified_count else "Question not found."))
    raise events.StopPropagation


async def set_auto(chat_id: int, enabled: bool, user_id: int = 0):
    now = int(time.time())
    await auto_db.update_one(
        {"chat_id": int(chat_id)},
        {
            "$set": {
                "chat_id": int(chat_id),
                "enabled": bool(enabled),
                "interval": AUTO_INTERVAL_SECONDS,
                "next_at": now + AUTO_INTERVAL_SECONDS if enabled else None,
                "updated_by": int(user_id or 0),
                "updated_at": now_ist(),
            }
        },
        upsert=True,
    )


async def auto_status_text(chat_id: int) -> str:
    row = await auto_db.find_one({"chat_id": int(chat_id)}) or {}
    enabled = bool(row.get("enabled", False))
    next_at = int(row.get("next_at") or 0)
    wait = max(next_at - int(time.time()), 0) if enabled else 0
    return (
        font("ANIME QUIZ AUTO") + "\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Status:") + f" {'ON' if enabled else 'OFF'}\n"
        + font("Interval:") + " 30 minutes\n"
        + font("Next Quiz In:") + f" {wait // 60} min {wait % 60} sec\n\n"
        + font("Rule:") + " one saved quiz at a time, never all together."
    )


async def quizon_handler(event):
    if not await is_owner(event):
        await event.reply(font("Owner only."))
        return
    sender = await event.get_sender()
    await set_auto(event.chat_id, True, sender.id if sender else 0)
    await event.reply(await auto_status_text(event.chat_id))
    raise events.StopPropagation


async def quizoff_handler(event):
    if not await is_owner(event):
        await event.reply(font("Owner only."))
        return
    sender = await event.get_sender()
    await set_auto(event.chat_id, False, sender.id if sender else 0)
    await event.reply(await auto_status_text(event.chat_id))
    raise events.StopPropagation


async def quizauto_handler(event):
    await event.reply(await auto_status_text(event.chat_id))
    raise events.StopPropagation


async def quiz_auto_loop():
    await asyncio.sleep(20)
    while True:
        try:
            now = int(time.time())
            async for row in auto_db.find({"enabled": True}):
                chat_id = int(row.get("chat_id", 0) or 0)
                if not chat_id:
                    continue
                next_at = int(row.get("next_at") or 0)
                if next_at > now:
                    continue
                if await get_active_session(chat_id):
                    await auto_db.update_one({"chat_id": chat_id}, {"$set": {"next_at": now + 60, "updated_at": now_ist()}}, upsert=True)
                    continue
                question = await pick_question()
                if question:
                    await send_quiz_to_chat(chat_id, question)
                await auto_db.update_one(
                    {"chat_id": chat_id},
                    {"$set": {"next_at": now + AUTO_INTERVAL_SECONDS, "last_sent_at": now_ist(), "updated_at": now_ist()}},
                    upsert=True,
                )
        except Exception as e:
            print(f"AZAI Anime Quiz Auto Error: {e}")
        await asyncio.sleep(AUTO_CHECK_SECONDS)


if "azai_anime_quiz_clean" not in tbot.handlers_loaded:
    tbot.add_event_handler(addanimeq_handler, events.NewMessage(pattern=f"^{prefix_cmds}addanimeq(?: .*)?$", incoming=True))
    tbot.add_event_handler(animeguess_handler, events.NewMessage(pattern=f"^{prefix_cmds}(animeguess|quiz)(?:@\\w+)?$", incoming=True))
    tbot.add_event_handler(quizstats_handler, events.NewMessage(pattern=f"^{prefix_cmds}quizstats(?:@\\w+)?$", incoming=True))
    tbot.add_event_handler(quiztop_handler, events.NewMessage(pattern=f"^{prefix_cmds}quiztop(?:@\\w+)?$", incoming=True))
    tbot.add_event_handler(quizlist_handler, events.NewMessage(pattern=f"^{prefix_cmds}quizlist(?:@\\w+)?$", incoming=True))
    tbot.add_event_handler(delanimeq_handler, events.NewMessage(pattern=f"^{prefix_cmds}delanimeq(?: .*)?$", incoming=True))
    tbot.add_event_handler(quizon_handler, events.NewMessage(pattern=f"^{prefix_cmds}quizon(?:@\\w+)?$", incoming=True))
    tbot.add_event_handler(quizoff_handler, events.NewMessage(pattern=f"^{prefix_cmds}quizoff(?:@\\w+)?$", incoming=True))
    tbot.add_event_handler(quizauto_handler, events.NewMessage(pattern=f"^{prefix_cmds}quizauto(?:@\\w+)?$", incoming=True))
    tbot.add_event_handler(quiz_answer_callback, events.CallbackQuery(pattern=b"^azq_ans:"))
    tbot.loop.create_task(quiz_auto_loop())
    tbot.handlers_loaded.add("azai_anime_quiz_clean")
