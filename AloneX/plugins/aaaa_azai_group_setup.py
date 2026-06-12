from telethon import events

from AloneX import font, prefix_cmds, tbot


async def settings_handler(event):
    text = (
        font("AZAI GROUP SETUP") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Owner:") + " " + font("MR EGO") + "\n"
        + font("Network:") + " " + font("EGO Network - EST. 2026") + "\n\n"
        + font("Security:") + " /verifyall /unverifyall /logstatus\n"
        + font("Market:") + " /shop /garage /inventory\n"
        + font("Media:") + " /setstartpic /setitempic item_id\n"
        + font("Control:") + " /owner /ping"
    )
    await event.reply(text)
    raise events.StopPropagation


if "aaaa_azai_group_setup" not in tbot.handlers_loaded:
    tbot.add_event_handler(settings_handler, events.NewMessage(pattern=f"^{prefix_cmds}settings(?:@\\w+)?$", incoming=True))
    tbot.handlers_loaded.add("aaaa_azai_group_setup")
