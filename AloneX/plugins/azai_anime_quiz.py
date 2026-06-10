import random
import time
from datetime import datetime

import pytz
from telethon import Button, events

from AloneX import database, font, prefix_cmds, tbot
from config import ALONE_OWNER_ID, OWNER_ID

IST = pytz.timezone("Asia/Kolkata")
BRAND = font("EGO Network - EST. 2026")
CURRENCY = "EC"

quiz_db = database["azai_anime_quiz"]
score_db = database["azai_anime_quiz_scores"]
wallet_db = database["azai_wallets"]
settings_db = database["azai_quiz_settings"]

CORRECT_EC = 100
CORRECT_XP = 15
DAILY_LIMIT = 10
STREAK_TARGET = 5
STREAK_BONUS_EC = 200
AUTO_INTERVAL_SECONDS = 1800

active_auto_task = None


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


async def get_wallet(user_id: int) -> dict:
    user_id = int(user_id)
    data = await wallet_db.find_one({"user_id": user_id})
    if not data:
        data = {"user_id": user_id, "balance": 0, "xp": 0, "level": 1, "inventory": [], "created_at": now_ist()}
        await wallet_db.insert_one(data)
    return data


async def add_reward(user_id: int, ec: int, xp: int):
    await get_wallet(user_id)
    await wallet_db.update_one(
        {"user_id": int(user_id)},
        {"$inc": {"balance": int(ec), "xp": int(xp)}, "$set": {"updated_at": now_ist()}},
        upsert=True,
    )


def parse_add_quiz(text: str):
    raw = (text or "").split(maxsplit=1)
    if len(raw) < 2:
        return None
    parts = [x.strip() for x in raw[1].split("|")]
    if len(parts) != 5:
        return None
    answer = parts[0]
    options = parts[1:]
    if answer not in options:
        return None
    return answer, options


async def add_anime_quiz(event):
    if not await is_owner(event):
        await event.reply(font("Owner only."))
        return
    reply = await event.get_reply_message()
    if not reply or not reply.media:
        await event.reply(font("Reply to anime image first."))
        return
    parsed = parse_add_quiz(event.raw_text)
    if not parsed:
        await event.reply(font("Use: /addanimeq answer | option1 | option2 | option3 | option4"))
        return
    answer, options = parsed
    qid = str(int(time.time() * 1000))
    await quiz_db.insert_one(
        {
            "qid": qid,
            "answer": answer,
            "options": options,
            "media_chat_id": int(reply.chat_id),
            "media_msg_id": int(reply.id),
            "created_by": int((await event.get_sender()).id),
            "enabled": True,
            "created_at": now_ist(),
        }
    )
    await event.reply(font("Anime quiz saved:") + f" {qid}")


async def random_quiz():
    data = await quiz_db.find({"enabled": True}).to_list(length=100)
    if not data:
        return None
    return random.choice(data)


def quiz_caption(q: dict) -> str:
    options = q.get("options", [])
    letters = ["A", "B", "C", "D"]
    text = font("ANIME QUIZ") + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    text += font("Guess the anime / character.") + "\n\n"
    for i, opt in enumerate(options[:4]):
        text += f"{letters[i]}. {opt}\n"
    text += "\n" + font("Reward: +100 EC +15 XP")
    return text


def quiz_buttons(q: dict):
    rows = []
    qid = q.get("qid")
    letters = ["A", "B", "C", "D"]
    row = []
    for i, _ in enumerate(q.get("options", [])[:4]):
        row.append(Button.inline(font(letters[i]), f"azquiz|{qid}|{i}".encode()))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    return rows


async def send_quiz(chat_id: int, q: dict):
    msg = await tbot.get_messages(int(q["media_chat_id"]), ids=int(q["media_msg_id"]))
    if msg and msg.media:
        await tbot.send_file(chat_id, msg.media, caption=quiz_caption(q), buttons=quiz_buttons(q))
    else:
        await tbot.send_message(chat_id, quiz_caption(q), buttons=quiz_buttons(q))


async def animeguess_handler(event):
    q = await random_quiz()
    if not q:
        await event.reply(font("No anime quiz added yet. Owner can add using /addanimeq."))
        return
    await send_quiz(event.chat_id, q)


async def get_score(user_id: int) -> dict:
    data = await score_db.find_one({"user_id": int(user_id)})
    if not data:
        data = {
            "user_id": int(user_id),
            "correct": 0,
            "wrong": 0,
            "streak": 0,
            "best_streak": 0,
            "daily": {},
            "answered": [],
        }
        await score_db.insert_one(data)
    return data


async def quiz_callback(event):
    try:
        _, qid, index = event.data.decode().split("|", 2)
        index = int(index)
    except Exception:
        await event.answer(font("Invalid quiz."), alert=True)
        return
    sender = await event.get_sender()
    user_id = int(sender.id)
    score = await get_score(user_id)
    answered = set(score.get("answered", []) or [])
    if qid in answered:
        await event.answer(font("You already answered this quiz."), alert=True)
        return
    q = await quiz_db.find_one({"qid": qid, "enabled": True})
    if not q:
        await event.answer(font("Quiz expired."), alert=True)
        return
    options = q.get("options", [])
    if index < 0 or index >= len(options):
        await event.answer(font("Invalid option."), alert=True)
        return
    selected = options[index]
    correct = selected == q.get("answer")
    day = today_key()
    daily = score.get("daily", {}) or {}
    rewarded_today = int(daily.get(day, 0))
    update = {"$addToSet": {"answered": qid}, "$set": {"updated_at": now_ist()}}
    if correct:
        new_streak = int(score.get("streak", 0)) + 1
        best = max(int(score.get("best_streak", 0)), new_streak)
        update["$inc"] = {"correct": 1}
        update["$set"].update({"streak": new_streak, "best_streak": best})
        reward_ec = 0
        reward_xp = 0
        bonus_ec = 0
        if rewarded_today < DAILY_LIMIT:
            reward_ec = CORRECT_EC
            reward_xp = CORRECT_XP
            daily[day] = rewarded_today + 1
            update["$set"]["daily"] = daily
            if new_streak % STREAK_TARGET == 0:
                bonus_ec = STREAK_BONUS_EC
            await add_reward(user_id, reward_ec + bonus_ec, reward_xp)
        msg = font("Correct answer!") + f"\n+{reward_ec} {CURRENCY} +{reward_xp} XP"
        if bonus_ec:
            msg += f"\n{STREAK_TARGET} streak bonus: +{bonus_ec} {CURRENCY}"
        if rewarded_today >= DAILY_LIMIT:
            msg += "\nDaily reward limit reached. Score saved, reward skipped."
        await score_db.update_one({"user_id": user_id}, update, upsert=True)
        await event.answer(msg, alert=True)
    else:
        update["$inc"] = {"wrong": 1}
        update["$set"].update({"streak": 0})
        await score_db.update_one({"user_id": user_id}, update, upsert=True)
        await event.answer(font("Wrong answer."), alert=True)


async def quizstats_handler(event):
    sender = await event.get_sender()
    score = await get_score(sender.id)
    text = (
        font("ANIME QUIZ STATS") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Correct:") + f" {score.get('correct', 0)}\n"
        + font("Wrong:") + f" {score.get('wrong', 0)}\n"
        + font("Current Streak:") + f" {score.get('streak', 0)}\n"
        + font("Best Streak:") + f" {score.get('best_streak', 0)}"
    )
    await event.reply(text)


async def quiztop_handler(event):
    rows = await score_db.find({}).sort("correct", -1).to_list(length=10)
    text = font("ANIME QUIZ TOP") + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    if not rows:
        text += font("No scores yet.")
    else:
        for i, row in enumerate(rows, 1):
            text += f"{i}. `{row.get('user_id')}` - {row.get('correct', 0)} correct\n"
    await event.reply(text)


async def quiz_panel(event):
    total = await quiz_db.count_documents({"enabled": True})
    text = (
        font("QUIZ PANEL") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Anime Quiz:") + f" {total} active questions\n"
        + font("Reward:") + f" {CORRECT_EC} {CURRENCY} + {CORRECT_XP} XP\n"
        + font("Daily Limit:") + f" {DAILY_LIMIT} rewarded quiz\n"
        + font("Streak Bonus:") + f" {STREAK_TARGET} correct = +{STREAK_BONUS_EC} {CURRENCY}"
    )
    buttons = [[Button.inline(font("Start Anime Quiz"), b"azqp_start")]]
    await event.reply(text, buttons=buttons)


async def quiz_toggle(event, enabled: bool):
    if not await is_owner(event):
        await event.reply(font("Owner only."))
        return
    await settings_db.update_one({"chat_id": int(event.chat_id)}, {"$set": {"chat_id": int(event.chat_id), "auto": bool(enabled), "updated_at": now_ist()}}, upsert=True)
    await event.reply(font("Auto quiz enabled." if enabled else "Auto quiz disabled."))


async def quizon_handler(event):
    await quiz_toggle(event, True)


async def quizoff_handler(event):
    await quiz_toggle(event, False)


async def quiz_panel_callback(event):
    if event.data == b"azqp_start":
        await event.answer()
        q = await random_quiz()
        if not q:
            await event.respond(font("No anime quiz added yet."))
            return
        await send_quiz(event.chat_id, q)


if "azai_anime_quiz" not in tbot.handlers_loaded:
    tbot.add_event_handler(add_anime_quiz, events.NewMessage(pattern=f"^{prefix_cmds}addanimeq(?: .*)?$", incoming=True))
    tbot.add_event_handler(animeguess_handler, events.NewMessage(pattern=f"^{prefix_cmds}animeguess(?:@\\w+)?$", incoming=True))
    tbot.add_event_handler(quiz_panel, events.NewMessage(pattern=f"^{prefix_cmds}quiz(?:@\\w+)?$", incoming=True))
    tbot.add_event_handler(quizstats_handler, events.NewMessage(pattern=f"^{prefix_cmds}quizstats(?:@\\w+)?$", incoming=True))
    tbot.add_event_handler(quiztop_handler, events.NewMessage(pattern=f"^{prefix_cmds}quiztop(?:@\\w+)?$", incoming=True))
    tbot.add_event_handler(quizon_handler, events.NewMessage(pattern=f"^{prefix_cmds}quizon(?:@\\w+)?$", incoming=True))
    tbot.add_event_handler(quizoff_handler, events.NewMessage(pattern=f"^{prefix_cmds}quizoff(?:@\\w+)?$", incoming=True))
    tbot.add_event_handler(quiz_callback, events.CallbackQuery(pattern=b"^azquiz\\|"))
    tbot.add_event_handler(quiz_panel_callback, events.CallbackQuery(pattern=b"^azqp_"))
    tbot.handlers_loaded.add("azai_anime_quiz")
