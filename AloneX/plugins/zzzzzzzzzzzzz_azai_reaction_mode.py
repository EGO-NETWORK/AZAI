from telethon import events

from AloneX import prefix_cmds, tbot

POSITIVE = ("thanks", "thank", "mast", "nice", "good", "smart", "op")
SOFT = ("mood off", "tension", "akela", "overthinking")
FIRM = ("bakwas", "faltu", "bad")


async def react(event, emoji):
    try:
        await event.message.react(emoji)
    except Exception:
        pass


async def azai_reaction_mode(event):
    text = (event.raw_text or "").lower().strip()
    if not text or text.startswith(tuple(prefix_cmds)):
        return
    if any(word in text for word in SOFT):
        await react(event, "❤️")
    elif any(word in text for word in POSITIVE):
        await react(event, "🔥")
    elif any(word in text for word in FIRM):
        await react(event, "😐")


if "zzzzzzzzzzzzz_azai_reaction_mode" not in tbot.handlers_loaded:
    tbot.add_event_handler(azai_reaction_mode, events.NewMessage(incoming=True))
    tbot.handlers_loaded.add("zzzzzzzzzzzzz_azai_reaction_mode")
