import random
import time

from telethon import Button, events

from AloneX import font, prefix_cmds, tbot
import AloneX.plugins.zzzz_azai_ego_hustle_core as core

CURRENCY = core.CURRENCY
HEIST_ENTRY = 300
HEIST_COOLDOWN = 7200


def _left(seconds):
    return core.left_time(seconds)


def _back():
    return [[Button.inline(font("EGO Hustle"), b"egoh_home"), Button.inline(font("Close"), b"egoh_close")]]


def _action_buttons():
    return [
        [Button.inline(font("Wallet"), b"egoh_bal"), Button.inline(font("Daily"), b"egoh_daily")],
        [Button.inline(font("Work"), b"egoh_work"), Button.inline(font("Luck"), b"egoh_luck")],
        [Button.inline(font("Raid Help"), b"egoh2_raidhelp"), Button.inline(font("Heist"), b"egoh2_heist")],
        [Button.inline(font("Profile"), b"egoh_profile"), Button.inline(font("Leaderboard"), b"egoh_top")],
        [Button.inline(font("Close"), b"egoh_close")],
    ]


def _home_text():
    return (
        font("EGO HUSTLE")
        + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        + core.BRAND
        + "\n\n"
        + font("One Wallet. One Economy. One Rank.")
        + "\n\n"
        + font("Wallet:") + " /bal\n"
        + font("Earn:") + " /daily /work /luck\n"
        + font("Battle:") + " /raid /attack /protect\n"
        + font("High Risk:") + " /heist\n"
        + font("Rank:") + " /leaderboard /profile"
    )


# Patch core panel without touching the original core file.
core.buttons = _action_buttons
core.home_text = _home_text


async def _target_from_reply(event):
    reply = await event.get_reply_message()
    if not reply:
        await event.reply(font("Reply to a user first. Example: reply + /raid"))
        raise events.StopPropagation
    user = await reply.get_sender()
    if not user or getattr(user, "bot", False):
        await event.reply(font("Target valid user hona chahiye."))
        raise events.StopPropagation
    if int(user.id) == int(event.sender_id or 0):
        await event.reply(font("Khud pe raid? Bhai mirror game nahi chal raha."))
        raise events.StopPropagation
    return user


async def raid_attack_result(event, mode="raid"):
    attacker = await event.get_sender()
    target = await _target_from_reply(event)

    a = await core.wallet(attacker.id, attacker)
    t = await core.wallet(target.id, target)

    if int(t.get("balance", 0)) < 1000:
        return font("TARGET TOO LOW") + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" + f"{core.uname(target)} " + font("ke paas raid ke liye enough EC nahi hai.") + f"\n{font('Required:')} 1000 {CURRENCY}"

    protect_until = core.active_protect(t)
    if protect_until > core.ts():
        return font("TARGET PROTECTED") + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" + f"{core.uname(target)} " + font("vault shield me hai.") + f"\n{font('Protection left:')} {_left(protect_until - core.ts())}"

    ap = int(a.get("power", 100) or 100)
    tp = int(t.get("power", 100) or 100)
    chance = 50
    if ap > tp:
        chance = 90
    elif ap < tp:
        chance = 10

    success = random.randint(1, 100) <= chance
    if not success:
        await core.wallet_db.update_one({"user_id": int(attacker.id)}, {"$inc": {f"game.{mode}_losses": 1}, "$set": {"updated_at": core.now_ist()}}, upsert=True)
        return font(f"{mode.upper()} FAILED") + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" + f"{core.uname(attacker)} " + font("ne try kiya, par target strong nikla.") + f"\n{font('Chance:')} {chance}%"

    loot = min(800, max(1, int(int(t.get("balance", 0)) * 0.70)))
    await core.wallet_db.update_one({"user_id": int(attacker.id)}, {"$inc": {"balance": loot, f"game.{mode}_wins": 1}, "$set": {"updated_at": core.now_ist()}}, upsert=True)
    await core.wallet_db.update_one({"user_id": int(target.id)}, {"$inc": {"balance": -loot, f"game.{mode}_losses": 1}, "$set": {"updated_at": core.now_ist()}}, upsert=True)
    return font(f"{mode.upper()} SUCCESS") + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" + f"{core.uname(attacker)} " + font("ne clean hit maara.") + f"\n{font('Target:')} {core.uname(target)}\n{font('Loot:')} {loot} {CURRENCY}\n{font('Chance:')} {chance}%"


async def raid_cmd(event):
    await core.send(event, "raid", await raid_attack_result(event, "raid"), _back())


async def attack_cmd(event):
    await core.send(event, "attack", await raid_attack_result(event, "attack"), _back())


async def heist_result(user):
    data = await core.wallet(user.id, user)
    wait = core.cd(data, "heist_at", HEIST_COOLDOWN)
    if wait:
        return font("HEIST COOLDOWN") + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" + f"{font('Try again in:')} {_left(wait)}"
    if int(data.get("balance", 0)) < HEIST_ENTRY:
        return font("HEIST ENTRY LOW") + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" + f"{font('Required:')} {HEIST_ENTRY} {CURRENCY}"

    success = random.randint(1, 100) <= 45
    if success:
        reward = random.randint(1500, 5000)
        await core.wallet_db.update_one({"user_id": int(user.id)}, {"$inc": {"balance": reward, "game.heist_wins": 1}, "$set": {"game.heist_at": core.ts(), "updated_at": core.now_ist()}}, upsert=True)
        return font("HEIST SUCCESS") + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" + f"{core.uname(user)} " + font("ne risky move jeet liya.") + f"\n{font('Reward:')} {reward} {CURRENCY}"

    await core.wallet_db.update_one({"user_id": int(user.id)}, {"$inc": {"balance": -HEIST_ENTRY, "game.heist_losses": 1}, "$set": {"game.heist_at": core.ts(), "updated_at": core.now_ist()}}, upsert=True)
    return font("HEIST FAILED") + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" + f"{core.uname(user)} " + font("ka risky plan fail ho gaya.") + f"\n{font('Lost:')} {HEIST_ENTRY} {CURRENCY}"


async def heist_cmd(event):
    await core.send(event, "heist", await heist_result(await event.get_sender()), _back())


async def help_cb(event):
    data = event.data.decode()
    if data == "egoh2_raidhelp":
        text = font("RAID / ATTACK") + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" + font("Reply to a user:") + " /raid or /attack\n" + font("Target minimum:") + f" 1000 {CURRENCY}\n" + font("Loot:") + f" 70% max 800 {CURRENCY}\n" + font("Chance:") + " Equal 50% | Stronger 90% | Weaker 10%\n" + font("Protection blocks raid.")
        await event.edit(text, buttons=_back())
    elif data == "egoh2_heist":
        await event.edit(await heist_result(await event.get_sender()), buttons=_back())
    raise events.StopPropagation


if "zzzzzzzzzzzzzzzzzzzz_azai_ego_hustle_actions" not in tbot.handlers_loaded:
    tbot.add_event_handler(raid_cmd, events.NewMessage(pattern=f"^{prefix_cmds}raid(?:@\\w+)?$", incoming=True))
    tbot.add_event_handler(attack_cmd, events.NewMessage(pattern=f"^{prefix_cmds}attack(?:@\\w+)?$", incoming=True))
    tbot.add_event_handler(heist_cmd, events.NewMessage(pattern=f"^{prefix_cmds}heist(?:@\\w+)?$", incoming=True))
    tbot.add_event_handler(help_cb, events.CallbackQuery(pattern=b"^egoh2_"))
    tbot.handlers_loaded.add("zzzzzzzzzzzzzzzzzzzz_azai_ego_hustle_actions")
