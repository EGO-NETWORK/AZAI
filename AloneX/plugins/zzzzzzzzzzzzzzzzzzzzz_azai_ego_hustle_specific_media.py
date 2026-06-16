from telethon import events

from AloneX import font, prefix_cmds, tbot
import AloneX.plugins.zzzz_azai_ego_hustle_core as core


async def bal_media(event):
    reply = await event.get_reply_message()
    user = await reply.get_sender() if reply else await event.get_sender()
    data = await core.wallet(user.id, user)
    await core.send(event, "wallet", await core.bal_text(user, data), core.back())


async def daily_media(event):
    user = await event.get_sender()
    await core.send(event, "daily", await core.daily_result(user), core.back())


async def protect_media(event):
    user = await event.get_sender()
    parts = (event.raw_text or "").split(maxsplit=1)
    plan = parts[1].strip().lower() if len(parts) > 1 else ""
    if plan not in core.PROTECT:
        await event.reply(font("VAULT PROTECTION") + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n/protect 6h - 200 EC\n/protect 1d - 500 EC")
        raise events.StopPropagation
    seconds, price = core.PROTECT[plan]
    data = await core.wallet(user.id, user)
    if int(data.get("balance", 0)) < price:
        await event.reply(font("Not enough EC."))
        raise events.StopPropagation
    await core.wallet_db.update_one({"user_id": int(user.id)}, {"$inc": {"balance": -price}, "$set": {"game.protection_until": core.ts() + seconds, "updated_at": core.now_ist()}}, upsert=True)
    text = font("VAULT PROTECTION") + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" + f"{core.uname(user)} " + font("activated vault protection.") + f"\n\n{font('Duration:')} {plan}\n{font('Paid:')} {price} {core.CURRENCY}"
    await core.send(event, "protect", text, core.back())


if "zzzzzzzzzzzzzzzzzzzzz_azai_ego_hustle_specific_media" not in tbot.handlers_loaded:
    try:
        tbot.remove_event_handler(core.bal)
        tbot.remove_event_handler(core.daily)
        tbot.remove_event_handler(core.protect)
    except Exception:
        pass
    tbot.add_event_handler(bal_media, events.NewMessage(pattern=f"^{prefix_cmds}(bal|wallet|balance)(?:@\\w+)?$", incoming=True))
    tbot.add_event_handler(daily_media, events.NewMessage(pattern=f"^{prefix_cmds}daily(?:@\\w+)?$", incoming=True))
    tbot.add_event_handler(protect_media, events.NewMessage(pattern=f"^{prefix_cmds}protect(?:@\\w+)?(?: .*)?$", incoming=True))
    tbot.handlers_loaded.add("zzzzzzzzzzzzzzzzzzzzz_azai_ego_hustle_specific_media")
