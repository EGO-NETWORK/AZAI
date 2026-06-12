from telethon import events

from AloneX import font, prefix_cmds, tbot
from config import ALONE_OWNER_ID, OWNER_ID


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


def panel_text():
    return (
        font("FESTIVAL CONTROL") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Calendar:") + " /festivals\n"
        + font("Today:") + " /todayfestivals\n"
        + font("Add or Update:") + " /addfestival DD/MM | name | wish\n"
        + font("Delete:") + " /delfestival name\n"
        + font("Auto Wish:") + " /festivalauto on | off | status\n\n"
        + font("Movable dates can be edited by owner every year.")
    )


async def control_handler(event):
    if not await is_owner(event):
        await event.reply(font("Owner only."))
        raise events.StopPropagation
    await event.reply(panel_text())
    raise events.StopPropagation


if "azai_festival_control" not in tbot.handlers_loaded:
    tbot.add_event_handler(control_handler, events.NewMessage(pattern=f"^{prefix_cmds}festcontrol(?:@\\w+)?$", incoming=True))
    tbot.handlers_loaded.add("azai_festival_control")
