from telethon import Button, events

from AloneX import font, prefix_cmds, tbot
from config import ALONE_OWNER_ID, OWNER_ID

SUPPORT_LINK = "https://t.me/EGOxSUPPORT"
UPDATES_LINK = "https://t.me/EGOxUPDATES"
MASTER_LINK = "https://t.me/EGOISTICxPRIME"


def owner_ids() -> set[int]:
    ids = set()
    for value in (ALONE_OWNER_ID, OWNER_ID):
        try:
            if int(value):
                ids.add(int(value))
        except Exception:
            pass
    return ids


async def is_owner_or_admin(event) -> bool:
    sender = await event.get_sender()
    if not sender:
        return False
    if int(sender.id) in owner_ids():
        return True
    if event.is_private:
        return False
    try:
        perms = await event.client.get_permissions(event.chat_id, sender.id)
        return bool(getattr(perms, "is_admin", False) or getattr(perms, "is_creator", False))
    except Exception:
        return False


def home_text():
    return (
        font("AZAI GROUP SETUP") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Access:") + " " + font("Group Admin / Bot Owner") + "\n"
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
    return panel("MEDIA SETUP", "/setstartpic\n/setitempic item_id\n/setleaderpic\n/stickerpack add <pack> <mood>\n/stickerpack remove <pack>\n/stickerpack list\n/stickermood <mood>")


def fun_text():
    return panel("FUN ZONE SETUP", font("Reply to media and use:") + "\n/addfun hug | hug,huggy | hugged\n/addfun kiss | kiss | sent a cute kiss to\n\n/funlist\n/delfun key")


async def settings_handler(event):
    if not await is_owner_or_admin(event):
        await event.reply(font("Group admin only."))
        raise events.StopPropagation
    await event.reply(home_text(), buttons=buttons())
    raise events.StopPropagation


async def settings_callback(event):
    if not await is_owner_or_admin(event):
        await event.answer(font("Group admin only."), alert=True)
        raise events.StopPropagation
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
