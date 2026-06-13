import asyncio
import time

from telethon import events

from AloneX import database, font, prefix_cmds, tbot
from config import ALONE_OWNER_ID, OWNER_ID

targets = database["azai_broadcast_targets"]


def owner_ids():
    ids = set()
    for value in (ALONE_OWNER_ID, OWNER_ID):
        try:
            value = int(value)
            if value:
                ids.add(value)
        except Exception:
            pass
    return ids


async def is_owner(event):
    sender = await event.get_sender()
    return bool(sender and int(sender.id) in owner_ids())


async def remember_target(event):
    if event.out or event.fwd_from:
        return

    sender = await event.get_sender()
    if not sender or getattr(sender, "bot", False):
        return

    if event.is_private:
        kind = "private"
    elif event.is_group:
        kind = "group"
    else:
        kind = "channel"

    await targets.update_one(
        {"chat_id": int(event.chat_id)},
        {
            "$set": {
                "chat_id": int(event.chat_id),
                "type": kind,
                "updated_at": int(time.time()),
            }
        },
        upsert=True,
    )


async def get_broadcast_content(event):
    reply = await event.get_reply_message()

    if reply:
        text = reply.message or ""
        media = reply.media
        return text, media

    raw = event.raw_text or ""
    parts = raw.split(maxsplit=1)

    if len(parts) < 2:
        return None, None

    return parts[1], None


async def send_exact(chat_id, text, media, pin=False):
    sent = await tbot.send_message(
        chat_id,
        text or None,
        file=media,
    )

    pin_ok = False
    dm_sent = False

    if pin:
        if int(chat_id) > 0:
            dm_sent = True
        else:
            try:
                await tbot.pin_message(chat_id, sent, notify=False)
                pin_ok = True
            except Exception:
                pin_ok = False

    return sent, pin_ok, dm_sent


async def run_broadcast(event, pin=False):
    if not await is_owner(event):
        await event.reply(font("Owner only."))
        raise events.StopPropagation

    text, media = await get_broadcast_content(event)

    if text is None and media is None:
        await event.reply(
            font("Use: /broadcast your message")
            + "\n"
            + font("Or reply to any message/media with /broadcast")
        )
        raise events.StopPropagation

    sent_count = 0
    failed_count = 0
    pinned_count = 0
    pin_failed_count = 0
    dm_count = 0

    async for item in targets.find({}):
        chat_id = int(item.get("chat_id", 0) or 0)
        if not chat_id:
            continue

        try:
            sent, pin_ok, dm_sent = await send_exact(
                chat_id,
                text,
                media,
                pin=pin,
            )

            sent_count += 1

            if pin:
                if pin_ok:
                    pinned_count += 1
                elif dm_sent:
                    dm_count += 1
                else:
                    pin_failed_count += 1

            await asyncio.sleep(0.35)

        except Exception:
            failed_count += 1

    if pin:
        await event.reply(
            font("Pinned broadcast done.")
            + f"\nSent: {sent_count}"
            + f"\nPinned: {pinned_count}"
            + f"\nPin Failed: {pin_failed_count}"
            + f"\nDM Sent: {dm_count}"
            + f"\nFailed Send: {failed_count}"
        )
    else:
        await event.reply(
            font("Broadcast done.")
            + f"\nSent: {sent_count}"
            + f"\nFailed: {failed_count}"
        )

    raise events.StopPropagation


async def broadcast_handler(event):
    await run_broadcast(event, pin=False)


async def broadcastpin_handler(event):
    await run_broadcast(event, pin=True)


async def broadcastchats_handler(event):
    if not await is_owner(event):
        await event.reply(font("Owner only."))
        raise events.StopPropagation

    total = await targets.count_documents({})
    groups = await targets.count_documents({"type": {"$in": ["group", "channel"]}})
    users = await targets.count_documents({"type": "private"})

    await event.reply(
        font("Broadcast targets")
        + f"\nTotal: {total}"
        + f"\nGroups: {groups}"
        + f"\nUsers: {users}"
    )

    raise events.StopPropagation


if "zzzz_azai_broadcast" not in tbot.handlers_loaded:
    tbot.add_event_handler(
        broadcast_handler,
        events.NewMessage(
            pattern=f"^{prefix_cmds}broadcast(?: .*)?$",
            incoming=True,
        ),
    )

    tbot.add_event_handler(
        broadcastpin_handler,
        events.NewMessage(
            pattern=f"^{prefix_cmds}broadcastpin(?: .*)?$",
            incoming=True,
        ),
    )

    tbot.add_event_handler(
        broadcastchats_handler,
        events.NewMessage(
            pattern=f"^{prefix_cmds}broadcastchats(?:@\\w+)?$",
            incoming=True,
        ),
    )

    tbot.add_event_handler(
        remember_target,
        events.NewMessage(incoming=True),
    )

    tbot.handlers_loaded.add("zzzz_azai_broadcast")