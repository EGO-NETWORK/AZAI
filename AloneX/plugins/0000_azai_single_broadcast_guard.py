import time

from telethon import events

from AloneX import database, font, prefix_cmds, tbot
from config import ALONE_OWNER_ID, OWNER_ID

broadcast_targets = database["azai_broadcast_targets"]
broadcast_locks = database["azai_broadcast_locks"]
users_col = database["users"]
chats_col = database["chats"]

LOCK_TTL = 45


def _safe_int(value):
    try:
        return int(value or 0)
    except Exception:
        return 0


def owner_ids():
    return {x for x in {_safe_int(ALONE_OWNER_ID), _safe_int(OWNER_ID)} if x}


async def owner_only(event):
    if int(event.sender_id or 0) not in owner_ids():
        await event.reply(font("Owner only."))
        raise events.StopPropagation


def parse_mode(text):
    low = (text or "").lower()
    target = "all"
    if " -users" in low:
        target = "users"
    elif " -groups" in low:
        target = "groups"
    pin = "-pin" in low or low.startswith("/broadcastpin") or low.startswith("!broadcastpin")
    return target, pin


def clean_message(text):
    parts = (text or "").split(maxsplit=1)
    if len(parts) < 2:
        return ""
    msg = parts[1]
    for token in ("-all", "-users", "-groups", "-pin"):
        msg = msg.replace(token, "")
    return msg.strip()


async def lock_once(event):
    key = f"{event.chat_id}:{event.id}:{event.raw_text}"
    old = await broadcast_locks.find_one({"key": key})
    now = int(time.time())
    if old and now - int(old.get("created_at", 0)) < LOCK_TTL:
        raise events.StopPropagation
    await broadcast_locks.update_one({"key": key}, {"$set": {"key": key, "created_at": now}}, upsert=True)


async def track_target(event):
    if not event.chat_id or not event.sender_id:
        return
    if event.is_private:
        kind = "user"
        target_id = int(event.chat_id)
    else:
        kind = "group"
        target_id = int(event.chat_id)
    await broadcast_targets.update_one(
        {"chat_id": target_id},
        {"$set": {"chat_id": target_id, "kind": kind, "last_seen": int(time.time())}},
        upsert=True,
    )


async def ids_from_collection(collection, kind):
    ids = set()
    try:
        rows = await collection.find({}).to_list(length=5000)
        for row in rows:
            for key in ("chat_id", "user_id", "id", "_id"):
                value = row.get(key)
                if isinstance(value, int) or (isinstance(value, str) and value.lstrip("-").isdigit()):
                    value = int(value)
                    if kind == "user" and value > 0:
                        ids.add(value)
                    elif kind == "group" and value < 0:
                        ids.add(value)
    except Exception:
        pass
    return ids


async def get_targets(target):
    user_ids, group_ids = set(), set()
    rows = await broadcast_targets.find({}).to_list(length=5000)
    for row in rows:
        cid = int(row.get("chat_id"))
        if row.get("kind") == "user" or cid > 0:
            user_ids.add(cid)
        else:
            group_ids.add(cid)
    user_ids |= await ids_from_collection(users_col, "user")
    group_ids |= await ids_from_collection(chats_col, "group")
    if target == "users":
        return sorted(user_ids)
    if target == "groups":
        return sorted(group_ids)
    return sorted(user_ids | group_ids)


async def send_one(chat_id, text, media, pin=False):
    sent = None
    if media:
        sent = await tbot.send_file(chat_id, media, caption=text or None)
    else:
        sent = await tbot.send_message(chat_id, text)
    if pin and sent:
        try:
            await tbot.pin_message(chat_id, sent, notify=False)
        except Exception:
            pass


async def broadcastchats(event):
    await owner_only(event)
    users = await get_targets("users")
    groups = await get_targets("groups")
    await event.reply(font("BROADCAST TARGETS") + f"\nUsers: {len(users)}\nGroups: {len(groups)}\nTotal: {len(set(users) | set(groups))}")
    raise events.StopPropagation


async def broadcast_cmd(event):
    await owner_only(event)
    await lock_once(event)
    await track_target(event)

    target, pin = parse_mode(event.raw_text)
    reply = await event.get_reply_message()
    media = reply.media if reply and reply.media else None
    text = clean_message(event.raw_text)
    if reply and not media and not text:
        text = reply.raw_text or ""

    if not text and not media:
        await event.reply(font("Use: /broadcast -all <message> or reply media + /broadcast -all"))
        raise events.StopPropagation

    targets = await get_targets(target)
    if not targets:
        await event.reply(font("No broadcast targets found yet."))
        raise events.StopPropagation

    ok = 0
    fail = 0
    started = await event.reply(font("Broadcast started...") + f"\nTarget: {target}\nCount: {len(targets)}")
    for chat_id in targets:
        try:
            await send_one(chat_id, text, media, pin)
            ok += 1
        except Exception:
            fail += 1
        await __import__("asyncio").sleep(0.08)

    await started.edit(font("Broadcast completed.") + f"\nSent: {ok}\nFailed: {fail}\nPinned: {'Yes' if pin else 'No'}")
    raise events.StopPropagation


if "0000_azai_single_broadcast_guard" not in tbot.handlers_loaded:
    # Prevent later duplicate broadcast plugin registrations where they respect handlers_loaded.
    tbot.handlers_loaded.add("zzzz_azai_broadcast")
    tbot.handlers_loaded.add("broadcast")
    tbot.add_event_handler(track_target, events.NewMessage(incoming=True))
    tbot.add_event_handler(broadcastchats, events.NewMessage(pattern=f"^{prefix_cmds}broadcastchats(?:@\\w+)?$", incoming=True))
    tbot.add_event_handler(broadcast_cmd, events.NewMessage(pattern=f"^{prefix_cmds}(broadcast|broadcastpin)(?:@\\w+)?(?: .*)?$", incoming=True))
    tbot.handlers_loaded.add("0000_azai_single_broadcast_guard")
