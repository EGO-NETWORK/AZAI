import asyncio
import os
import random
import time

from telethon import Button, events

from AloneX import database, font, prefix_cmds, tbot

QUIZ_INTERVAL = int(os.getenv("AZAI_ANIME_QUIZ_INTERVAL", "1800"))
REWARD = int(os.getenv("AZAI_ANIME_QUIZ_REWARD", "150"))

chat_db = database["azai_anime_quiz_chats"]
active_db = database["azai_anime_quiz_active"]
wallet_db = database["azai_wallets"]

QUESTIONS = [
    {
        "q": "Which anime has a notebook that can cause death when a name is written in it?",
        "options": ["Death Note", "Bleach", "Naruto", "One Piece"],
        "answer": 0,
    },
    {
        "q": "In Naruto, what is the energy system used by shinobi called?",
        "options": ["Nen", "Chakra", "Haki", "Ki"],
        "answer": 1,
    },
    {
        "q": "Which anime follows Monkey D. Luffy and his crew?",
        "options": ["Black Clover", "One Piece", "Tokyo Revengers", "Demon Slayer"],
        "answer": 1,
    },
    {
        "q": "In Demon Slayer, what weapon do demon slayers mainly use?",
        "options": ["Nichirin Sword", "Kunai", "Death Scythe", "Gunblade"],
        "answer": 0,
    },
    {
        "q": "Which anime features Titans as a major threat?",
        "options": ["Attack on Titan", "Haikyuu", "Blue Lock", "Dr. Stone"],
        "answer": 0,
    },
    {
        "q": "Which anime is centered around volleyball?",
        "options": ["Blue Lock", "Haikyuu", "Kuroko no Basket", "Free"],
        "answer": 1,
    },
    {
        "q": "In Dragon Ball, what are the magical wish-granting objects called?",
        "options": ["Soul Stones", "Dragon Balls", "Sacred Gems", "Spirit Orbs"],
        "answer": 1,
    },
    {
        "q": "Which anime focuses on heroes, quirks, and U.A. High School?",
        "options": ["My Hero Academia", "Jujutsu Kaisen", "Mob Psycho", "Spy x Family"],
        "answer": 0,
    },
]


def quiz_id(chat_id):
    return f"{chat_id}:{int(time.time())}:{random.randint(1000,9999)}"


def quiz_text(question):
    return (
        font("ANIME QUIZ")
        + "\n━━━━━━━━━━━━━━━━━━━━\n"
        + font(question["q"])
        + "\n\n"
        + font("Reward:") + f" {REWARD} EC\n"
        + font("One attempt only.")
    )


def quiz_buttons(qid, question):
    rows = []
    opts = question["options"]
    for i in range(0, len(opts), 2):
        row = []
        for idx in range(i, min(i + 2, len(opts))):
            row.append(Button.inline(font(opts[idx]), f"azai_anime:{qid}:{idx}".encode()))
        rows.append(row)
    return rows


async def register_chat(event):
    if event.is_private:
        return
    await chat_db.update_one(
        {"chat_id": int(event.chat_id)},
        {"$set": {"chat_id": int(event.chat_id), "enabled": True, "last_seen": int(time.time())}},
        upsert=True,
    )


async def send_quiz(chat_id):
    question = random.choice(QUESTIONS)
    qid = quiz_id(chat_id)
    await active_db.update_one(
        {"quiz_id": qid},
        {"$set": {"quiz_id": qid, "chat_id": int(chat_id), "question": question, "answered": [], "created_at": int(time.time())}},
        upsert=True,
    )
    await tbot.send_message(int(chat_id), quiz_text(question), buttons=quiz_buttons(qid, question))


async def animeguess(event):
    await register_chat(event)
    await send_quiz(event.chat_id)
    raise events.StopPropagation


async def animequiz_toggle(event):
    if event.is_private:
        await event.reply(font("Use this command inside a group."))
        raise events.StopPropagation
    arg = ""
    parts = (event.raw_text or "").split(maxsplit=1)
    if len(parts) > 1:
        arg = parts[1].strip().lower()
    if arg not in {"on", "off"}:
        await event.reply(font("Use: /animequiz on or /animequiz off"))
        raise events.StopPropagation
    enabled = arg == "on"
    await chat_db.update_one({"chat_id": int(event.chat_id)}, {"$set": {"chat_id": int(event.chat_id), "enabled": enabled, "updated_at": int(time.time())}}, upsert=True)
    await event.reply(font(f"Anime quiz auto {'ON' if enabled else 'OFF'} for this group."))
    raise events.StopPropagation


async def anime_answer(event):
    try:
        _, qid, raw_idx = event.data.decode().split(":", 2)
        idx = int(raw_idx)
    except Exception:
        await event.answer("Invalid quiz", alert=True)
        raise events.StopPropagation
    row = await active_db.find_one({"quiz_id": qid})
    if not row:
        await event.answer("Quiz expired", alert=True)
        raise events.StopPropagation
    user_id = int(event.sender_id or 0)
    answered = [int(x) for x in row.get("answered", [])]
    if user_id in answered:
        await event.answer("One attempt only", alert=True)
        raise events.StopPropagation
    await active_db.update_one({"quiz_id": qid}, {"$addToSet": {"answered": user_id}})
    question = row["question"]
    if idx == int(question["answer"]):
        await wallet_db.update_one({"user_id": user_id}, {"$inc": {"balance": REWARD}, "$set": {"updated_at": int(time.time())}}, upsert=True)
        await event.answer(f"Correct! +{REWARD} EC", alert=True)
        await event.reply(font(f"Correct answer! +{REWARD} EC"))
    else:
        correct = question["options"][int(question["answer"])]
        await event.answer("Wrong answer", alert=True)
        await event.reply(font(f"Wrong answer. Correct: {correct}"))
    raise events.StopPropagation


async def anime_auto_loop():
    await asyncio.sleep(20)
    while True:
        try:
            rows = await chat_db.find({"enabled": True}).to_list(length=500)
            for row in rows:
                chat_id = int(row.get("chat_id"))
                try:
                    await send_quiz(chat_id)
                    await asyncio.sleep(2)
                except Exception:
                    pass
        except Exception:
            pass
        await asyncio.sleep(QUIZ_INTERVAL)


if "zzzzzzzzzzzzzzzzzzzz_azai_anime_quiz_auto" not in tbot.handlers_loaded:
    tbot.add_event_handler(register_chat, events.NewMessage(incoming=True))
    tbot.add_event_handler(animeguess, events.NewMessage(pattern=f"^{prefix_cmds}animeguess(?:@\\w+)?$", incoming=True))
    tbot.add_event_handler(animequiz_toggle, events.NewMessage(pattern=f"^{prefix_cmds}animequiz(?:@\\w+)?(?: .*)?$", incoming=True))
    tbot.add_event_handler(anime_answer, events.CallbackQuery(pattern=b"^azai_anime:"))
    try:
        asyncio.get_event_loop().create_task(anime_auto_loop())
    except RuntimeError:
        pass
    tbot.handlers_loaded.add("zzzzzzzzzzzzzzzzzzzz_azai_anime_quiz_auto")
