import re
import time

from telethon import Button, events

from AloneX import database, font, prefix_cmds, tbot
from config import ALONE_OWNER_ID, OWNER_ID
from AloneX.plugins import aaa_azai_start_pic as start_panel
try:
    from AloneX.plugins import azai_owner_panel as owner_panel
except Exception:
    owner_panel = None

fun_db = database["azai_fun_zone"]
RESERVED = {"start", "help", "ping", "alive", "repo", "owner", "settings", "shop", "gift", "wallet", "daily", "send", "leaderboard", "inventory", "garage", "animeguess", "quiz", "quizstats", "quiztop", "addfun", "delfun", "funlist"}


def owner_ids():
    ids = set()
    for value in (ALONE_OWNER_ID, OWNER_ID):
        try:
            if int(value):
                ids.add(int(value))
        except Exception:
            pass
    return ids


async def is_owner(event):
    sender = await event.get_sender()
    return bool(sender and int(sender.id) in owner_ids())


def word(value):
    value = str(value or "").strip().lower().replace("/", "")
    value = re.sub(r"[^a-z0-9_]+", "", value)
    if not value or value in RESERVED or len(value) > 24:
        return None
    return value


def name(user):
    if not user:
        return font("Member")
    full = " ".join(x for x in [getattr(user, "first_name", None), getattr(user, "last_name", None)] if x).strip()
    username = getattr(user, "username", None)
    if full and username:
        return f"{font(full)} (@{username})"
    return f"@{username}" if username else font(full or "Member")


def parse_add(text):
    raw = (text or "").split(maxsplit=1)
    if len(raw) < 2:
        return None
    parts = [x.strip() for x in raw[1].split("|")]
    if len(parts) < 3:
        return None
    key = word(parts[0])
    aliases = [word(x) for x in parts[1].split(",")]
    aliases = [x for x in aliases if x]
    action = parts[2].strip()[:40]
    if not key or not aliases or not action:
        return None
    aliases = list(dict.fromkeys([key] + aliases))[:12]
    return key, aliases, action


async def fun_text():
    rows = await fun_db.find({}).sort("key", 1).to_list(length=25)
    text = font("FUN ZONE") + "\n━━━━━━━━━━━━━━━━━━━━\n\n" + font("Reply to a member and use a fun action.") + "\n\n"
    if rows:
        for row in rows:
            aliases = row.get("aliases", [])[:4]
            text += "• " + ", ".join(f"/{x}" for x in aliases) + "\n"
    else:
        text += "/hug\n/huggy\n/pat\n/dance\n/kiss"
    return text


def owner_guide():
    return font("FUN ZONE GUIDE") + "\n━━━━━━━━━━━━━━━━━━━━\n\n" + font("Reply to media and use:") + "\n/addfun key | alias1,alias2 | action\n\n" + font("Examples:") + "\n/addfun hug | hug,huggy | hugged\n/addfun kiss | kiss | sent a cute kiss to\n\n/funlist\n/delfun key"


async def addfun(event):
    if not await is_owner(event):
        await event.reply(font("Owner only."))
        raise events.StopPropagation
    reply = await event.get_reply_message()
    if not reply or not reply.media:
        await event.reply(font("Reply to media first."))
        raise events.StopPropagation
    parsed = parse_add(event.raw_text)
    if not parsed:
        await event.reply(font("Use: /addfun key | aliases | action"))
        raise events.StopPropagation
    key, aliases, action = parsed
    await fun_db.update_one({"key": key}, {"$set": {"key": key, "aliases": aliases, "action": action, "chat_id": int(reply.chat_id), "msg_id": int(reply.id), "updated_at": int(time.time())}}, upsert=True)
    await event.reply(font("Saved:") + f" /{key}\n" + ", ".join(f"/{x}" for x in aliases))
    raise events.StopPropagation


async def delfun(event):
    if not await is_owner(event):
        await event.reply(font("Owner only."))
        raise events.StopPropagation
    parts = (event.raw_text or "").split(maxsplit=1)
    key = word(parts[1]) if len(parts) > 1 else None
    if not key:
        await event.reply(font("Use: /delfun key"))
        raise events.StopPropagation
    res = await fun_db.delete_one({"key": key})
    await event.reply(font("Deleted." if res.deleted_count else "Action not found."))
    raise events.StopPropagation


async def funlist(event):
    if not await is_owner(event):
        await event.reply(font("Owner only."))
        raise events.StopPropagation
    rows = await fun_db.find({}).sort("key", 1).to_list(length=50)
    text = font("FUN ZONE ACTIONS") + "\n━━━━━━━━━━━━━━━━━━━━\n\n"
    text += font("No actions added yet.") if not rows else "".join(f"/{r.get('key')} - " + ", ".join(f"/{x}" for x in r.get("aliases", [])) + "\n" for r in rows)
    await event.reply(text)
    raise events.StopPropagation


async def action(event):
    text = (event.raw_text or "").strip()
    if not text or text[0] not in prefix_cmds:
        return
    cmd = word(text.split()[0])
    if not cmd or cmd in RESERVED:
        return
    data = await fun_db.find_one({"aliases": cmd})
    if not data:
        return
    reply = await event.get_reply_message()
    if not reply:
        await event.reply(font(f"Reply to someone and use /{cmd}."))
        raise events.StopPropagation
    actor = await event.get_sender()
    target = await reply.get_sender()
    caption = font("𓆩 AZAI FUN ZONE 𓆪") + "\n━━━━━━━━━━━━━━━━━━━━\n" + name(actor) + " " + font(data.get("action", "sent fun to")) + " " + name(target)
    try:
        m = await tbot.get_messages(int(data["chat_id"]), ids=int(data["msg_id"]))
        if m and m.media:
            await tbot.send_file(event.chat_id, m.media, caption=caption, reply_to=reply.id)
        else:
            await event.reply(caption)
    except Exception:
        await event.reply(caption)
    raise events.StopPropagation


def help_buttons():
    return [
        [Button.inline(font("Core"), b"azai_help_core"), Button.inline(font("Owner"), b"azai_help_owner")],
        [Button.inline(font("Economy"), b"azai_help_economy"), Button.inline(font("Market"), b"azai_help_market")],
        [Button.inline(font("Family"), b"azai_help_family"), Button.inline(font("Games"), b"azai_help_games")],
        [Button.inline(font("Fun Zone"), b"azai_help_fun"), Button.inline(font("Anime Quiz"), b"azai_help_quiz")],
        [Button.inline(font("Media"), b"azai_help_media"), Button.inline(font("System"), b"azai_system_stats")],
        [Button.inline(font("Back"), b"azai_start_home"), Button.inline(font("Close"), b"azai_close_panel")],
    ]


start_panel.help_buttons = help_buttons


async def fun_help(event):
    await event.edit(await fun_text(), buttons=start_panel.close_back_buttons())
    raise events.StopPropagation


if owner_panel:
    old_guide = owner_panel.guide_text
    def guide():
        return old_guide() + "\n\n" + owner_guide()
    owner_panel.guide_text = guide


if "zzzz_azai_fun_zone" not in tbot.handlers_loaded:
    tbot.add_event_handler(addfun, events.NewMessage(pattern=f"^{prefix_cmds}addfun(?: .*)?$", incoming=True))
    tbot.add_event_handler(delfun, events.NewMessage(pattern=f"^{prefix_cmds}delfun(?: .*)?$", incoming=True))
    tbot.add_event_handler(funlist, events.NewMessage(pattern=f"^{prefix_cmds}funlist$", incoming=True))
    tbot.add_event_handler(fun_help, events.CallbackQuery(pattern=b"^azai_help_fun$"))
    tbot.add_event_handler(action, events.NewMessage(incoming=True))
    tbot.handlers_loaded.add("zzzz_azai_fun_zone")
