from telethon import Button, events

from AloneX import font, prefix_cmds, tbot
from config import ALONE_OWNER_ID, OWNER_ID


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


def panel_buttons():
    return [
        [Button.inline(font("ToneGuard"), b"az_owner:tone"), Button.inline(font("EGO Media"), b"az_owner:media")],
        [Button.inline(font("Broadcast"), b"az_owner:broadcast"), Button.inline(font("Anime Quiz"), b"az_owner:anime")],
        [Button.inline(font("EGO Hustle"), b"az_owner:hustle"), Button.inline(font("Settings"), b"az_owner:settings")],
        [Button.inline(font("Close"), b"az_owner:close")],
    ]


def home_text():
    return (
        font("AZAI OWNER PANEL")
        + "\n━━━━━━━━━━━━━━━━━━━━\n"
        + font("Master Control for MR EGO")
        + "\n\n"
        + font("Choose a system below.")
    )


def section_text(name, lines):
    text = font(name) + "\n━━━━━━━━━━━━━━━━━━━━"
    for line in lines:
        text += "\n" + line
    return text


def back_buttons():
    return [[Button.inline(font("Back"), b"az_owner:home"), Button.inline(font("Close"), b"az_owner:close")]]


async def owner_panel(event):
    await owner_only(event)
    await event.reply(home_text(), buttons=panel_buttons())
    raise events.StopPropagation


async def owner_cb(event):
    if int(event.sender_id or 0) not in owner_ids():
        await event.answer("Owner only", alert=True)
        raise events.StopPropagation
    data = event.data.decode()
    if data == "az_owner:close":
        await event.delete()
    elif data == "az_owner:home":
        await event.edit(home_text(), buttons=panel_buttons())
    elif data == "az_owner:tone":
        await event.edit(section_text("TONEGUARD", ["/tonepanel", "/toneguard on", "/toneguard off", "/toneadd <trigger>", "/tonelist", "/tonereplylist"]), buttons=back_buttons())
    elif data == "az_owner:media":
        await event.edit(section_text("EGO HUSTLE MEDIA", ["/egohmedia", "/sethustlepic", "/setwalletpic", "/setdailypic", "/setworkpic", "/setluckpic", "/setprotectpic", "/setraidpic", "/setattackpic", "/setheistpic", "/setleaderboardpic", "/setprofilepic"]), buttons=back_buttons())
    elif data == "az_owner:broadcast":
        await event.edit(section_text("BROADCAST", ["/broadcastchats", "/broadcast -all <message>", "/broadcast -users <message>", "/broadcast -groups <message>", "/broadcast -pin -all <message>", "Reply media + /broadcast -all"]), buttons=back_buttons())
    elif data == "az_owner:anime":
        await event.edit(section_text("ANIME QUIZ", ["/animeguess", "/animequiz on", "/animequiz off", "Auto quiz interval uses AZAI_ANIME_QUIZ_INTERVAL"]), buttons=back_buttons())
    elif data == "az_owner:hustle":
        await event.edit(section_text("EGO HUSTLE", ["/hustle", "/bal", "/daily", "/work", "/luck", "/protect 6h", "/raid", "/attack", "/heist", "/leaderboard", "/profile"]), buttons=back_buttons())
    elif data == "az_owner:settings":
        await event.edit(section_text("SETTINGS", ["/settings", "/owner", "/commands", "Use group admin permissions for mute, delete, pin."]), buttons=back_buttons())
    raise events.StopPropagation


if "0001_azai_owner_control_panel" not in tbot.handlers_loaded:
    tbot.add_event_handler(owner_panel, events.NewMessage(pattern=f"^{prefix_cmds}(ownerpanel|azpanel|masterpanel|owner)(?:@\\w+)?$", incoming=True))
    tbot.add_event_handler(owner_cb, events.CallbackQuery(pattern=b"^az_owner:"))
    tbot.handlers_loaded.add("0001_azai_owner_control_panel")
