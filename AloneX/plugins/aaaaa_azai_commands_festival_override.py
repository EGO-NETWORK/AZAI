from telethon import Button, events

from AloneX import font, prefix_cmds, tbot

BRAND = font("EGO Network - EST. 2026")


def home_text():
    return (
        font("AZAI COMMAND CENTER") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Choose a command section below.") + "\n"
        + font("Festival calendar is now active.") + "\n\n"
        + font("Powered By:") + " " + BRAND
    )


def buttons():
    return [
        [Button.inline(font("User"), b"azcmd_user"), Button.inline(font("Profile"), b"azcmd_profile")],
        [Button.inline(font("Verification"), b"azcmd_verify"), Button.inline(font("Admin"), b"azcmd_admin")],
        [Button.inline(font("Moderation"), b"azcmd_mod"), Button.inline(font("Economy"), b"azcmd_eco")],
        [Button.inline(font("Market"), b"azcmd_market"), Button.inline(font("Events"), b"azcmd_events")],
        [Button.inline(font("Festivals"), b"azcmd_festivals"), Button.inline(font("Games"), b"azcmd_games")],
        [Button.inline(font("Stickers"), b"azcmd_media"), Button.inline(font("Coming Soon"), b"azcmd_soon")],
        [Button.inline(font("Close"), b"azcmd_close")],
    ]


def back_buttons():
    return [[Button.inline(font("Back"), b"azcmd_home"), Button.inline(font("Close"), b"azcmd_close")]]


def festival_text():
    return (
        font("FESTIVAL COMMANDS") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + "/festivals - " + font("Open festival calendar") + "\n"
        + "/todayfestivals - " + font("Show today's festivals") + "\n"
        + "/addfestival DD/MM | name | wish - " + font("Owner: add or update festival") + "\n"
        + "/delfestival name - " + font("Owner: delete festival") + "\n"
        + "/festivalauto on | off | status - " + font("Owner: control festival auto wishes") + "\n\n"
        + font("Note:") + " " + font("Movable dates can be edited by owner every year.") + "\n\n"
        + font("Powered By:") + " " + BRAND
    )


async def commands_handler(event):
    if event.is_channel and not event.is_group:
        return
    await event.reply(home_text(), buttons=buttons())
    raise events.StopPropagation


async def callback_handler(event):
    data = event.data.decode()
    if data == "azcmd_home":
        await event.edit(home_text(), buttons=buttons())
        raise events.StopPropagation
    if data == "azcmd_festivals":
        await event.edit(festival_text(), buttons=back_buttons())
        raise events.StopPropagation


if "aaaaa_azai_commands_festival_override" not in tbot.handlers_loaded:
    tbot.add_event_handler(commands_handler, events.NewMessage(pattern=f"^{prefix_cmds}commands$", incoming=True))
    tbot.add_event_handler(callback_handler, events.CallbackQuery(pattern=b"^azcmd_(home|festivals)$"))
    tbot.handlers_loaded.add("aaaaa_azai_commands_festival_override")
