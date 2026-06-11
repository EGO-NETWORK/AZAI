from telethon import events

from AloneX import database, font, prefix_cmds, tbot
from config import ALONE_OWNER_ID, OWNER_ID

OWNER_LABEL = "MR EGO"
OWNER_LINK = "@EGOISTICxPRIME"
ALIZA_ID = 8899742834

identity_db = database["azai_identity_cache"]


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


def role_for(user_id: int) -> str:
    user_id = int(user_id)
    if user_id in owner_ids():
        return "owner"
    if user_id == int(ALIZA_ID):
        return "bhabhi"
    return "user"


def display_for(user_id: int, fallback: str = "User") -> str:
    role = role_for(user_id)
    if role == "owner":
        return OWNER_LABEL
    if role == "bhabhi":
        return "Bhabhi Ji"
    return fallback or "User"


async def cache_identity(user):
    if not user:
        return
    role = role_for(user.id)
    name = getattr(user, "first_name", None) or getattr(user, "username", None) or "User"
    username = getattr(user, "username", None)
    await identity_db.update_one(
        {"user_id": int(user.id)},
        {"$set": {"user_id": int(user.id), "role": role, "name": name, "username": username}},
        upsert=True,
    )


async def whoami_handler(event):
    sender = await event.get_sender()
    await cache_identity(sender)
    role = role_for(sender.id)
    if role == "owner":
        text = font("Identity:") + f" {OWNER_LABEL}\n" + font("Master:") + f" {OWNER_LINK}"
    elif role == "bhabhi":
        text = font("Identity:") + " Bhabhi Ji\n" + font("Respect Level:") + " High"
    else:
        text = font("Identity:") + f" {getattr(sender, 'first_name', 'User')}"
    await event.reply(text)


async def identity_passive(event):
    if event.fwd_from:
        return
    sender = await event.get_sender()
    if sender and not getattr(sender, "bot", False):
        await cache_identity(sender)


if "aaa_azai_identity" not in tbot.handlers_loaded:
    tbot.add_event_handler(whoami_handler, events.NewMessage(pattern=f"^{prefix_cmds}whoami(?:@\\w+)?$", incoming=True))
    tbot.add_event_handler(identity_passive, events.NewMessage(incoming=True))
    tbot.handlers_loaded.add("aaa_azai_identity")
