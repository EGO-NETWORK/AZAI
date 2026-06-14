from telethon import Button, events

from AloneX import database, font, prefix_cmds, tbot
from config import ALONE_OWNER_ID, OWNER_ID

panel_db = database["azai_panel_media"]

PANEL_SETTERS = {
    "sethelppic": "help",
    "setsettingspic": "settings",
    "seteconomypic": "economy",
    "setgamespic": "games",
    "setfamilypic": "family",
    "setquizpic": "animequiz",
    "setownerpic": "owner",
    "setcorepic": "core",
}

PANEL_TITLES = {
    "help": "AZAI COMMAND CENTER",
    "settings": "AZAI GROUP SETTINGS",
    "economy": "ECONOMY COMMANDS",
    "games": "GAME COMMANDS",
    "family": "FAMILY COMMANDS",
    "animequiz": "ANIME QUIZ PANEL",
    "owner": "OWNER COMMANDS",
    "core": "CORE COMMANDS",
}


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


def line(cmd: str, desc: str) -> str:
    return f"{cmd} - {font(desc)}\n"


def close_buttons():
    return [[Button.inline(font("Close"), b"azpm_close")]]


def help_buttons():
    return [
        [Button.inline(font("Core"), b"azpm_core"), Button.inline(font("Economy"), b"azpm_economy")],
        [Button.inline(font("Games"), b"azpm_games"), Button.inline(font("Family"), b"azpm_family")],
        [Button.inline(font("Anime Quiz"), b"azpm_animequiz"), Button.inline(font("Owner"), b"azpm_owner")],
        [Button.inline(font("Close"), b"azpm_close")],
    ]


def panel_text(key: str) -> str:
    if key == "help":
        return font("AZAI COMMAND CENTER") + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n" + font("Choose a command category below.")
    if key == "core":
        return font("CORE COMMANDS") + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n" + line("/start", "Open the official AZAI start panel") + line("/help", "Open the command help menu") + line("/ping", "Check bot speed") + line("/alive", "Check AZAI online status")
    if key == "settings":
        return font("AZAI GROUP SETTINGS") + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n" + line("/group", "Open group panel") + line("/verify", "Verify yourself") + line("/verifyall", "Admin verify all") + line("/unverifyall", "Admin reset verification") + line("/mod", "Open moderation panel") + line("/antilink on/off", "Control link guard") + line("/owner", "Open owner panel")
    if key == "economy":
        return font("ECONOMY COMMANDS") + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n" + line("/bal", "Check EC balance") + line("/daily", "Claim daily EC reward") + line("/work", "Earn EC through tasks") + line("/leaderboard", "Open economy ranking") + line("/profile", "Open your profile")
    if key == "games":
        return font("GAME COMMANDS") + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n" + line("/hustle", "Open EGO Hustle") + line("/dice", "Play dice") + line("/dart", "Play dart") + line("/basketball", "Play basketball") + line("/slot", "Play slot")
    if key == "family":
        return font("FAMILY COMMANDS") + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n" + line("/brother", "Send brother relation request") + line("/sister", "Send sister relation request") + line("/adopt", "Send adopt relation request") + line("/family", "View family list") + line("/familytree", "Open family tree")
    if key == "animequiz":
        return font("ANIME QUIZ PANEL") + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n" + line("/animeguess", "Start anime image quiz") + line("/quiz", "Open quiz panel") + line("/quizstats", "View your quiz stats") + line("/quiztop", "View quiz leaderboard")
    if key == "owner":
        return font("OWNER COMMANDS") + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n" + line("/owner", "Open owner control panel") + line("/msettings", "Open media setup guide") + line("/panelmedia", "View panel media guide")
    return font("AZAI PANEL")


async def saved_media(key: str):
    data = await panel_db.find_one({"key": key})
    if not data:
        return None
    try:
        msg = await tbot.get_messages(int(data["chat_id"]), ids=int(data["msg_id"]))
        return msg.media if msg and msg.media else None
    except Exception:
        return None


async def send_panel(event, key: str, buttons=None):
    text = panel_text(key)
    media = await saved_media(key)
    if media:
        await tbot.send_file(event.chat_id, media, caption=text, buttons=buttons)
    else:
        await event.reply(text, buttons=buttons)
    raise events.StopPropagation


async def panel_command(event):
    cmd = (event.raw_text or "").split()[0].lstrip("/!.").lower()
    mapping = {
        "help": "help",
        "commands": "help",
        "cmds": "help",
        "settings": "settings",
        "economy": "economy",
        "games": "games",
        "familycmds": "family",
        "animequiz": "animequiz",
        "quizhelp": "animequiz",
        "corecmds": "core",
    }
    key = mapping.get(cmd)
    if key == "help":
        await send_panel(event, key, help_buttons())
    elif key:
        await send_panel(event, key, close_buttons())


async def panel_callback(event):
    key = event.data.decode().replace("azpm_", "")
    if key == "close":
        await event.delete()
        raise events.StopPropagation
    if key == "help":
        await send_panel(event, "help", help_buttons())
    if key in PANEL_TITLES:
        await event.delete()
        await send_panel(event, key, close_buttons())


async def save_panel_media(event):
    if not await is_owner(event):
        await event.reply(font("Owner only."))
        raise events.StopPropagation
    cmd = (event.raw_text or "").split()[0].lstrip("/!.").lower()
    key = PANEL_SETTERS.get(cmd)
    reply = await event.get_reply_message()
    if not key or not reply or not reply.media:
        await event.reply(font("Reply to media and use a panel media command."))
        raise events.StopPropagation
    await panel_db.update_one({"key": key}, {"$set": {"key": key, "chat_id": int(reply.chat_id), "msg_id": int(reply.id)}}, upsert=True)
    await event.reply(font("Panel media saved:") + " " + PANEL_TITLES.get(key, key))
    raise events.StopPropagation


async def panelmedia_guide(event):
    if not await is_owner(event):
        await event.reply(font("Owner only."))
        raise events.StopPropagation
    text = font("PANEL MEDIA GUIDE") + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    text += "/sethelppic - " + font("Set /help media") + "\n"
    text += "/setsettingspic - " + font("Set /settings media") + "\n"
    text += "/seteconomypic - " + font("Set Economy panel media") + "\n"
    text += "/setgamespic - " + font("Set Games panel media") + "\n"
    text += "/setfamilypic - " + font("Set Family panel media") + "\n"
    text += "/setquizpic - " + font("Set Anime Quiz panel media") + "\n"
    text += "/setownerpic - " + font("Set Owner command panel media") + "\n"
    text += "/setcorepic - " + font("Set Core command panel media") + "\n\n"
    text += font("Use: send media, reply to it, then run the command.")
    await event.reply(text)
    raise events.StopPropagation


if "aa000_azai_panel_media_manager" not in tbot.handlers_loaded:
    tbot.add_event_handler(panel_command, events.NewMessage(pattern=f"^{prefix_cmds}(help|commands|cmds|settings|economy|games|familycmds|animequiz|quizhelp|corecmds)(?:@\\w+)?$", incoming=True))
    tbot.add_event_handler(save_panel_media, events.NewMessage(pattern=f"^{prefix_cmds}(sethelppic|setsettingspic|seteconomypic|setgamespic|setfamilypic|setquizpic|setownerpic|setcorepic)$", incoming=True))
    tbot.add_event_handler(panelmedia_guide, events.NewMessage(pattern=f"^{prefix_cmds}panelmedia(?:@\\w+)?$", incoming=True))
    tbot.add_event_handler(panel_callback, events.CallbackQuery(pattern=b"^azpm_"))
    tbot.handlers_loaded.add("aa000_azai_panel_media_manager")
