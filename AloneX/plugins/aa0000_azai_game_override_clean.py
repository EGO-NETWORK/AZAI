import random

from telethon import events

from AloneX import font, prefix_cmds, tbot

GAME_INFO = {
    "dice": ("DICE ROLL", "🎲", 6, "Roll a dice and get a score."),
    "dart": ("DART THROW", "🎯", 6, "Throw a dart and check your aim."),
    "basketball": ("BASKETBALL SHOT", "🏀", 5, "Take a shot and check your score."),
}
SPIN_ITEMS = ["🍒", "🍋", "🔔", "⭐", "💎"]


def clean_cmd(text: str):
    text = (text or "").strip().split()[0].lower().replace("/", "")
    if "@" in text:
        text = text.split("@", 1)[0]
    return text


async def game_override(event):
    text = (event.raw_text or "").strip()
    if not text or text[0] not in prefix_cmds:
        return
    cmd = clean_cmd(text)
    if cmd == "slot":
        result = [random.choice(SPIN_ITEMS) for _ in range(3)]
        body = (
            font("AZAI GAME")
            + "\n━━━━━━━━━━━━━━━━━━━━\n"
            + font("SYMBOL SPIN")
            + " 🎰\nResult: "
            + " ".join(result)
            + "\n\n"
            + font("Use: /slot - spin symbols for fun.")
        )
        await event.reply(body)
        raise events.StopPropagation
    if cmd not in GAME_INFO:
        return
    title, icon, max_score, use = GAME_INFO[cmd]
    score = random.randint(1, max_score)
    body = (
        font("AZAI GAME")
        + "\n━━━━━━━━━━━━━━━━━━━━\n"
        + font(title)
        + f" {icon}\nResult: {score}/{max_score}\n\n"
        + font(f"Use: /{cmd} - {use}")
    )
    await event.reply(body)
    raise events.StopPropagation


if "aa0000_azai_game_override_clean" not in tbot.handlers_loaded:
    tbot.add_event_handler(game_override, events.NewMessage(pattern=f"^{prefix_cmds}(dice|dart|basketball|slot)(?:@\\w+)?$", incoming=True))
    tbot.handlers_loaded.add("aa0000_azai_game_override_clean")
