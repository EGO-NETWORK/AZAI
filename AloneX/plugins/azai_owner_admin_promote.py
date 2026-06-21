import inspect
import os

from telethon import events, functions, types

from AloneX import font, tbot
import config


ADMIN_PATTERN = r"(?i)^(?:azai\s+admin|/azaiadmin|/makeadmin)(?:\s+(.+))?$"


def owner_ids() -> set[int]:
    ids = set()
    for key in ("ALONE_OWNER_ID", "OWNER_ID", "OWNER_IDS"):
        value = getattr(config, key, None) or os.getenv(key)
        for part in str(value or "").replace(",", " ").split():
            try:
                user_id = int(part)
                if user_id:
                    ids.add(user_id)
            except Exception:
                pass
    return ids


async def is_owner(event) -> bool:
    sender = await event.get_sender()
    return bool(sender and int(sender.id) in owner_ids())


def admin_rights():
    supported = set(inspect.signature(types.ChatAdminRights).parameters)
    requested = {
        "change_info": True,
        "post_messages": True,
        "edit_messages": True,
        "delete_messages": True,
        "ban_users": True,
        "invite_users": True,
        "pin_messages": True,
        "add_admins": True,
        "anonymous": False,
        "manage_call": True,
        "other": True,
        "manage_topics": True,
        "post_stories": True,
        "edit_stories": True,
        "delete_stories": True,
    }
    return types.ChatAdminRights(**{key: value for key, value in requested.items() if key in supported})


async def resolve_target(event, args: str | None):
    reply = await event.get_reply_message()
    if reply and getattr(reply, "sender_id", None):
        return await reply.get_sender()

    if args:
        raw = args.strip()
        if raw:
            return await tbot.get_entity(raw)

    return None


async def promote_user(chat, user, rank: str):
    try:
        input_chat = await tbot.get_input_entity(chat)
        input_user = await tbot.get_input_entity(user)
        await tbot(functions.channels.EditAdminRequest(input_chat, input_user, admin_rights(), rank))
        return True, None
    except Exception as channel_error:
        try:
            chat_id = getattr(chat, "id", None)
            user_id = getattr(user, "id", user)
            await tbot(functions.messages.EditChatAdminRequest(chat_id=chat_id, user_id=user_id, is_admin=True))
            return True, None
        except Exception:
            return False, str(channel_error)


def user_name(user) -> str:
    if not user:
        return "Unknown"
    username = getattr(user, "username", None)
    name = " ".join(x for x in [getattr(user, "first_name", None), getattr(user, "last_name", None)] if x).strip()
    base = name or str(getattr(user, "id", "Unknown"))
    return f"{base} (@{username})" if username else base


async def azai_admin_cmd(event):
    if not await is_owner(event):
        await event.reply(font("Owner only command."))
        raise events.StopPropagation

    if event.is_private:
        await event.reply(font("Use this command inside a group where AZAI is admin."))
        raise events.StopPropagation

    args = event.pattern_match.group(1) if event.pattern_match else None
    chat = await event.get_chat()
    sender = await event.get_sender()
    target = await resolve_target(event, args)

    users_to_promote = []
    if sender:
        users_to_promote.append((sender, "MR EGO"))
    if target and sender and int(getattr(target, "id", 0)) != int(getattr(sender, "id", 0)):
        users_to_promote.append((target, "AZAI Admin"))
    elif target and not sender:
        users_to_promote.append((target, "AZAI Admin"))

    if not users_to_promote:
        await event.reply(font("No valid user found to promote."))
        raise events.StopPropagation

    success = []
    failed = []
    for user, rank in users_to_promote:
        ok, error = await promote_user(chat, user, rank)
        if ok:
            success.append(user_name(user))
        else:
            failed.append(f"{user_name(user)}: {error or 'promotion failed'}")

    if success:
        text = font("AZAI ADMIN PROMOTION DONE") + "\n━━━━━━━━━━━━━━━━━━\n"
        text += font("Promoted:") + "\n" + "\n".join(f"• {name}" for name in success)
        if failed:
            text += "\n\n" + font("Failed:") + "\n" + "\n".join(f"• {item}" for item in failed)
        await event.reply(text)
    else:
        await event.reply(
            font("AZAI could not promote the user.")
            + "\n"
            + font("Make sure AZAI is admin with Add New Admins permission.")
        )

    raise events.StopPropagation


if "azai_owner_admin_promote" not in tbot.handlers_loaded:
    tbot.add_event_handler(azai_admin_cmd, events.NewMessage(pattern=ADMIN_PATTERN, incoming=True))
    tbot.handlers_loaded.add("azai_owner_admin_promote")
