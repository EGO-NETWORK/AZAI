import time

from telethon import Button, events

from AloneX import database, font, prefix_cmds, tbot
from config import ALONE_OWNER_ID, OWNER_ID

settings_db = database["azai_tone_guard_settings"]
triggers_db = database["azai_tone_guard_triggers"]
replies_db = database["azai_tone_guard_replies"]


def _safe_int(value):
    try:
        return int(value or 0)
    except Exception:
        return 0


def owner_ids():
    return {x for x in {_safe_int(ALONE_OWNER_ID), _safe_int(OWNER_ID)} if x}


async def owner_only(event):
    if int(event.sender_id or 0) not in owner_ids():
        await event.reply(font("Owner only."))
        raise events.StopPropagation


async def panel_text(chat_id):
    settings = await settings_db.find_one({"chat_id": int(chat_id)}) or {}
    enabled = bool(settings.get("enabled", True))
    triggers = await triggers_db.find({"chat_id": int(chat_id)}).to_list(length=100)
    replies = await replies_db.find({"chat_id": int(chat_id)}).to_list(length=50)
    return (
        font("AZAI TONEGUARD PANEL")
        + "\n━━━━━━━━━━━━━━━━━━━━\n"
        + f"Status: {'ON' if enabled else 'OFF'}\n"
        + f"Triggers: {len(triggers)}\n"
        + f"Replies: {len(replies)}\n\n"
        + "Commands:\n"
        + "/toneguard on | off\n"
        + "/toneadd <trigger>\n"
        + "/tonedel <trigger>\n"
        + "/tonelist\n"
        + "/tonereplyadd <reply>\n"
        + "/tonereplydel <number>\n"
        + "/tonereplylist"
    )


def panel_buttons(enabled=True):
    toggle = Button.inline(font("Turn OFF" if enabled else "Turn ON"), b"azai_tone_toggle")
    return [
        [toggle, Button.inline(font("Triggers"), b"azai_tone_list")],
        [Button.inline(font("Replies"), b"azai_tone_replies"), Button.inline(font("Close"), b"azai_tone_close")],
    ]


async def tonepanel_cmd(event):
    await owner_only(event)
    settings = await settings_db.find_one({"chat_id": int(event.chat_id)}) or {}
    enabled = bool(settings.get("enabled", True))
    await event.reply(await panel_text(event.chat_id), buttons=panel_buttons(enabled))
    raise events.StopPropagation


async def tonepanel_callback(event):
    if int(event.sender_id or 0) not in owner_ids():
        await event.answer("Owner only", alert=True)
        raise events.StopPropagation

    data = event.data or b""
    chat_id = int(event.chat_id)

    if data == b"azai_tone_close":
        await event.delete()
        raise events.StopPropagation

    if data == b"azai_tone_toggle":
        settings = await settings_db.find_one({"chat_id": chat_id}) or {}
        enabled = not bool(settings.get("enabled", True))
        await settings_db.update_one({"chat_id": chat_id}, {"$set": {"chat_id": chat_id, "enabled": enabled, "updated_at": int(time.time())}}, upsert=True)
        await event.edit(await panel_text(chat_id), buttons=panel_buttons(enabled))
        raise events.StopPropagation

    if data == b"azai_tone_list":
        triggers = await triggers_db.find({"chat_id": chat_id}).sort("created_at", 1).to_list(length=100)
        values = [row.get("trigger") for row in triggers if row.get("trigger")]
        text = font("ToneGuard Triggers") + "\n━━━━━━━━━━━━━━━━━━━━\n"
        text += "\n".join([f"• {x}" for x in values]) if values else "No custom trigger yet.\nUse /toneadd <trigger>"
        await event.edit(text, buttons=[[Button.inline(font("Back"), b"azai_tone_back")]])
        raise events.StopPropagation

    if data == b"azai_tone_replies":
        replies = await replies_db.find({"chat_id": chat_id}).sort("created_at", 1).to_list(length=50)
        values = [row.get("reply") for row in replies if row.get("reply")]
        text = font("Tone Replies") + "\n━━━━━━━━━━━━━━━━━━━━\n"
        text += "\n".join([f"{i}. {x}" for i, x in enumerate(values, 1)]) if values else "No custom reply yet.\nUse /tonereplyadd <reply>"
        await event.edit(text, buttons=[[Button.inline(font("Back"), b"azai_tone_back")]])
        raise events.StopPropagation

    if data == b"azai_tone_back":
        settings = await settings_db.find_one({"chat_id": chat_id}) or {}
        enabled = bool(settings.get("enabled", True))
        await event.edit(await panel_text(chat_id), buttons=panel_buttons(enabled))
        raise events.StopPropagation


if "zzzzzzzzzzzzzzzzzzzz_azai_tone_panel" not in tbot.handlers_loaded:
    tbot.add_event_handler(tonepanel_cmd, events.NewMessage(pattern=f"^{prefix_cmds}tonepanel(?:@\\w+)?$", incoming=True))
    tbot.add_event_handler(tonepanel_callback, events.CallbackQuery(pattern=b"^azai_tone_"))
    tbot.handlers_loaded.add("zzzzzzzzzzzzzzzzzzzz_azai_tone_panel")
