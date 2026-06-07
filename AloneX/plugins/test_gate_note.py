import random
from datetime import datetime

import pytz
from telethon import Button, events

from AloneX import database, font, prefix_cmds, tbot

IST = pytz.timezone("Asia/Kolkata")
AZAI_BOT_USERNAME = "Urxazaibot"
gate_db = database["azai_group_gate"]
active_gate = {}


def now_ist() -> str:
    return datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S")


def gate_key(chat_id: int, user_id: int) -> dict:
    return {"chat_id": chat_id, "user_id": user_id}


async def gate_done(chat_id: int, user_id: int) -> bool:
    data = await gate_db.find_one(gate_key(chat_id, user_id))
    return bool(data and data.get("done") is True)


async def mark_gate_pending(chat_id: int, user_id: int):
    await gate_db.update_one(
        gate_key(chat_id, user_id),
        {"$setOnInsert": {"chat_id": chat_id, "user_id": user_id, "done": False, "created_at": now_ist()}},
        upsert=True,
    )


async def mark_gate_done(chat_id: int, user_id: int):
    await gate_db.update_one(
        gate_key(chat_id, user_id),
        {"$set": {"done": True, "done_at": now_ist(), "updated_at": now_ist()}},
        upsert=True,
    )


def setup_link() -> str:
    return f"https://t.me/{AZAI_BOT_USERNAME}?start=setup"


def gate_text(question: str) -> str:
    return (
        font("❂ AZAI GROUP GATE") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Only /verify is allowed before verification.") + "\n"
        + font("Solve this to unlock chat access in this group.") + "\n\n"
        + font("Question:") + f" {question}\n\n"
        + font("Powered By:") + " EGO Network - EST. 2026"
    )


def done_text() -> str:
    return (
        font("❂ VERIFICATION COMPLETE") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("You can now chat in this group.") + "\n"
        + font("Complete setup in DM for profile features.")
    )


def setup_button():
    return [[Button.url(font("Open Setup In DM"), setup_link())]]


def captcha_buttons(chat_id: int, user_id: int, answer: int):
    options = {answer}
    while len(options) < 4:
        options.add(random.randint(2, 18))
    options = list(options)
    random.shuffle(options)
    return [
        [Button.inline(str(options[0]), f"azg|{chat_id}|{user_id}|{options[0]}".encode()), Button.inline(str(options[1]), f"azg|{chat_id}|{user_id}|{options[1]}".encode())],
        [Button.inline(str(options[2]), f"azg|{chat_id}|{user_id}|{options[2]}".encode()), Button.inline(str(options[3]), f"azg|{chat_id}|{user_id}|{options[3]}".encode())],
    ]


async def send_gate(event):
    user = await event.get_sender()
    chat_id = event.chat_id
    user_id = user.id

    if await gate_done(chat_id, user_id):
        await event.reply(font("Your verification is already completed for this group."), buttons=setup_button())
        return

    await mark_gate_pending(chat_id, user_id)
    a = random.randint(2, 9)
    b = random.randint(2, 9)
    answer = a + b
    active_gate[(chat_id, user_id)] = answer
    await event.reply(gate_text(f"{a} + {b} = ?"), buttons=captcha_buttons(chat_id, user_id, answer))


async def verify_handler(event):
    if event.is_private:
        await event.reply(font("Use /verify inside your group."))
        return
    if event.is_channel and not event.is_group:
        return
    await send_gate(event)


async def gate_answer(event):
    try:
        _, chat_raw, user_raw, selected_raw = event.data.decode().split("|")
        chat_id = int(chat_raw)
        target_user = int(user_raw)
        selected = int(selected_raw)
    except Exception:
        await event.answer(font("Invalid verification."), alert=True)
        return

    sender = await event.get_sender()
    if sender.id != target_user:
        await event.answer(font("This verification is not for you."), alert=True)
        return

    answer = active_gate.get((chat_id, target_user))
    if answer is None:
        await event.answer(font("Expired. Send /verify again."), alert=True)
        return

    if selected != answer:
        await event.answer(font("Wrong answer."), alert=True)
        return

    active_gate.pop((chat_id, target_user), None)
    await mark_gate_done(chat_id, target_user)
    await event.edit(done_text(), buttons=setup_button())
    await event.answer(font("Verification completed."), alert=True)


if "azai_group_gate" not in tbot.handlers_loaded:
    tbot.add_event_handler(verify_handler, events.NewMessage(pattern=f"^{prefix_cmds}verify$", incoming=True))
    tbot.add_event_handler(gate_answer, events.CallbackQuery(pattern=b"azg|"))
    tbot.handlers_loaded.add("azai_group_gate")
