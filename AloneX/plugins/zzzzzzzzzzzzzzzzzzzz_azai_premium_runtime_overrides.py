import random
import re

from telethon import Button, events

from AloneX import font, prefix_cmds, tbot
from config import OWNER_ID, BOT_USERNAME

GAME_COMMANDS = {"dice", "dart", "basketball", "slot"}
GAME_USAGE_TEXT = font("GAMES COMMANDS") + "\n━━━━━━━━━━━━━━━━━━━━\n\n" + "\n".join([
    "🎲 /dice - Roll a 1-6 dice. Quick luck test.",
    "🎯 /dart - Throw a dart. Higher score means cleaner aim.",
    "🏀 /basketball - Take a basketball shot. Score out of 5.",
    "🎰 /slot - Spin the slot machine. Match symbols for luck.",
]) + "\n\n" + font("EGO HUSTLE") + "\n" + "\n".join([
    "💰 /bal - Check your EC wallet or another member's balance.",
    "🧰 /work - Earn EC by working. Cooldown based reward.",
    "🛡 /protect - Activate protection before raids.",
    "🍀 /luck - Try luck for EC, power, or shield.",
    "💣 /heist - High risk, high reward EC game.",
    "🏆 /leaderboard - See top members.",
    "👤 /profile - Show your game profile.",
])


def owner_ids():
    try:
        owner = int(OWNER_ID)
        return {owner} if owner else set()
    except Exception:
        return set()


def command_from(text):
    raw = (text or "").strip().split(maxsplit=1)[0].lower().replace("/", "")
    if "@" in raw:
        raw = raw.split("@", 1)[0]
    return re.sub(r"[^a-z0-9_]+", "", raw)


def short_ai_reply(text, user_id):
    body = (text or "").strip()
    low = body.lower()
    owner = int(user_id or 0) in owner_ids()

    if owner:
        if len(body) <= 3 or low in {"hi", "hu", "hello", "hey", "j"}:
            return font("MR EGO, bol. Kya kaam hai?")
        if any(x in low for x in ["gali", "rough", "bad", "bakwas"]):
            return font("Sir, tone rough hai. Point batao, main fix karta hoon.")
        return font("Sir, samjha. Seedha kaam batao, main handle karta hoon.")

    if len(body) <= 3 or low in {"hi", "hu", "hello", "hey"}:
        return font("Haan, bol. Kya chahiye?")
    return font("Samjha. Short me batao, main help karta hoon.")


def game_result(cmd):
    if cmd == "dice":
        score = random.randint(1, 6)
        return font("AZAI DICE ROLL 🎲") + f"\n━━━━━━━━━━━━━━━━━━━━\nResult: {score}/6"
    if cmd == "dart":
        score = random.randint(1, 6)
        return font("AZAI DART THROW 🎯") + f"\n━━━━━━━━━━━━━━━━━━━━\nResult: {score}/6"
    if cmd == "basketball":
        score = random.randint(1, 5)
        return font("AZAI BASKETBALL SHOT 🏀") + f"\n━━━━━━━━━━━━━━━━━━━━\nResult: {score}/5"
    symbols = ["🍒", "🍋", "⭐", "💎", "7️⃣"]
    roll = [random.choice(symbols) for _ in range(3)]
    matched = len(set(roll)) == 1
    result = "Jackpot" if matched else "Try again"
    return font("AZAI SLOT SPIN 🎰") + f"\n━━━━━━━━━━━━━━━━━━━━\n{' '.join(roll)}\nResult: {result}"


def remove_old_game_handlers():
    builders = getattr(tbot, "_event_builders", None)
    if not builders:
        return
    cleaned = []
    for item in builders:
        try:
            builder, callback = item
            raw = f"{getattr(builder, 'pattern', '')} {getattr(builder, '_pattern', '')} {getattr(callback, '__name__', '')} {getattr(callback, '__module__', '')}".lower()
            if any(cmd in raw for cmd in GAME_COMMANDS) or "azai_help_games" in raw:
                continue
        except Exception:
            pass
        cleaned.append(item)
    try:
        tbot._event_builders = cleaned
    except Exception:
        pass


async def premium_game_handler(event):
    cmd = command_from(event.raw_text)
    if cmd not in GAME_COMMANDS:
        return
    await event.reply(game_result(cmd))
    raise events.StopPropagation


async def premium_games_panel(event):
    await event.edit(GAME_USAGE_TEXT, buttons=[[Button.inline(font("Help Menu"), b"azai_start_help"), Button.inline(font("Close"), b"azai_close_panel")]])
    raise events.StopPropagation


async def premium_short_ai(event):
    text = (event.raw_text or "").strip()
    if not text or text[0] in prefix_cmds:
        return
    if int(getattr(event, "chat_id", 0) or 0) < 0:
        username = str(BOT_USERNAME or "").lower().replace("@", "")
        mentioned = username and (f"@{username}" in text.lower())
        replied = False
        try:
            reply = await event.get_reply_message()
            replied = bool(reply and getattr(reply.sender, "bot", False))
        except Exception:
            replied = False
        if not mentioned and not replied and int(event.sender_id or 0) not in owner_ids():
            return
    await event.reply(short_ai_reply(text, event.sender_id))
    raise events.StopPropagation


remove_old_game_handlers()

if "zzzzzzzzzzzzzzzzzzzz_azai_premium_runtime_overrides" not in tbot.handlers_loaded:
    for command in GAME_COMMANDS:
        tbot.add_event_handler(premium_game_handler, events.NewMessage(pattern=f"^{prefix_cmds}{command}(?:@\\w+)?$", incoming=True))
    tbot.add_event_handler(premium_games_panel, events.CallbackQuery(pattern=b"^azai_help_games$"))
    tbot.add_event_handler(premium_short_ai, events.NewMessage(incoming=True))
    tbot.handlers_loaded.add("zzzzzzzzzzzzzzzzzzzz_azai_premium_runtime_overrides")
