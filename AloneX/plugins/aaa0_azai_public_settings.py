from telethon import Button, events

from AloneX import font, prefix_cmds, tbot
from config import ALONE_OWNER_ID, OWNER_ID

SUPPORT = "https://t.me/EGOxSUPPORT"
UPDATES = "https://t.me/EGOxUPDATES"


def owner_ids():
    ids = set()
    for value in (ALONE_OWNER_ID, OWNER_ID):
        try:
            if int(value):
                ids.add(int(value))
        except Exception:
            pass
    return ids


async def can_manage(event):
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


def settings_text(admin=False):
    mode = "Admin Setup" if admin else "Public View"
    line = "Safe group setup is available for admins." if admin else "Use /help for commands. Only admins can change group setup."
    return font("AZAI GROUP SETTINGS") + "\n━━━━━━━━━━━━━━━━━━━━\n\n" + font("Mode:") + " " + font(mode) + "\n" + font("Network:") + " " + font("EGO Network - EST. 2026") + "\n\n" + font(line)


def public_buttons():
    return [[Button.inline(font("Info"), b"azpub_info")], [Button.url(font("Support"), SUPPORT), Button.url(font("Updates"), UPDATES)], [Button.inline(font("Close"), b"azpub_close")]]


def admin_buttons():
    return [[Button.inline(font("Media"), b"azpub_media"), Button.inline(font("Fun Zone"), b"azpub_fun")], [Button.url(font("Support"), SUPPORT), Button.url(font("Updates"), UPDATES)], [Button.inline(font("Close"), b"azpub_close")]]


def back(admin=False):
    return [[Button.inline(font("Back"), b"azpub_admin" if admin else b"azpub_home"), Button.inline(font("Close"), b"azpub_close")]]


async def settings(event):
    admin = await can_manage(event)
    await event.reply(settings_text(admin), buttons=admin_buttons() if admin else public_buttons())
    raise events.StopPropagation


async def cb(event):
    data = event.data.decode()
    admin = await can_manage(event)
    if data == "azpub_close":
        await event.delete()
    elif data == "azpub_home":
        await event.edit(settings_text(False), buttons=public_buttons())
    elif data == "azpub_admin":
        if not admin:
            await event.answer(font("Group admin only."), alert=True)
            raise events.StopPropagation
        await event.edit(settings_text(True), buttons=admin_buttons())
    elif data == "azpub_info":
        await event.edit(font("PUBLIC INFO") + "\n━━━━━━━━━━━━━━━━━━━━\n\n/help\n/ping\n/shop\n/quiz\n/events", buttons=back(False))
    elif data == "azpub_media":
        if not admin:
            await event.answer(font("Group admin only."), alert=True)
            raise events.StopPropagation
        await event.edit(font("MEDIA SETUP") + "\n━━━━━━━━━━━━━━━━━━━━\n\n" + font("Group admins can manage safe group media setup."), buttons=back(True))
    elif data == "azpub_fun":
        if not admin:
            await event.answer(font("Group admin only."), alert=True)
            raise events.StopPropagation
        await event.edit(font("FUN ZONE SETUP") + "\n━━━━━━━━━━━━━━━━━━━━\n\n" + font("Group admins can manage safe fun media actions."), buttons=back(True))
    raise events.StopPropagation


if "aaa0_azai_public_settings" not in tbot.handlers_loaded:
    tbot.add_event_handler(settings, events.NewMessage(pattern=f"^{prefix_cmds}settings(?:@\\w+)?$", incoming=True))
    tbot.add_event_handler(cb, events.CallbackQuery(pattern=b"^azpub_"))
    tbot.handlers_loaded.add("aaa0_azai_public_settings")
