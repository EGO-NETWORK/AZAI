from telethon import events

from AloneX import font, tbot


async def tone_guard_status(event):
    await event.reply(font("AZAI tone guard placeholder active."))


if "azai_tone_guard" not in tbot.handlers_loaded:
    tbot.add_event_handler(tone_guard_status, events.NewMessage(pattern=r"^/toneguard$", incoming=True))
    tbot.handlers_loaded.add("azai_tone_guard")
