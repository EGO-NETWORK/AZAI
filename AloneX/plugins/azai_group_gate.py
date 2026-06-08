import random
import time
from datetime import datetime

import pytz
from telethon import Button, events

from AloneX import database, font, prefix_cmds, tbot

IST = pytz.timezone("Asia/Kolkata")
AZAI_BOT_USERNAME = "Urxazaibot"
gate_db = database["azai_group_gate"]
active_gate = {}
gate_notice_cd = {}


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
        + font("Powered By:") + " " + font("EGO Network - EST. 2026")
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


def allowed_gate_text(text: str) -> bool:
    text = (text or "").strip().lower()
    return any(text == f"{prefix}verify" for prefix in prefix_cmds)


async def is_admin_user(event) -> bool:
    try:
        sender = await event.get_sender()
        if getattr(sender, "bot", False):
            return True
        perms = await event.client.get_permissions(event.chat_id, sender.id)
        return bool(getattr(perms, "is_admin", False) or getattr(perms, "is_creator", False))
    except Exception:
        return False


async def require_admin(event) -> bool:
    if event.is_private:
        await event.reply(font("This command works only inside groups."))
        return False
    if event.is_channel and not event.is_group:
        return False
    if not await is_admin_user(event):
        await event.reply(font("Only group admins can use this command."))
        return False
    return True


async def verifyall_handler(event):
    if not await require_admin(event):
        return

    msg = await event.reply(font("Marking current group members as verified..."))
    total = 0
    skipped = 0
    try:
        async for user in event.client.iter_participants(event.chat_id):
            if getattr(user, "bot", False):
                skipped += 1
                continue
            await mark_gate_done(event.chat_id, user.id)
            total += 1
    except Exception:
        await msg.edit(font("Failed to verify all members. Make sure AZAI has proper group access."))
        return

    await msg.edit(
        font("❂ VERIFY ALL COMPLETE") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Verified Members:") + f" {total}\n"
        + font("Skipped Bots:") + f" {skipped}"
    )


async def unverifyall_handler(event):
    if not await require_admin(event):
        return

    result = await gate_db.update_many(
        {"chat_id": event.chat_id},
        {"$set": {"done": False, "updated_at": now_ist()}},
    )
    active_to_remove = [key for key in active_gate if key[0] == event.chat_id]
    for key in active_to_remove:
        active_gate.pop(key, None)

    await event.reply(
        font("❂ UNVERIFY ALL COMPLETE") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Known members marked unverified:") + f" {result.modified_count}\n"
        + font("Now users must send /verify before chatting.")
    )


async def verified_handler(event):
    if not await require_admin(event):
        return
    count = await gate_db.count_documents({"chat_id": event.chat_id, "done": True})
    await event.reply(
        font("❂ VERIFIED USERS") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Verified count:") + f" {count}"
    )


async def unverified_handler(event):
    if not await require_admin(event):
        return
    count = await gate_db.count_documents({"chat_id": event.chat_id, "done": False})
    await event.reply(
        font("❂ UNVERIFIED USERS") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Known unverified count:") + f" {count}\n"
        + font("Note: Users not seen by AZAI yet are also treated as unverified.")
    )


async def group_gate_guard(event):
    if event.is_private:
        return
    if event.is_channel and not event.is_group:
        return
    if not event.sender_id:
        return
    if await is_admin_user(event):
        return
    if await gate_done(event.chat_id, event.sender_id):
        return
    if allowed_gate_text(event.raw_text):
        await mark_gate_pending(event.chat_id, event.sender_id)
        return

    try:
        await event.delete()
    except Exception:
        pass

    cd_key = (event.chat_id, event.sender_id)
    now = time.time()
    if gate_notice_cd.get(cd_key, 0) > now:
        return
    gate_notice_cd[cd_key] = now + 25

    try:
        await event.respond(font("Verification required. Send /verify first."))
    except Exception:
        pass


if "azai_group_gate" not in tbot.handlers_loaded:
    tbot.add_event_handler(verify_handler, events.NewMessage(pattern=f"^{prefix_cmds}verify$", incoming=True))
    tbot.add_event_handler(verifyall_handler, events.NewMessage(pattern=f"^{prefix_cmds}verifyall$", incoming=True))
    tbot.add_event_handler(unverifyall_handler, events.NewMessage(pattern=f"^{prefix_cmds}unverifyall$", incoming=True))
    tbot.add_event_handler(verified_handler, events.NewMessage(pattern=f"^{prefix_cmds}verified$", incoming=True))
    tbot.add_event_handler(unverified_handler, events.NewMessage(pattern=f"^{prefix_cmds}unverified$", incoming=True))
    tbot.add_event_handler(gate_answer, events.CallbackQuery(pattern=b"azg|"))
    tbot.add_event_handler(group_gate_guard, events.NewMessage(incoming=True))
    tbot.handlers_loaded.add("azai_group_gate")
