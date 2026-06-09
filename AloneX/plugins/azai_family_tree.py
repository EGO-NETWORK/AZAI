from datetime import datetime

import pytz
from telethon import Button, events

from AloneX import database, font, prefix_cmds, tbot

IST = pytz.timezone("Asia/Kolkata")
BRAND = font("EGO Network - EST. 2026")
family_db = database["azai_family_tree"]
pending_family = {}

LINK_LABELS = {
    "brother": "Brother Link",
    "sister": "Sister Link",
    "adopt": "Adopted Member Link",
}


def now_ist() -> str:
    return datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S")


def clean_name(user) -> str:
    return getattr(user, "first_name", None) or getattr(user, "username", None) or "User"


def make_key(chat_id: int, from_id: int, to_id: int, link_type: str) -> str:
    return f"{chat_id}:{from_id}:{to_id}:{link_type}"


def pair_query(chat_id: int, user_a: int, user_b: int, link_type: str) -> dict:
    a, b = sorted([int(user_a), int(user_b)])
    return {"chat_id": int(chat_id), "user_a": a, "user_b": b, "link_type": link_type}


async def existing_link(chat_id: int, user_a: int, user_b: int, link_type: str):
    return await family_db.find_one(pair_query(chat_id, user_a, user_b, link_type))


async def save_link(chat_id: int, user_a: int, user_b: int, link_type: str):
    data = pair_query(chat_id, user_a, user_b, link_type)
    data.update({"created_at": now_ist(), "updated_at": now_ist()})
    await family_db.update_one(pair_query(chat_id, user_a, user_b, link_type), {"$set": data}, upsert=True)


async def remove_links(chat_id: int, user_id: int) -> int:
    result = await family_db.delete_many({"chat_id": int(chat_id), "$or": [{"user_a": int(user_id)}, {"user_b": int(user_id)}]})
    return int(result.deleted_count)


def request_text(from_user, to_user, link_type: str) -> str:
    label = LINK_LABELS.get(link_type, "Family Link")
    return (
        font("FAMILY TREE REQUEST") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("From:") + f" {clean_name(from_user)}\n"
        + font("To:") + f" {clean_name(to_user)}\n"
        + font("Type:") + f" {label}\n\n"
        + font("This will be saved only after the selected user accepts.") + "\n\n"
        + font("Powered By:") + " " + BRAND
    )


def request_buttons(key: str):
    return [[Button.inline(font("Accept"), f"azfam_accept|{key}".encode()), Button.inline(font("Reject"), f"azfam_reject|{key}".encode())]]


async def link_request(event, link_type: str):
    if event.is_private:
        await event.reply(font("Use this command inside a group by replying to a user."))
        return
    reply = await event.get_reply_message()
    if not reply:
        await event.reply(font("Reply to a user to send a Family Tree request."))
        return
    from_user = await event.get_sender()
    to_user = await reply.get_sender()
    if not to_user or getattr(to_user, "bot", False):
        await event.reply(font("This target cannot be selected."))
        return
    if int(from_user.id) == int(to_user.id):
        await event.reply(font("You cannot create a link with yourself."))
        return
    if await existing_link(event.chat_id, from_user.id, to_user.id, link_type):
        await event.reply(font("This family link already exists."))
        return
    key = make_key(event.chat_id, from_user.id, to_user.id, link_type)
    pending_family[key] = {"chat_id": int(event.chat_id), "from_id": int(from_user.id), "to_id": int(to_user.id), "link_type": link_type, "created_at": now_ist()}
    await event.reply(request_text(from_user, to_user, link_type), buttons=request_buttons(key))


async def brother_handler(event):
    await link_request(event, "brother")


async def sister_handler(event):
    await link_request(event, "sister")


async def adopt_handler(event):
    await link_request(event, "adopt")


async def family_handler(event):
    if event.is_private:
        await event.reply(font("Use /family inside a group."))
        return
    sender = await event.get_sender()
    rows = family_db.find({"chat_id": int(event.chat_id), "$or": [{"user_a": int(sender.id)}, {"user_b": int(sender.id)}]})
    text = font("FAMILY TREE") + "\n" + "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    count = 0
    async for row in rows:
        other = row["user_b"] if int(row.get("user_a")) == int(sender.id) else row["user_a"]
        label = LINK_LABELS.get(row.get("link_type"), "Family Link")
        text += f"• {label}: {other}\n"
        count += 1
    if count == 0:
        text += font("No family links yet.")
    text += "\n\n" + font("Powered By:") + " " + BRAND
    await event.reply(text)


async def leavefamily_handler(event):
    if event.is_private:
        await event.reply(font("Use /leavefamily inside a group."))
        return
    sender = await event.get_sender()
    removed = await remove_links(event.chat_id, sender.id)
    await event.reply(font("Family links removed:") + f" {removed}")


async def family_callback(event):
    try:
        raw = event.data.decode()
        action, key = raw.split("|", 1)
    except Exception:
        await event.answer(font("Invalid request."), alert=True)
        return
    req = pending_family.get(key)
    if not req:
        await event.answer(font("Request expired."), alert=True)
        return
    sender = await event.get_sender()
    if int(sender.id) != int(req["to_id"]):
        await event.answer(font("Only the selected user can respond."), alert=True)
        return
    if action == "azfam_reject":
        pending_family.pop(key, None)
        await event.edit(font("Family Tree request rejected."))
        return
    if action == "azfam_accept":
        pending_family.pop(key, None)
        await save_link(req["chat_id"], req["from_id"], req["to_id"], req["link_type"])
        label = LINK_LABELS.get(req["link_type"], "Family Link")
        await event.edit(
            font("FAMILY TREE UPDATED") + "\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            + font("Type:") + f" {label}\n"
            + font("Status:") + " Accepted"
        )


if "azai_family_tree" not in tbot.handlers_loaded:
    tbot.add_event_handler(brother_handler, events.NewMessage(pattern=f"^{prefix_cmds}brother$", incoming=True))
    tbot.add_event_handler(sister_handler, events.NewMessage(pattern=f"^{prefix_cmds}sister$", incoming=True))
    tbot.add_event_handler(adopt_handler, events.NewMessage(pattern=f"^{prefix_cmds}adopt$", incoming=True))
    tbot.add_event_handler(family_handler, events.NewMessage(pattern=f"^{prefix_cmds}family$", incoming=True))
    tbot.add_event_handler(leavefamily_handler, events.NewMessage(pattern=f"^{prefix_cmds}leavefamily$", incoming=True))
    tbot.add_event_handler(family_callback, events.CallbackQuery(pattern=b"^azfam_"))
    tbot.handlers_loaded.add("azai_family_tree")
