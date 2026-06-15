import asyncio
import time

from telethon import events

from AloneX import database, font, prefix_cmds, tbot
from config import ALONE_OWNER_ID, OWNER_ID

targets = database["azai_broadcast_targets"]

USAGE = (
    font("AZAI Broadcast")
    + "\n━━━━━━━━━━━━━━━━━━━━\n"
    + "Use:\n"
    + "• /broadcast -all message\n"
    + "• /broadcast -users message\n"
    + "• /broadcast -groups message\n"
    + "• /broadcast -pin -all message\n"
    + "• /broadcast -pin -users message\n"
    + "• Reply media/message + /broadcast -all -pin\n\n"
    + "Flags:\n"
    + "-all = users + groups\n"
    + "-users = private users only\n"
    + "-groups = groups/channels only\n"
    + "-pin = pin in groups where possible"
)


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


def parse_flags_and_text(raw_text: str, default_pin: bool = False):
    parts = (raw_text or "").split(maxsplit=1)
    body = parts[1] if len(parts) > 1 else ""
    tokens = body.split()

    pin = bool(default_pin)
    mode = "all"
    message_tokens = []

    for token in tokens:
        low = token.lower().strip()
        if low in {"-pin", "pin", "--pin"}:
            pin = True
        elif low in {"-all", "all", "--all"}:
            mode = "all"
        elif low in {"-users", "-user", "users", "user", "-dm", "dm", "--users"}:
            mode = "users"
        elif low in {"-groups", "-group", "-chats", "-chat", "groups", "group", "chats", "chat", "--groups"}:
            mode = "groups"
        else:
            message_tokens.append(token)

    return mode, pin, " ".join(message_tokens).strip()


async def get_broadcast_content(event, default_pin=False):
    mode, pin, inline_text = parse_flags_and_text(event.raw_text or "", default_pin=default_pin)
    reply = await event.get_reply_message()

    if reply:
        text = inline_text or reply.message or ""
        media = reply.media
        return mode, pin, text, media

    if inline_text:
        return mode, pin, inline_text, None

    return mode, pin, None, None


def query_for_mode(mode):
    if mode == "users":
        return {"type": "private"}
    if mode == "groups":
        return {"type": {"$in": ["group", "channel"]}}
    return {}


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


async def run_broadcast(event, default_pin=False):
    if not await is_owner(event):
        await event.reply(font("Owner only."))
        raise events.StopPropagation

    mode, pin, text, media = await get_broadcast_content(event, default_pin=default_pin)

    if text is None and media is None:
        await event.reply(USAGE)
        raise events.StopPropagation

    sent_count = 0
    failed_count = 0
    pinned_count = 0
    pin_failed_count = 0
    dm_count = 0

    query = query_for_mode(mode)
    total = await targets.count_documents(query)

    if total <= 0:
        await event.reply(font("No broadcast targets found yet."))
        raise events.StopPropagation

    status = await event.reply(
        font("Broadcast started.")
        + f"\nMode: {mode}"
        + f"\nPin: {'yes' if pin else 'no'}"
        + f"\nTargets: {total}"
    )

    async for item in targets.find(query):
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

    result = (
        font("Broadcast finished.")
        + f"\nMode: {mode}"
        + f"\nSent: {sent_count}/{total}"
        + f"\nFailed: {failed_count}"
    )

    if pin:
        result += f"\nPinned: {pinned_count}\nPin Failed: {pin_failed_count}\nDM Sent: {dm_count}"

    try:
        await status.edit(result)
    except Exception:
        await event.reply(result)

    raise events.StopPropagation


async def broadcast_handler(event):
    await run_broadcast(event, default_pin=False)


async def broadcastpin_handler(event):
    await run_broadcast(event, default_pin=True)


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
        + "\n\n"
        + USAGE
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
