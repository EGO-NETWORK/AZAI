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

DISPLAY = {
    "rose": "Rose",
    "chocolate": "Chocolate",
    "ring": "Ring",
    "teddy": "Teddy Bear",
    "pizza": "Pizza",
    "surprise_box": "Surprise Box",
    "puppy": "Puppy",
    "cake": "Cake",
    "letter": "Letter",
    "cat": "Cat",
    "tulip": "Tulip",
}


def show(user):
    if not user:
        return "User"
    name = getattr(user, "first_name", None) or getattr(user, "username", None) or "User"
    username = getattr(user, "username", None)
    if username:
        return f"{name} (@{username})"
    return name


async def gift_alias_help(event):
    raw = (event.raw_text or "").strip()
    parts = raw.split(maxsplit=1)
    if len(parts) < 2:
        return
    item = parts[1].lower().strip().replace(" ", "_").replace("-", "_")
    item = ALIASES.get(item, item)
    if item not in DISPLAY:
        return
    reply = await event.get_reply_message()
    if not reply:
        return
    sender = await event.get_sender()
    target = await reply.get_sender()
    preview = f"🎁 {show(sender)} gifted {DISPLAY[item]} to {show(target)}\nPaid: EC will be handled by market system."
    await event.reply(font(preview), reply_to=reply.id)


if "aaa_azai_gift_alias" not in tbot.handlers_loaded:
    tbot.add_event_handler(gift_alias_help, events.NewMessage(pattern=r"^[/!.]gift(?: .*)?$", incoming=True))
    tbot.handlers_loaded.add("aaa_azai_gift_alias")
