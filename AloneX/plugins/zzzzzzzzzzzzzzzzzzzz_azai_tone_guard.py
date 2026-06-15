import time
from datetime import datetime, timedelta

from telethon import events
from telethon.tl.types import ChatBannedRights

from AloneX import database, font, prefix_cmds, tbot
from config import ALONE_OWNER_ID, OWNER_ID

settings_db = database["azai_tone_guard_settings"]
triggers_db = database["azai_tone_guard_triggers"]
replies_db = database["azai_tone_guard_replies"]
warnings_db = database["azai_tone_guard_warnings"]

DEFAULT_TRIGGERS = ["gali", "bakwas", "faltu"]
DEFAULT_REPLIES = [
    "Warning {count}/3. Tone clean rakho, issue bolo.",
    "Bhai, warning {count}/3. Drama kam, kaam clear.",
    "Warning {count}/3. Repeat hua to silence mode.",
]


def _safe_int(value):
    try:
        return int(value or 0)
    except Exception:
        return 0


def owner_ids():
    return {x for x in {_safe_int(ALONE_OWNER_ID), _safe_int(OWNER_ID)} if x}


def cmd_name(text):
    raw = (text or "").strip().split(maxsplit=1)[0].lower().replace("/", "")
    if "@" in raw:
        raw = raw.split("@", 1)[0]
    return raw


def cmd_arg(text):
    parts = (text or "").strip().split(maxsplit=1)
    return parts[1].strip() if len(parts) > 1 else ""


async def is_enabled(chat_id):
    row = await settings_db.find_one({"chat_id": int(chat_id)}) or {}
    return bool(row.get("enabled", True))


async def get_triggers(chat_id):
    rows = await triggers_db.find({"chat_id": int(chat_id)}).to_list(length=200)
    values = [str(row.get("trigger", "")).lower().strip() for row in rows if row.get("trigger")]
    return values or DEFAULT_TRIGGERS


async def get_replies(chat_id):
    rows = await replies_db.find({"chat_id": int(chat_id)}).sort("created_at", 1).to_list(length=50)
    values = [str(row.get("reply", "")).strip() for row in rows if row.get("reply")]
    return values or DEFAULT_REPLIES


async def owner_only(event):
    if int(event.sender_id or 0) not in owner_ids():
        await event.reply(font("Owner only."))
        raise events.StopPropagation


async def toneguard_cmd(event):
    await owner_only(event)
    arg = cmd_arg(event.raw_text).lower()
    chat_id = int(event.chat_id)
    if arg in {"on", "enable"}:
        await settings_db.update_one({"chat_id": chat_id}, {"$set": {"chat_id": chat_id, "enabled": True}}, upsert=True)
        await event.reply(font("ToneGuard ON. Clean chat mode active."))
    elif arg in {"off", "disable"}:
        await settings_db.update_one({"chat_id": chat_id}, {"$set": {"chat_id": chat_id, "enabled": False}}, upsert=True)
        await event.reply(font("ToneGuard OFF. Main chup ho gaya, humans free disaster mode."))
    else:
        state = "ON" if await is_enabled(chat_id) else "OFF"
        await event.reply(font(f"ToneGuard: {state}\nUse: /toneguard on | off"))
    raise events.StopPropagation


async def toneadd_cmd(event):
    await owner_only(event)
    trigger = cmd_arg(event.raw_text).lower().strip()
    if not trigger:
        await event.reply(font("Use: /toneadd <trigger>"))
        raise events.StopPropagation
    await triggers_db.update_one({"chat_id": int(event.chat_id), "trigger": trigger}, {"$set": {"chat_id": int(event.chat_id), "trigger": trigger, "created_at": int(time.time())}}, upsert=True)
    await event.reply(font("Trigger added."))
    raise events.StopPropagation


async def tonedel_cmd(event):
    await owner_only(event)
    trigger = cmd_arg(event.raw_text).lower().strip()
    if not trigger:
        await event.reply(font("Use: /tonedel <trigger>"))
        raise events.StopPropagation
    await triggers_db.delete_one({"chat_id": int(event.chat_id), "trigger": trigger})
    await event.reply(font("Trigger removed."))
    raise events.StopPropagation


async def tonelist_cmd(event):
    await owner_only(event)
    triggers = await get_triggers(int(event.chat_id))
    text = font("ToneGuard Triggers") + "\n━━━━━━━━━━━━━━━━━━━━\n" + "\n".join([f"• {x}" for x in triggers])
    await event.reply(text)
    raise events.StopPropagation


async def tonereplyadd_cmd(event):
    await owner_only(event)
    reply = cmd_arg(event.raw_text).strip()
    if not reply:
        await event.reply(font("Use: /tonereplyadd <reply>"))
        raise events.StopPropagation
    await replies_db.insert_one({"chat_id": int(event.chat_id), "reply": reply, "created_at": int(time.time())})
    await event.reply(font("Tone reply added."))
    raise events.StopPropagation


async def tonereplylist_cmd(event):
    await owner_only(event)
    replies = await get_replies(int(event.chat_id))
    text = font("Tone Replies") + "\n━━━━━━━━━━━━━━━━━━━━\n" + "\n".join([f"{i}. {x}" for i, x in enumerate(replies, 1)])
    await event.reply(text)
    raise events.StopPropagation


async def tonereplydel_cmd(event):
    await owner_only(event)
    arg = cmd_arg(event.raw_text).strip()
    if not arg.isdigit():
        await event.reply(font("Use: /tonereplydel <number>"))
        raise events.StopPropagation
    index = int(arg) - 1
    rows = await replies_db.find({"chat_id": int(event.chat_id)}).sort("created_at", 1).to_list(length=50)
    if index < 0 or index >= len(rows):
        await event.reply(font("Invalid reply number."))
        raise events.StopPropagation
    await replies_db.delete_one({"_id": rows[index]["_id"]})
    await event.reply(font("Tone reply removed."))
    raise events.StopPropagation


async def tone_guard_listener(event):
    if event.is_private or event.fwd_from:
        return
    if not await is_enabled(int(event.chat_id)):
        return
    text = (event.raw_text or "").lower()
    if not text or text[0] in prefix_cmds:
        return
    triggers = await get_triggers(int(event.chat_id))
    if not any(trigger and trigger in text for trigger in triggers):
        return

    key = {"chat_id": int(event.chat_id), "user_id": int(event.sender_id or 0)}
    row = await warnings_db.find_one(key) or {}
    count = min(3, int(row.get("count", 0) or 0) + 1)
    await warnings_db.update_one(key, {"$set": {**key, "count": count, "updated_at": int(time.time())}}, upsert=True)

    try:
        await event.delete()
    except Exception:
        pass

    replies = await get_replies(int(event.chat_id))
    reply = replies[(count - 1) % len(replies)].replace("{count}", str(count))
    await tbot.send_message(event.chat_id, font(reply))

    if count >= 3:
        try:
            rights = ChatBannedRights(until_date=datetime.utcnow() + timedelta(minutes=10), send_messages=True)
            await tbot.edit_permissions(event.chat_id, int(event.sender_id), rights)
        except Exception:
            pass
    raise events.StopPropagation


if "zzzzzzzzzzzzzzzzzzzz_azai_tone_guard" not in tbot.handlers_loaded:
    tbot.add_event_handler(toneguard_cmd, events.NewMessage(pattern=f"^{prefix_cmds}toneguard(?:@\\w+)?(?: .*)?$", incoming=True))
    tbot.add_event_handler(toneadd_cmd, events.NewMessage(pattern=f"^{prefix_cmds}toneadd(?:@\\w+)?(?: .*)?$", incoming=True))
    tbot.add_event_handler(tonedel_cmd, events.NewMessage(pattern=f"^{prefix_cmds}tonedel(?:@\\w+)?(?: .*)?$", incoming=True))
    tbot.add_event_handler(tonelist_cmd, events.NewMessage(pattern=f"^{prefix_cmds}tonelist(?:@\\w+)?$", incoming=True))
    tbot.add_event_handler(tonereplyadd_cmd, events.NewMessage(pattern=f"^{prefix_cmds}tonereplyadd(?:@\\w+)?(?: .*)?$", incoming=True))
    tbot.add_event_handler(tonereplydel_cmd, events.NewMessage(pattern=f"^{prefix_cmds}tonereplydel(?:@\\w+)?(?: .*)?$", incoming=True))
    tbot.add_event_handler(tonereplylist_cmd, events.NewMessage(pattern=f"^{prefix_cmds}tonereplylist(?:@\\w+)?$", incoming=True))
    tbot.add_event_handler(tone_guard_listener, events.NewMessage(incoming=True))
    tbot.handlers_loaded.add("zzzzzzzzzzzzzzzzzzzz_azai_tone_guard")
