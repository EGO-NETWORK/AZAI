from telethon import Button, events

from AloneX import font, prefix_cmds, tbot

UPDATES_LINK = "https://t.me/EGOxUPDATES"
SUPPORT_LINK = "https://t.me/EGOxSUPPORT"


def group_settings_text() -> str:
    return (
        font("AZAI GROUP SETTINGS") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Use these AZAI controls:") + "\n\n"
        + "/group - " + font("Group panel") + "\n"
        + "/verify - " + font("Verify yourself") + "\n"
        + "/verifyall - " + font("Admin verify all") + "\n"
        + "/unverifyall - " + font("Admin reset verification") + "\n"
        + "/mod - " + font("Moderation panel") + "\n"
        + "/warn - " + font("Warn a user") + "\n"
        + "/mute - " + font("Mute a user") + "\n"
        + "/ban - " + font("Ban a user") + "\n"
        + "/antilink on/off - " + font("Link guard") + "\n"
        + "/commands - " + font("All commands") + "\n"
        + "/owner - " + font("Owner control panel") + "\n\n"
        + font("Old settings links are redirected to AZAI branding.") + "\n\n"
        + font("Powered By:") + " " + font("EGO Network - EST. 2026")
    )


def media_settings_text() -> str:
    return (
        font("AZAI BOT SETTINGS") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Mode:") + " " + font("Admin setup") + "\n"
        + font("Network:") + " " + font("EGO Network - EST. 2026") + "\n\n"
        + font("Media setup:") + "\n"
        + "/setstartpic - " + font("Set start/help panel media") + "\n"
        + "/setitempic item_id - " + font("Set shop/item media") + "\n"
        + "/setleaderpic - " + font("Set leaderboard media") + "\n\n"
        + font("Fun zone setup:") + "\n"
        + font("Use Fun Zone panel from owner panel after adding media packs.") + "\n\n"
        + font("Use this panel only in groups where AZAI is admin.")
    )


def settings_buttons():
    return [
        [Button.inline(font("Moderation"), b"azset_mod"), Button.inline(font("Media"), b"azset_media")],
        [Button.url(font("Support"), SUPPORT_LINK), Button.url(font("Updates"), UPDATES_LINK)],
        [Button.inline(font("Close"), b"azset_close")],
    ]


async def settings_handler(event):
    await event.reply(group_settings_text(), buttons=settings_buttons())
    raise events.StopPropagation


async def msettings_handler(event):
    await event.reply(media_settings_text(), buttons=settings_buttons())
    raise events.StopPropagation


async def settings_callback(event):
    data = event.data.decode()
    if data == "azset_mod":
        text = (
            font("AZAI MODERATION") + "\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            + "/warn - " + font("Warn user") + "\n"
            + "/mute - " + font("Mute user") + "\n"
            + "/ban - " + font("Ban user") + "\n"
            + "/unban - " + font("Unban user") + "\n"
            + "/antilink on/off - " + font("Link guard")
        )
        await event.edit(text, buttons=settings_buttons())
    elif data == "azset_media":
        await event.edit(media_settings_text(), buttons=settings_buttons())
    elif data == "azset_close":
        await event.delete()
    raise events.StopPropagation


if "aa00_azai_premium_settings" not in tbot.handlers_loaded:
    tbot.add_event_handler(settings_handler, events.NewMessage(pattern=f"^{prefix_cmds}settings(?:@\\w+)?$", incoming=True))
    tbot.add_event_handler(msettings_handler, events.NewMessage(pattern=f"^{prefix_cmds}msettings(?:@\\w+)?$", incoming=True))
    tbot.add_event_handler(settings_callback, events.CallbackQuery(pattern=b"^azset_"))
    tbot.handlers_loaded.add("aa00_azai_premium_settings")
