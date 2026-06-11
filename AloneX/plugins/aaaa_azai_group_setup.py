from telethon import Button, events

from AloneX import font, prefix_cmds, tbot

CMD = "sett" + "ings"


def text():
    return (
        font("AZAI GROUP SETUP")
        + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Use AZAI commands below:")
        + "\n/group\n/rules\n/verify\n/verifyall\n/unverifyall\n/mod\n/shop\n/leaderboard\n"
        + "\n"
        + font("Powered By: EGO Network - EST. 2026")
    )


def buttons():
    return [[Button.inline(font("Close"), b"azsetup_close")]]


async def setup_panel(event):
    if event.is_private:
        await event.reply(font("Use this inside a group."))
        raise events.StopPropagation
    await event.reply(text(), buttons=buttons())
    raise events.StopPropagation


async def close_panel(event):
    await event.delete()


if "aaaa_azai_group_setup" not in tbot.handlers_loaded:
    pattern = rf"^[{prefix_cmds}]{CMD}(?:@\\w+)?$"
    tbot.add_event_handler(setup_panel, events.NewMessage(pattern=pattern, incoming=True))
    tbot.add_event_handler(close_panel, events.CallbackQuery(pattern=b"^azsetup_close$"))
    tbot.handlers_loaded.add("aaaa_azai_group_setup")
