from telethon import events

from AloneX import font, prefix_cmds, tbot

REMOVED_COMMANDS = ("prop", "weds", "ageverify")


async def removed_command_handler(event):
    await event.reply(font("This command has been removed by owner."))
    raise events.StopPropagation


if "aaa_azai_removed_shortcuts" not in tbot.handlers_loaded:
    for cmd in REMOVED_COMMANDS:
        tbot.add_event_handler(
            removed_command_handler,
            events.NewMessage(pattern=f"^{prefix_cmds}{cmd}(?:@\\w+)?$", incoming=True),
        )
    tbot.handlers_loaded.add("aaa_azai_removed_shortcuts")
