import asyncio
import random
from datetime import datetime

import pytz
import shortuuid
from telethon import Button, events

from AloneX import database, font, prefix_cmds, tbot
from config import ALONE_OWNER_ID, OWNER_ID

IST = pytz.timezone("Asia/Kolkata")
BRAND = font("EGO Network - EST. 2026")
CURRENCY = "EC"

questions_db = database["azai_anime_questions"]
sessions_db = database["azai_anime_sessions"]
stats_db = database["azai_anime_stats"]
auto_db = database["azai_anime_auto"]
wallet_db = database["azai_wallets"]

CORRECT_EC = 100
CORRECT_XP = 15
DAILY_LIMIT = 10
STREAK_BONUS_EC = 200
AUTO_SECONDS = 1800


def today_key() -> str:
    return datetime.now(IST).strftime("%Y-%m-%d")


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


async def can_manage(event) -> bool:
    if await is_owner(event):
        return True
    if event.is_private:
        return False
    sender = await event.get_sender()
    try:
        perms = await event.client.get_permissions(event.chat_id, sender.id)
        return bool(getattr(perms, "is_admin", False) or getattr(perms, "is_creator", False))
    except Exception:
        return False


async def random_question():
    docs = await questions_db.aggregate([{"$sample": {"size": 1}}]).to_list(length=1)
    return docs[0] if docs else None


async def question_media(question: dict):
    try:
        msg = await tbot.get_messages(int(question["media_chat_id"]), ids=int(question["media_msg_id"]))
        if msg and msg.media:
            return msg.media
    except Exception:
        return None
    return None


async def add_wallet_reward(user_id: int, ec: int, xp: int):
    await wallet_db.update_one(
        {"user_id": int(user_id)},
        {"$inc": {"balance": int(ec), "xp": int(xp)}, "$set": {"updated_at": now_ist()}},
        upsert=True,
    )


def quiz_caption(options: list[str]) -> str:
    letters = ["A", "B", "C", "D"]
    text = font("ANIME QUIZ") + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    text += font("Guess the anime / character.") + "\n\n"
    for i, option in enumerate(options[:4]):
        text += f"{letters[i]}. {option}\n"
    text += "\n" + font("Tap one option. One attempt only.")
    return text


def option_buttons(session_id: str, options: list[str]):
    letters = ["A", "B", "C", "D"]
    rows = []
    for i, option in enumerate(options[:4]):
        rows.append([Button.inline(font(f"{letters[i]}. {option}"), f"azaq|{session_id}|{i}".encode())])
    return rows


async def send_quiz(chat_id: int):
    q = await random_question()
    if not q:
        return False
    session_id = shortuuid.uuid()[:10]
    options = q.get("options", [])[:4]
    random.shuffle(options)
    caption = quiz_caption(options)
    media = await question_media(q)
    if media:
        sent = await tbot.send_file(chat_id, media, caption=caption, buttons=option_buttons(session_id, options))
    else:
        sent = await tbot.send_message(chat_id, caption, buttons=option_buttons(session_id, options))
    await sessions_db.update_one(
        {"session_id": session_id},
        {"$set": {
            "session_id": session_id,
            "chat_id": int(chat_id),
            "message_id": int(sent.id),
            "answer": q.get("answer"),
            "options": options,
            "answered": [],
            "created_at": now_ist(),
        }},
        upsert=True,
    )
    return True


async def addanimeq_handler(event):
    if not await is_owner(event):
        await event.reply(font("Owner only."))
        return
    reply = await event.get_reply_message()
    if not reply or not reply.media:
        await event.reply(font("Reply to anime image and use: /addanimeq answer | option1 | option2 | option3 | option4"))
        return
    raw = (event.raw_text or "").split(maxsplit=1)
    if len(raw) < 2:
        await event.reply(font("Use: /addanimeq answer | option1 | option2 | option3 | option4"))
        return
    parts = [x.strip() for x in raw[1].split("|") if x.strip()]
    if len(parts) != 5:
        await event.reply(font("Need exactly 5 parts: answer | option1 | option2 | option3 | option4"))
        return
    answer = parts[0]
    options = parts[1:]
    if answer.lower() not in [x.lower() for x in options]:
        await event.reply(font("Answer must be one of the 4 options."))
        return
    await questions_db.insert_one({
        "answer": answer,
        "options": options,
        "media_chat_id": int(reply.chat_id),
        "media_msg_id": int(reply.id),
        "created_by": int((await event.get_sender()).id),
        "created_at": now_ist(),
    })
    await event.reply(font("Anime quiz added."))


async def animeguess_handler(event):
    ok = await send_quiz(event.chat_id)
    if not ok:
        await event.reply(font("No anime quiz added yet. Owner can add with /addanimeq."))


async def quiz_panel_handler(event):
    buttons = [
        [Button.inline(font("Start Anime Quiz"), b"azquiz_start")],
        [Button.inline(font("My Stats"), b"azquiz_stats"), Button.inline(font("Top"), b"azquiz_top")],
        [Button.inline(font("Close"), b"azquiz_close")],
    ]
    await event.reply(font("AZAI QUIZ PANEL") + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n" + font("Choose an option."), buttons=buttons)


async def reward_user(user_id: int, correct: bool):
    stats = await stats_db.find_one({"user_id": int(user_id)}) or {"user_id": int(user_id), "correct": 0, "wrong": 0, "streak": 0, "best_streak": 0, "daily_date": today_key(), "daily_count": 0}
    if stats.get("daily_date") != today_key():
        stats["daily_date"] = today_key()
        stats["daily_count"] = 0
    ec = 0
    xp = 0
    bonus = 0
    if correct:
        stats["correct"] = int(stats.get("correct", 0)) + 1
        stats["streak"] = int(stats.get("streak", 0)) + 1
        stats["best_streak"] = max(int(stats.get("best_streak", 0)), int(stats["streak"]))
        if int(stats.get("daily_count", 0)) < DAILY_LIMIT:
            ec = CORRECT_EC
            xp = CORRECT_XP
            stats["daily_count"] = int(stats.get("daily_count", 0)) + 1
            if stats["streak"] % 5 == 0:
                bonus = STREAK_BONUS_EC
                ec += bonus
            await add_wallet_reward(user_id, ec, xp)
    else:
        stats["wrong"] = int(stats.get("wrong", 0)) + 1
        stats["streak"] = 0
    await stats_db.update_one({"user_id": int(user_id)}, {"$set": stats}, upsert=True)
    return stats, ec, xp, bonus


async def answer_callback(event):
    try:
        _, session_id, idx = event.data.decode().split("|", 2)
        idx = int(idx)
    except Exception:
        await event.answer(font("Invalid answer."), alert=True)
        return
    session = await sessions_db.find_one({"session_id": session_id})
    if not session:
        await event.answer(font("Quiz expired."), alert=True)
        return
    sender = await event.get_sender()
    answered = session.get("answered", []) or []
    if int(sender.id) in answered:
        await event.answer(font("You already attempted this quiz."), alert=True)
        return
    options = session.get("options", [])
    if idx >= len(options):
        await event.answer(font("Invalid option."), alert=True)
        return
    selected = options[idx]
    answer = session.get("answer", "")
    is_correct = selected.lower() == str(answer).lower()
    await sessions_db.update_one({"session_id": session_id}, {"$addToSet": {"answered": int(sender.id)}})
    stats, ec, xp, bonus = await reward_user(sender.id, is_correct)
    if is_correct:
        msg = f"Correct! +{ec} {CURRENCY} +{xp} XP"
        if bonus:
            msg += f" | Streak bonus +{bonus} {CURRENCY}"
        if ec == 0:
            msg = "Correct! Daily reward limit reached."
    else:
        msg = f"Wrong. Correct answer: {answer}"
    await event.answer(font(msg), alert=True)


async def stats_text(user_id: int) -> str:
    s = await stats_db.find_one({"user_id": int(user_id)}) or {}
    return (
        font("QUIZ STATS") + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Correct:") + f" {s.get('correct', 0)}\n"
        + font("Wrong:") + f" {s.get('wrong', 0)}\n"
        + font("Current Streak:") + f" {s.get('streak', 0)}\n"
        + font("Best Streak:") + f" {s.get('best_streak', 0)}\n"
        + font("Daily Rewards:") + f" {s.get('daily_count', 0)}/{DAILY_LIMIT}"
    )


async def quizstats_handler(event):
    sender = await event.get_sender()
    await event.reply(await stats_text(sender.id))


async def quiztop_handler(event):
    rows = await stats_db.find({}).sort("correct", -1).limit(10).to_list(length=10)
    text = font("QUIZ TOP") + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    if not rows:
        text += font("No quiz stats yet.")
    for i, row in enumerate(rows, 1):
        text += f"{i}. {row.get('user_id')} - {row.get('correct', 0)} correct\n"
    await event.reply(text)


async def quiz_toggle(event, enabled: bool):
    if not await can_manage(event):
        await event.reply(font("Admin only."))
        return
    await auto_db.update_one({"chat_id": int(event.chat_id)}, {"$set": {"chat_id": int(event.chat_id), "enabled": bool(enabled), "updated_at": now_ist()}}, upsert=True)
    await event.reply(font("Auto quiz enabled." if enabled else "Auto quiz disabled."))


async def quizon_handler(event):
    await quiz_toggle(event, True)


async def quizoff_handler(event):
    await quiz_toggle(event, False)


async def quiz_panel_callback(event):
    data = event.data.decode()
    if data == "azquiz_close":
        await event.delete()
    elif data == "azquiz_start":
        await event.answer(font("Starting quiz..."))
        await send_quiz(event.chat_id)
    elif data == "azquiz_stats":
        sender = await event.get_sender()
        await event.answer()
        await event.edit(await stats_text(sender.id), buttons=[[Button.inline(font("Back"), b"azquiz_back"), Button.inline(font("Close"), b"azquiz_close")]])
    elif data == "azquiz_top":
        await event.answer(font("Use /quiztop to see leaderboard."), alert=True)
    elif data == "azquiz_back":
        await quiz_panel_handler(event)


async def auto_quiz_loop():
    await asyncio.sleep(10)
    while True:
        await asyncio.sleep(AUTO_SECONDS)
        try:
            rows = await auto_db.find({"enabled": True}).to_list(length=200)
            for row in rows:
                try:
                    await send_quiz(int(row["chat_id"]))
                except Exception:
                    pass
        except Exception:
            pass


if "aaa_azai_anime_quiz" not in tbot.handlers_loaded:
    tbot.add_event_handler(addanimeq_handler, events.NewMessage(pattern=f"^{prefix_cmds}addanimeq(?: .*)?$", incoming=True))
    tbot.add_event_handler(animeguess_handler, events.NewMessage(pattern=f"^{prefix_cmds}animeguess(?:@\\w+)?$", incoming=True))
    tbot.add_event_handler(quiz_panel_handler, events.NewMessage(pattern=f"^{prefix_cmds}quiz(?:@\\w+)?$", incoming=True))
    tbot.add_event_handler(quizstats_handler, events.NewMessage(pattern=f"^{prefix_cmds}quizstats(?:@\\w+)?$", incoming=True))
    tbot.add_event_handler(quiztop_handler, events.NewMessage(pattern=f"^{prefix_cmds}quiztop(?:@\\w+)?$", incoming=True))
    tbot.add_event_handler(quizon_handler, events.NewMessage(pattern=f"^{prefix_cmds}quizon(?:@\\w+)?$", incoming=True))
    tbot.add_event_handler(quizoff_handler, events.NewMessage(pattern=f"^{prefix_cmds}quizoff(?:@\\w+)?$", incoming=True))
    tbot.add_event_handler(answer_callback, events.CallbackQuery(pattern=b"^azaq\\|"))
    tbot.add_event_handler(quiz_panel_callback, events.CallbackQuery(pattern=b"^azquiz_"))
    try:
        tbot.loop.create_task(auto_quiz_loop())
    except Exception:
        pass
    tbot.handlers_loaded.add("aaa_azai_anime_quiz")
