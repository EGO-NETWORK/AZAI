from telethon import events

from AloneX import font, tbot


TONE_TEXT = (
    font("AZAI TONE GUARD") + "\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    + font("Status:") + " " + font("Ready") + "\n"
    + font("Mode:") + " " + font("Clean premium replies only") + "\n"
    + font("Style:") + " " + font("Bhai vibe, respectful vibe, owner priority") + "\n\n"
    + font("Powered By:") + " " + font("EGO Network - EST. 2026")
)


async def tone_guard_status(event):
    await event.reply(TONE_TEXT)


if "azai_tone_guard" not in tbot.handlers_loaded:
    tbot.add_event_handler(tone_guard_status, events.NewMessage(pattern=r"^/toneguard$", incoming=True))
    tbot.handlers_loaded.add("azai_tone_guard")
