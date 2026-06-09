import random
import string
from datetime import datetime

import pytz
from telethon import events

from AloneX import database, font, prefix_cmds, tbot

IST = pytz.timezone("Asia/Kolkata")
BRAND = font("EGO Network - EST. 2026")
CURRENCY = "EC"
REF_OWNER_REWARD = 100
REF_NEW_USER_REWARD = 50

wallet_db = database["azai_wallets"]
ref_db = database["azai_referrals"]


def now_ist() -> str:
    return datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S")


def make_code(user_id: int) -> str:
    base = "AZ" + str(user_id)[-4:]
    tail = "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(4))
    return f"{base}{tail}"


async def get_wallet(user_id: int) -> dict:
    user_id = int(user_id)
    data = await wallet_db.find_one({"user_id": user_id})
    if not data:
        data = {"user_id": user_id, "balance": 0, "xp": 0, "level": 1, "inventory": [], "created_at": now_ist()}
        await wallet_db.insert_one(data)
    return data


async def add_balance(user_id: int, amount: int):
    await get_wallet(user_id)
    await wallet_db.update_one(
        {"user_id": int(user_id)},
        {"$inc": {"balance": int(amount)}, "$set": {"updated_at": now_ist()}},
        upsert=True,
    )


async def get_or_create_ref_code(user_id: int) -> str:
    user_id = int(user_id)
    existing = await ref_db.find_one({"type": "code", "user_id": user_id})
    if existing and existing.get("code"):
        return existing["code"]
    code = make_code(user_id)
    while await ref_db.find_one({"type": "code", "code": code}):
        code = make_code(user_id)
    await ref_db.insert_one({"type": "code", "user_id": user_id, "code": code, "created_at": now_ist()})
    return code


async def refer_handler(event):
    sender = await event.get_sender()
    code = await get_or_create_ref_code(sender.id)
    text = (
        font("REFER EARN") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Your Code:") + f" `{code}`\n\n"
        + font("Reward:") + f" {REF_OWNER_REWARD} {CURRENCY} when a new user redeems it.\n"
        + font("New User Gets:") + f" {REF_NEW_USER_REWARD} {CURRENCY}\n\n"
        + font("Use:") + f" /redeemref {code}\n\n"
        + font("Powered By:") + " " + BRAND
    )
    await event.reply(text)


async def redeemref_handler(event):
    sender = await event.get_sender()
    parts = (event.raw_text or "").split()
    if len(parts) < 2:
        await event.reply(font("Use: /redeemref CODE"))
        return
    code = parts[1].strip().upper()
    code_doc = await ref_db.find_one({"type": "code", "code": code})
    if not code_doc:
        await event.reply(font("Invalid referral code."))
        return
    owner_id = int(code_doc.get("user_id", 0))
    if owner_id == int(sender.id):
        await event.reply(font("You cannot redeem your own referral code."))
        return
    old = await ref_db.find_one({"type": "redeem", "user_id": int(sender.id)})
    if old:
        await event.reply(font("You already redeemed a referral code."))
        return
    await ref_db.insert_one(
        {
            "type": "redeem",
            "user_id": int(sender.id),
            "code": code,
            "owner_id": owner_id,
            "created_at": now_ist(),
        }
    )
    await add_balance(owner_id, REF_OWNER_REWARD)
    await add_balance(sender.id, REF_NEW_USER_REWARD)
    await event.reply(
        font("REFERRAL REDEEMED") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("You received:") + f" {REF_NEW_USER_REWARD} {CURRENCY}\n"
        + font("Referrer received:") + f" {REF_OWNER_REWARD} {CURRENCY}"
    )


if "azai_refer" not in tbot.handlers_loaded:
    tbot.add_event_handler(refer_handler, events.NewMessage(pattern=f"^{prefix_cmds}refer$", incoming=True))
    tbot.add_event_handler(redeemref_handler, events.NewMessage(pattern=f"^{prefix_cmds}redeemref(?: .*)?$", incoming=True))
    tbot.handlers_loaded.add("azai_refer")
