from telethon import Button, events

from AloneX import font, prefix_cmds, tbot

SUPPORT_LINK = "https://t.me/EGOxSUPPORT"
UPDATES_LINK = "https://t.me/EGOxUPDATES"
MASTER_LINK = "https://t.me/EGOISTICxPRIME"


def home_text():
    return (
        font("AZAI GROUP SETUP") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Owner:") + " " + font("MR EGO") + "\n"
        + font("Network:") + " " + font("EGO Network - EST. 2026") + "\n\n"
        + font("Choose a setup panel below.")
    )


def buttons():
    return [
        [Button.inline(font("Security"), b"azset_security"), Button.inline(font("Market"), b"azset_market")],
        [Button.inline(font("Media"), b"azset_media"), Button.inline(font("Fun Zone"), b"azset_fun")],
        [Button.url(font("Support"), SUPPORT_LINK), Button.url(font("Updates"), UPDATES_LINK)],
        [Button.url(font("My Master"), MASTER_LINK), Button.inline(font("Close"), b"azset_close")],
    ]


def back_buttons():
    return [[Button.inline(font("Back"), b"azset_home"), Button.inline(font("Close"), b"azset_close")]]


def panel(title, body):
    return font(title) + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n" + body


def security_text():
    return panel("SECURITY SETUP", "/verifyall\n/unverifyall\n/verify\n/logstatus\n/logon\n/logoff")


def market_text():
    return panel("MARKET SETUP", "/shop\n/garage\n/inventory\n/vaultitems\n/buyvault item_id")


def media_text():
    return panel("MEDIA SETUP", "/setstartpic\n/setitempic item_id\n/setleaderpic")


def fun_text():
    return panel("FUN ZONE SETUP", font("Reply to media and use:") + "\n/addfun hug | hug,huggy | hugged\n/addfun kiss | kiss | sent a cute kiss to\n\n/funlist\n/delfun key")


async def settings_handler(event):
    await event.reply(home_text(), buttons=buttons())
    raise events.StopPropagation


async def settings_callback(event):
    data = event.data.decode()
    if data == "azset_home":
        await event.edit(home_text(), buttons=buttons())
    elif data == "azset_security":
        await event.edit(security_text(), buttons=back_buttons())
    elif data == "azset_market":
        await event.edit(market_text(), buttons=back_buttons())
    elif data == "azset_media":
        await event.edit(media_text(), buttons=back_buttons())
    elif data == "azset_fun":
        await event.edit(fun_text(), buttons=back_buttons())
    elif data == "azset_close":
        await event.delete()
    raise events.StopPropagation


if "aaaa_azai_group_setup" not in tbot.handlers_loaded:
    tbot.add_event_handler(settings_handler, events.NewMessage(pattern=f"^{prefix_cmds}settings(?:@\\w+)?$", incoming=True))
    tbot.add_event_handler(settings_callback, events.CallbackQuery(pattern=b"^azset_"))
    tbot.handlers_loaded.add("aaaa_azai_group_setup")
