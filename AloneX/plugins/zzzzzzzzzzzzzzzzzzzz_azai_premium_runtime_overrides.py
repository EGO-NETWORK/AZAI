import random
import re

from telethon import Button, events

from AloneX import database, font, prefix_cmds, tbot
from config import OWNER_ID, BOT_USERNAME

try:
    from config import BHABHI_ID, ALIZA_ID
except Exception:
    BHABHI_ID = 0
    ALIZA_ID = 0

profile_db = database["azai_profile_modes"]

GAME_COMMANDS = {"dice", "dart", "basketball", "slot"}
GAME_USAGE_TEXT = font("GAMES COMMANDS") + "\n━━━━━━━━━━━━━━━━━━━━\n\n" + "\n".join([
    "🎲 /dice - Roll a 1-6 dice. Quick luck test.",
    "🎯 /dart - Throw a dart. Higher score means cleaner aim.",
    "🏀 /basketball - Take a basketball shot. Score out of 5.",
    "🎰 /slot - Spin the slot machine. Match symbols for luck.",
]) + "\n\n" + font("EGO HUSTLE COMMANDS") + "\n" + "\n".join([
    "💰 /bal - Check your EC wallet or another member's balance.",
    "🧰 /work - Earn EC by working. Cooldown based reward.",
    "⚔️ /raid - Attack an unprotected wallet for loot.",
    "🛡 /protect - Activate protection before raids.",
    "🍀 /luck - Try luck for EC, power, or shield.",
    "💣 /heist - High risk, high reward EC game.",
    "🏆 /leaderboard - See top members.",
    "👤 /profile - Show your game profile.",
])

BOY_NAMES = {"raj", "rahul", "aman", "rohit", "sahil", "arjun", "aryan", "vivek", "mohit", "mr", "ego"}
GIRL_NAMES = {"aliza", "ayesha", "priya", "neha", "anjali", "rani", "muskan", "isha", "sana", "fatima", "zoya"}
SOFT_WORDS = {"sad", "mood off", "tension", "akela", "overthinking", "broken"}
POSITIVE_WORDS = {"thanks", "thank", "mast", "nice", "good", "op", "smart"}
ROUGH_WORDS = {"gali", "rough", "bad", "bakwas", "faltu"}


def safe_int(value):
    try:
        return int(value)
    except Exception:
        return 0


def owner_ids():
    owner = safe_int(OWNER_ID)
    return {owner} if owner else set()


def bhabhi_ids():
    ids = {safe_int(BHABHI_ID), safe_int(ALIZA_ID)}
    return {x for x in ids if x}


def command_from(text):
    raw = (text or "").strip().split(maxsplit=1)[0].lower().replace("/", "")
    if "@" in raw:
        raw = raw.split("@", 1)[0]
    return re.sub(r"[^a-z0-9_]+", "", raw)


def first_name(user):
    name = getattr(user, "first_name", "") or ""
    username = getattr(user, "username", "") or ""
    clean = re.sub(r"[^a-zA-Z]+", " ", f"{name} {username}").lower().strip().split()
    return clean[0] if clean else ""


def guess_mode(user):
    key = first_name(user)
    if key in BOY_NAMES:
        return "male"
    if key in GIRL_NAMES:
        return "female"
    return "unknown"


async def stored_mode(user_id):
    row = await profile_db.find_one({"user_id": int(user_id)}) or {}
    return row.get("mode")


async def ask_profile_mode(event):
    buttons = [[
        Button.inline(font("Bhai Mode"), b"azai_profile_male"),
        Button.inline(font("Ma'am Mode"), b"azai_profile_female"),
    ], [
        Button.inline(font("Neutral"), b"azai_profile_neutral"),
        Button.inline(font("Skip"), b"azai_profile_skip"),
    ]]
    await event.reply(font("Naam clear nahi hai. Profile mode choose kar do, phir reply tone perfect rahega."), buttons=buttons)
    raise events.StopPropagation


async def save_profile_mode(event):
    sender = await event.get_sender()
    data = (event.data or b"").decode()
    mode = data.replace("azai_profile_", "")
    if mode == "skip":
        mode = "neutral"
    await profile_db.update_one({"user_id": int(sender.id)}, {"$set": {"user_id": int(sender.id), "mode": mode}}, upsert=True)
    label = {"male": "Bhai Mode", "female": "Ma'am Mode", "neutral": "Neutral"}.get(mode, "Neutral")
    await event.edit(font(f"Saved: {label}"))
    raise events.StopPropagation


def line_for_mode(text, user_id, mode):
    body = (text or "").strip()
    low = body.lower()
    is_short = len(body) <= 3 or low in {"hi", "hu", "hello", "hey", "yo", "j"}
    rough = any(x in low for x in ROUGH_WORDS) or len(body) > 0 and sum(ch in "!@#$%^&*" for ch in body) >= 3

    if int(user_id or 0) in owner_ids():
        if rough:
            return font("Control, Sir. Issue bolo, I will fix it.")
        if is_short:
            return font("Ready, Sir. Drop the task.")
        return font("Got it, Sir. I am on it.")

    if int(user_id or 0) in bhabhi_ids():
        if is_short:
            return font("Bhabhi Ji, I am here. Bataiye.")
        return font("Ma'am, noted. I will handle it cleanly.")

    if mode == "male":
        if rough:
            return font("Bhai, issue bol. Drama kam, fix zyada.")
        if is_short:
            return font("Yo bro, kya scene hai?")
        return font("Bhai, got it. Seedha point bhej.")

    if mode == "female":
        if rough:
            return font("Aap point batao, main calmly help karta hoon.")
        if is_short:
            return font("Hey, tell me. What do you need?")
        return font("Noted. I will keep it simple and clean.")

    if rough:
        return font("Point batao. Main help ke liye hoon, lecture ke liye nahi.")
    if is_short:
        return font("Yo, I am here. Kya scene hai?")
    return font("Got it. Short me clear karo, I will handle it.")


async def react_safe(event, emoji):
    try:
        await event.message.react(emoji)
    except Exception:
        pass


def reaction_for(text):
    low = (text or "").lower()
    if any(x in low for x in SOFT_WORDS):
        return "❤️"
    if any(x in low for x in POSITIVE_WORDS):
        return "🔥"
    if any(x in low for x in ROUGH_WORDS):
        return "😐"
    return None


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

    emoji = reaction_for(text)
    if emoji:
        await react_safe(event, emoji)

    private_chat = int(getattr(event, "chat_id", 0) or 0) > 0
    if not private_chat:
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

    sender = await event.get_sender()
    user_id = int(getattr(sender, "id", event.sender_id or 0) or 0)
    mode = await stored_mode(user_id)
    if not mode:
        guessed = guess_mode(sender)
        if guessed == "unknown" and user_id not in owner_ids() and user_id not in bhabhi_ids():
            await ask_profile_mode(event)
            return
        mode = guessed
    await event.reply(line_for_mode(text, user_id, mode))
    raise events.StopPropagation


remove_old_game_handlers()

if "zzzzzzzzzzzzzzzzzzzz_azai_premium_runtime_overrides" not in tbot.handlers_loaded:
    for command in GAME_COMMANDS:
        tbot.add_event_handler(premium_game_handler, events.NewMessage(pattern=f"^{prefix_cmds}{command}(?:@\\w+)?$", incoming=True))
    tbot.add_event_handler(premium_games_panel, events.CallbackQuery(pattern=b"^azai_help_games$"))
    tbot.add_event_handler(save_profile_mode, events.CallbackQuery(pattern=b"^azai_profile_"))
    tbot.add_event_handler(premium_short_ai, events.NewMessage(incoming=True))
    tbot.handlers_loaded.add("zzzzzzzzzzzzzzzzzzzz_azai_premium_runtime_overrides")
