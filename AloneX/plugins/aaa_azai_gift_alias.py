from telethon import events

from AloneX import font, tbot

ALIASES = {
    "teddy_bear": "teddy",
    "bear": "teddy",
    "surprise": "surprise_box",
    "surprisebox": "surprise_box",
    "box": "surprise_box",
    "note": "letter",
    "message": "letter",
}


async def gift_alias_help(event):
    raw = (event.raw_text or "").strip()
    parts = raw.split(maxsplit=1)
    if len(parts) < 2:
        return
    gift_name = parts[1].lower().strip().replace(" ", "_").replace("-", "_")
    if gift_name in ALIASES:
        await event.reply(font("Use this gift key:") + f" /gift {ALIASES[gift_name]}")
        raise events.StopPropagation


if "aaa_azai_gift_alias" not in tbot.handlers_loaded:
    tbot.add_event_handler(gift_alias_help, events.NewMessage(pattern=r"^[/!.]gift(?: .*)?$", incoming=True))
    tbot.handlers_loaded.add("aaa_azai_gift_alias")
