import time

from telethon import events

from AloneX import font, prefix_cmds, tbot

COOLDOWN = 5
last_play = {}


def can_play(user_id):
    now = int(time.time())
    old = last_play.get(int(user_id), 0)
    if now - old < COOLDOWN:
        return False
    last_play[int(user_id)] = now
    return True


def score(user_id, max_value):
    base = int(time.time()) + int(user_id)
    return (base % max_value) + 1


async def play(event, title, emoji, max_value):
    sender = await event.get_sender()
    if sender and not can_play(sender.id):
        await event.reply(font("Try again in a few seconds."))
        raise events.StopPropagation
    value = score(sender.id if sender else 1, max_value)
    text = (
        font(title) + f" {emoji}\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        + font("Result:") + f" {value}/{max_value}"
    )
    await event.reply(text)
    raise events.StopPropagation


async def dice_handler(event):
    await play(event, "DICE ROLL", "🎲", 6)


async def dart_handler(event):
    await play(event, "DART THROW", "🎯", 6)


async def basketball_handler(event):
    await play(event, "BASKETBALL SHOT", "🏀", 5)


if "azai_games_basic" not in tbot.handlers_loaded:
    tbot.add_event_handler(dice_handler, events.NewMessage(pattern=f"^{prefix_cmds}dice(?:@\\w+)?$", incoming=True))
    tbot.add_event_handler(dart_handler, events.NewMessage(pattern=f"^{prefix_cmds}dart(?:@\\w+)?$", incoming=True))
    tbot.add_event_handler(basketball_handler, events.NewMessage(pattern=f"^{prefix_cmds}basketball(?:@\\w+)?$", incoming=True))
    tbot.handlers_loaded.add("azai_games_basic")
