from datetime import datetime

import pytz
from telethon import Button, events

from AloneX import database, font, prefix_cmds, tbot

IST = pytz.timezone("Asia/Kolkata")
BRAND = font("EGO Network - EST. 2026")
bond_db = database["azai_bond_tree"]
age_db = database["azai_age_gate"]
pending_bonds = {}

LABELS = {"prop": "Prime Bond", "weds": "Duo Bond"}


def now_ist() -> str:
    return datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S")


def clean_name(user) -> str:
    return getattr(user, "first_name", None) or getattr(user, "username", None) or "User"


def make_key(chat_id: int, from_id: int, to_id: int, kind: str) -> str:
    return f"{chat_id}:{from_id}:{to_id}:{kind}"


def pair(chat_id: int, user_a: int, user_b: int, kind: str) -> dict:
    a, b = sorted([int(user_a), int(user_b)])
    return {"chat_id": int(chat_id), "user_a": a, "user_b": b, "kind": kind}


async def is_age_allowed(user_id: int) -> bool:
    data = await age_db.find_one({"user_id": int(user_id), "allowed": True})
    return bool(data)


async def ageverify_handler(event):
    text = (
        font("AGE ACCESS CHECK") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("This command unlocks adult-only bond commands for your own account.") + "\n"
        + font("Please confirm only if you are 18 or older.") + "\n\n"
        + font("Are you 18+?")
    )
    buttons = [[Button.inline(font("Yes, I am 18+"), b"azage_yes"), Button.inline(font("No"), b"azage_no")]]
    await event.reply(text, buttons=buttons)


async def age_callback(event):
    sender = await event.get_sender()
    data = event.data.decode()
    if data == "azage_yes":
        await age_db.update_one(
            {"user_id": int(sender.id)},
            {"$set": {"user_id": int(sender.id), "allowed": True, "updated_at": now_ist()}},
            upsert=True,
        )
        await event.edit(font("18+ access enabled for your account."))
    elif data == "azage_no":
        await age_db.update_one(
            {"user_id": int(sender.id)},
            {"$set": {"user_id": int(sender.id), "allowed": False, "updated_at": now_ist()}},
            upsert=True,
        )
        await event.edit(font("Access locked. You cannot use adult-only bond commands."))


async def request_bond(event, kind: str):
    sender = await event.get_sender()
    if not await is_age_allowed(sender.id):
        await event.reply(
            font("AGE ACCESS REQUIRED") + "\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            + font("Please complete /ageverify first.")
        )
        return
    if event.is_private:
        await event.reply(font("Use this command inside a group by replying to a user."))
        return
    reply = await event.get_reply_message()
    if not reply:
        await event.reply(font("Reply to a user to send a bond request."))
        return
    target = await reply.get_sender()
    if not target or getattr(target, "bot", False):
        await event.reply(font("This target cannot be selected."))
        return
    if int(sender.id) == int(target.id):
        await event.reply(font("You cannot create this with yourself."))
        return
    if await bond_db.find_one(pair(event.chat_id, sender.id, target.id, kind)):
        await event.reply(font("This bond already exists."))
        return
    key = make_key(event.chat_id, sender.id, target.id, kind)
    pending_bonds[key] = {"chat_id": int(event.chat_id), "from_id": int(sender.id), "to_id": int(target.id), "kind": kind, "at": now_ist()}
    await event.reply(
        font("BOND REQUEST") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("From:") + f" {clean_name(sender)}\n"
        + font("To:") + f" {clean_name(target)}\n"
        + font("Type:") + f" {LABELS.get(kind, 'Bond')}\n\n"
        + font("This saves only after accept."),
        buttons=[[Button.inline(font("Accept"), f"azbond_ok|{key}".encode()), Button.inline(font("Reject"), f"azbond_no|{key}".encode())]],
    )


async def prop_handler(event):
    await request_bond(event, "prop")


async def weds_handler(event):
    await request_bond(event, "weds")


async def bond_callback(event):
    try:
        action, key = event.data.decode().split("|", 1)
    except Exception:
        await event.answer(font("Invalid request."), alert=True)
        return
    req = pending_bonds.get(key)
    if not req:
        await event.answer(font("Request expired."), alert=True)
        return
    sender = await event.get_sender()
    if int(sender.id) != int(req["to_id"]):
        await event.answer(font("Only the selected user can respond."), alert=True)
        return
    if action == "azbond_no":
        pending_bonds.pop(key, None)
        await event.edit(font("Bond request rejected."))
        return
    pending_bonds.pop(key, None)
    data = pair(req["chat_id"], req["from_id"], req["to_id"], req["kind"])
    data.update({"created_at": now_ist(), "updated_at": now_ist()})
    await bond_db.update_one(pair(req["chat_id"], req["from_id"], req["to_id"], req["kind"]), {"$set": data}, upsert=True)
    await event.edit(font("Bond request accepted."))


if "azai_bond_alias" not in tbot.handlers_loaded:
    tbot.add_event_handler(ageverify_handler, events.NewMessage(pattern=f"^{prefix_cmds}ageverify$", incoming=True))
    tbot.add_event_handler(prop_handler, events.NewMessage(pattern=f"^{prefix_cmds}prop$", incoming=True))
    tbot.add_event_handler(weds_handler, events.NewMessage(pattern=f"^{prefix_cmds}weds$", incoming=True))
    tbot.add_event_handler(age_callback, events.CallbackQuery(pattern=b"^azage_"))
    tbot.add_event_handler(bond_callback, events.CallbackQuery(pattern=b"^azbond_"))
    tbot.handlers_loaded.add("azai_bond_alias")
