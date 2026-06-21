import re
from datetime import datetime

import pytz
from telethon import events

from AloneX import database, font, prefix_cmds, tbot
from config import ALONE_OWNER_ID, OWNER_ID

IST = pytz.timezone("Asia/Kolkata")
fun_db = database["azai_custom_fun_commands"]

CMD_RE = re.compile(r"^[a-zA-Z0-9_]{2,32}$")
RESERVED = {
    "start", "help", "owner", "settings", "msettings", "wallet", "balance", "bal",
    "daily", "work", "send", "leaderboard", "hustle", "raid", "attack", "luck",
    "heist", "protect", "shop", "inventory", "garage", "verify", "verifyall",
    "unverifyall", "ban", "mute", "kick", "purge", "logon", "logoff", "logstatus",
}

DEFAULT_FUN = {
    "huggy": "{user} sent a clean friendly hug to {target}. Keep it wholesome.",
    "pat": "{user} gave {target} a calm head pat. Soft scene, no drama.",
    "highfive": "{user} gave {target} a sharp high five. Energy restored.",
}


def now_ist() -> str:
    return datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S")


def owner_ids() -> set[int]:
    ids = set()
    for value in (ALONE_OWNER_ID, OWNER_ID):
        try:
            value = int(value)
            if value:
                ids.add(value)
        except Exception:
            pass
    return ids


async def is_owner(event) -> bool:
    sender = await event.get_sender()
    return bool(sender and int(sender.id) in owner_ids())


def clean_command(raw: str) -> str:
    cmd = (raw or "").strip().lower().lstrip("/!.?*#,$&\\")
    if "@" in cmd:
        cmd = cmd.split("@", 1)[0]
    return cmd


def user_name(user) -> str:
    if not user:
        return "Someone"
    name = getattr(user, "first_name", None) or getattr(user, "username", None) or "Someone"
    username = getattr(user, "username", None)
    return f"{name} (@{username})" if username else name


async def get_media(cmd: str):
    row = await fun_db.find_one({"cmd": cmd})
    if not row or not row.get("chat_id") or not row.get("msg_id"):
        return None
    try:
        msg = await tbot.get_messages(int(row["chat_id"]), ids=int(row["msg_id"]))
        if msg and msg.media:
            return msg.media
    except Exception:
        return None
    return None


async def add_fun_cmd(event):
    if not await is_owner(event):
        await event.reply(font("Owner only."))
        raise events.StopPropagation
    raw = event.raw_text or ""
    if "|" not in raw:
        await event.reply(font("Use: /addfuncmd command | response text"))
        raise events.StopPropagation
    left, response = raw.split("|", 1)
    parts = left.split(maxsplit=1)
    if len(parts) < 2:
        await event.reply(font("Use: /addfuncmd command | response text"))
        raise events.StopPropagation
    cmd = clean_command(parts[1])
    response = response.strip()
    if not CMD_RE.match(cmd):
        await event.reply(font("Command name must be 2-32 letters, numbers, or underscore."))
        raise events.StopPropagation
    if cmd in RESERVED:
        await event.reply(font("This command is reserved by AZAI core."))
        raise events.StopPropagation
    if not response:
        await event.reply(font("Response text cannot be empty."))
        raise events.StopPropagation
    await fun_db.update_one(
        {"cmd": cmd},
        {"$set": {"cmd": cmd, "text": response, "updated_at": now_ist()}},
        upsert=True,
    )
    await event.reply(font("Custom fun command saved:") + f" /{cmd}")
    raise events.StopPropagation


async def set_fun_media(event):
    if not await is_owner(event):
        await event.reply(font("Owner only."))
        raise events.StopPropagation
    parts = (event.raw_text or "").split(maxsplit=1)
    if len(parts) < 2:
        await event.reply(font("Use: /setfuncmdpic command by replying to media."))
        raise events.StopPropagation
    cmd = clean_command(parts[1])
    if not CMD_RE.match(cmd):
        await event.reply(font("Invalid command name."))
        raise events.StopPropagation
    reply = await event.get_reply_message()
    if not reply or not reply.media:
        await event.reply(font("Reply to image, gif, video, or sticker first."))
        raise events.StopPropagation
    existing = await fun_db.find_one({"cmd": cmd})
    if not existing and cmd not in DEFAULT_FUN:
        await event.reply(font("Add the command first with /addfuncmd, then set media."))
        raise events.StopPropagation
    await fun_db.update_one(
        {"cmd": cmd},
        {"$set": {"cmd": cmd, "chat_id": int(reply.chat_id), "msg_id": int(reply.id), "updated_at": now_ist()}},
        upsert=True,
    )
    await event.reply(font("Custom fun media saved:") + f" /{cmd}")
    raise events.StopPropagation


async def delete_fun_cmd(event):
    if not await is_owner(event):
        await event.reply(font("Owner only."))
        raise events.StopPropagation
    parts = (event.raw_text or "").split(maxsplit=1)
    if len(parts) < 2:
        await event.reply(font("Use: /delfuncmd command"))
        raise events.StopPropagation
    cmd = clean_command(parts[1])
    await fun_db.delete_one({"cmd": cmd})
    await event.reply(font("Custom fun command deleted:") + f" /{cmd}")
    raise events.StopPropagation


async def list_fun_cmds(event):
    rows = await fun_db.find({}).sort("cmd", 1).to_list(length=100)
    commands = sorted(set(DEFAULT_FUN) | {row.get("cmd") for row in rows if row.get("cmd")})
    text = font("CUSTOM FUN COMMANDS") + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    if not commands:
        text += font("No custom fun commands yet.")
    else:
        text += "\n".join(f"/{cmd}" for cmd in commands)
    text += "\n\n" + font("Owner setup:") + " /addfuncmd /setfuncmdpic /delfuncmd"
    await event.reply(text)
    raise events.StopPropagation


async def custom_fun_handler(event):
    if not event.raw_text:
        return
    raw_cmd = event.raw_text.split(maxsplit=1)[0]
    cmd = clean_command(raw_cmd)
    if not cmd or cmd in RESERVED:
        return
    row = await fun_db.find_one({"cmd": cmd})
    template = (row or {}).get("text") or DEFAULT_FUN.get(cmd)
    if not template:
        return
    sender = await event.get_sender()
    reply = await event.get_reply_message()
    target = await reply.get_sender() if reply else None
    text = template.format(user=user_name(sender), target=user_name(target))
    media = await get_media(cmd)
    if media:
        await tbot.send_file(event.chat_id, media, caption=font(text))
    else:
        await event.reply(font(text))
    raise events.StopPropagation


if "azai_custom_fun_media" not in tbot.handlers_loaded:
    tbot.add_event_handler(add_fun_cmd, events.NewMessage(pattern=f"^{prefix_cmds}addfuncmd(?: .*)?$", incoming=True))
    tbot.add_event_handler(set_fun_media, events.NewMessage(pattern=f"^{prefix_cmds}setfuncmdpic(?: .*)?$", incoming=True))
    tbot.add_event_handler(delete_fun_cmd, events.NewMessage(pattern=f"^{prefix_cmds}delfuncmd(?: .*)?$", incoming=True))
    tbot.add_event_handler(list_fun_cmds, events.NewMessage(pattern=f"^{prefix_cmds}(funcmds|funcommands)$", incoming=True))
    tbot.add_event_handler(custom_fun_handler, events.NewMessage(incoming=True))
    tbot.handlers_loaded.add("azai_custom_fun_media")
