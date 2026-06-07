import random
from datetime import datetime

import pytz
from telethon import Button, events

from AloneX import database, font, prefix_cmds, tbot

IST = pytz.timezone("Asia/Kolkata")
AZAI_BOT_USERNAME = "Urxazaibot"
gate_db = database["azai_group_gate"]
active_gate = {}


def now_ist() -> str:
    return datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S")


def gate_key(chat_id: int, user_id: int) -> dict:
    return {"chat_id": chat_id, "user_id": user_id}


async def gate_done(chat_id: int, user_id: int) -> bool:
    data = await gate_db.find_one(gate_key(chat_id, user_id))
    return bool(data and data.get("done") is True)


async def mark_gate_pending(chat_id: int, user_id: int):
    await gate_db.update_one(
        gate_key(chat_id, user_id),
        {"$setOnInsert": {"chat_id": chat_id, "user_id": user_id, "done": False, "created_at": now_ist()}},
        upsert=True,
    )


async def mark_gate_done(chat_id: int, user_id: int):
    await gate_db.update_one(
        gate_key(chat_id, user_id),
        {"$set": {"done": True, "done_at": now_ist(), "updated_at": now_ist()}},
        upsert=True,
    )
