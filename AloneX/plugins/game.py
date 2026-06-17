import asyncio
from datetime import datetime, timedelta

from pyrogram import filters, types
from AloneX import pbot as bot

__module__ = "Mini Games"

__help__ = """
🎮 Mini Games Module

Commands:
/dice - Roll a dice
/dart - Play darts
/basketball - Shoot a basketball
/bowl - Bowling dice game
/slot - Spin slot machine

Note:
This module only plays Telegram mini-games.
EGO HUSTLE wallet stays separate: use /bal, /daily, /work, /luck, /raid, /heist.
"""

FLOOD_MAX = 2
GAME_USERS = {}

GAME_CONFIG = {
    "dice": ("🎲", "Dice Roll"),
    "dart": ("🎯", "Dart Throw"),
    "basketball": ("🏀", "Basketball Shot"),
    "bball": ("🏀", "Basketball Shot"),
    "bowl": ("🎳", "Bowling Roll"),
    "bowling": ("🎳", "Bowling Roll"),
    "slot": ("🎰", "Slot Machine"),
}


def _left(user_id: int, command: str) -> float:
    key = (int(user_id), command)
    until = GAME_USERS.get(key)
    if not until:
        return 0
    left = (until - datetime.now()).total_seconds()
    if left <= 0:
        GAME_USERS.pop(key, None)
        return 0
    return left


async def _remove_after(user_id: int, command: str):
    await asyncio.sleep(FLOOD_MAX * 60)
    GAME_USERS.pop((int(user_id), command), None)


def _result_line(command: str, value: int) -> str:
    if command in {"dice"}:
        return f"Result: {value}/6"
    if command in {"dart"}:
        return f"Score: {value}/6"
    if command in {"basketball", "bball"}:
        return f"Shot Score: {value}/5"
    if command in {"bowl", "bowling"}:
        return f"Pins Score: {value}/6"
    if command == "slot":
        return f"Slot Value: {value}"
    return f"Value: {value}"


async def _play_game(_, m: types.Message, command: str):
    user = m.from_user
    if not user:
        return

    wait = _left(user.id, command)
    if wait:
        return await m.reply_text(f"Cooldown active. Try again after {int(wait)} seconds.")

    emoji, title = GAME_CONFIG[command]
    GAME_USERS[(int(user.id), command)] = datetime.now() + timedelta(minutes=FLOOD_MAX)

    try:
        msg = await bot.send_dice(
            chat_id=m.chat.id,
            emoji=emoji,
            reply_parameters=types.ReplyParameters(message_id=m.id),
        )
    except TypeError:
        msg = await bot.send_dice(
            chat_id=m.chat.id,
            emoji=emoji,
            reply_to_message_id=m.id,
        )

    value = getattr(getattr(msg, "dice", None), "value", 0)
    player = user.first_name or user.username or "Player"

    await asyncio.sleep(2)
    await msg.reply_text(
        f"{title}\n"
        f"Player: {player}\n"
        f"{_result_line(command, value)}"
    )
    asyncio.create_task(_remove_after(user.id, command))


@bot.on_message(filters.command("dice") & ~filters.forwarded)
async def _dice(_, m: types.Message):
    await _play_game(_, m, "dice")


@bot.on_message(filters.command("dart") & ~filters.forwarded)
async def _dart(_, m: types.Message):
    await _play_game(_, m, "dart")


@bot.on_message(filters.command(["basketball", "bball"]) & ~filters.forwarded)
async def _basketball(_, m: types.Message):
    await _play_game(_, m, "basketball")


@bot.on_message(filters.command(["bowl", "bowling"]) & ~filters.forwarded)
async def _bowl(_, m: types.Message):
    await _play_game(_, m, "bowl")


@bot.on_message(filters.command("slot") & ~filters.forwarded)
async def _slot(_, m: types.Message):
    await _play_game(_, m, "slot")
