from telethon import Button, events

from AloneX import font, prefix_cmds, tbot

SUPPORT_LINK = "https://t.me/EGOxSUPPORT"
UPDATES_LINK = "https://t.me/EGOxUPDATES"
MASTER_LINK = "https://t.me/EGOISTICxPRIME"


def games_buttons():
    return [
        [Button.url(font("Support"), SUPPORT_LINK), Button.url(font("Updates"), UPDATES_LINK)],
        [Button.url(font("Owner"), MASTER_LINK), Button.inline(font("Close"), b"azgp_close")],
    ]


def games_text():
    return (
        font("AZAI GAME PANEL") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Available commands") + "\n"
        + "/dice\n"
        + "/dart\n"
        + "/basketball\n\n"
        + font("Clean mini-game handlers are active.")
    )


async def games_handler(event):
    await event.reply(games_text(), buttons=games_buttons())
    raise events.StopPropagation


async def close_handler(event):
    try:
        await event.answer(font("Closed."), alert=False)
    except Exception:
        pass
    try:
        await event.delete()
    except Exception:
        pass


if "azai_games_panel" not in tbot.handlers_loaded:
    tbot.add_event_handler(games_handler, events.NewMessage(pattern=f"^{prefix_cmds}games(?:@\\w+)?$", incoming=True))
    tbot.add_event_handler(close_handler, events.CallbackQuery(data=b"azgp_close"))
    tbot.handlers_loaded.add("azai_games_panel")
