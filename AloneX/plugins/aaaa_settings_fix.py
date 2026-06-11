from telethon import events

from AloneX import font, prefix_cmds, tbot


async def settings_fix(event):
    if event.is_private:
        await event.reply(font("This command works only inside groups."))
    else:
        text = (
            font("AZAI SETTINGS") + "\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            + font("Old settings panel is disabled.") + "\n"
            + font("Use /commands for all AZAI commands.") + "\n"
            + font("Use /owner for owner control panel.") + "\n"
            + font("Use /verify, /verifyall, /unverifyall for verification.") + "\n\n"
            + font("Powered By: EGO Network - EST. 2026")
        )
        await event.reply(text)
    raise events.StopPropagation


if "aaaa_settings_fix" not in tbot.handlers_loaded:
    tbot.add_event_handler(settings_fix, events.NewMessage(pattern=f"^{prefix_cmds}(settings|msettings)(?:@\\w+)?$", incoming=True))
    tbot.handlers_loaded.add("aaaa_settings_fix")
