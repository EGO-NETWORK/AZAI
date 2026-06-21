"""AZAI group join welcome panel."""

from telethon import Button, events, types

from AloneX import font, tbot
from AloneX.plugins.aaa_azai_start_pic import saved_pic

UPDATES_LINK = "https://t.me/EGOxUPDATES"
SUPPORT_LINK = "https://t.me/EGOxSUPPORT"


def welcome_buttons():
    return [
        [Button.url(font("Support"), SUPPORT_LINK), Button.url(font("Updates"), UPDATES_LINK)],
        [Button.inline(font("Settings"), b"azgw_settings"), Button.inline(font("Close"), b"azgw_close")],
    ]


def readable_user(user) -> str:
    username = getattr(user, "username", None)
    if username:
        return f"@{username}"
    return getattr(user, "first_name", None) or "Admin"


async def admin_mentions(chat_id: int) -> str:
    names = []
    try:
        async for user in tbot.iter_participants(chat_id, filter=types.ChannelParticipantsAdmins):
            if getattr(user, "bot", False):
                continue
            label = readable_user(user)
            if label not in names:
                names.append(label)
            if len(names) >= 6:
                break
    except Exception:
        pass
    return ", ".join(names) if names else "Admins / Owner"


def welcome_text(group_name: str, admin_line: str) -> str:
    return (
        font("AZAI HAS JOINED YOUR GROUP")
        + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Thank you for adding AZAI to") + f" {group_name}.\n"
        + font("AZAI is ready for verification, moderation, economy, media control, and clean community management.")
        + "\n\n"
        + font("Admin / Owner Notice:")
        + f" {admin_line}\n"
        + font("For no verification restriction on current members, run:")
        + " /verifyall\n"
        + font("For fresh verification for everyone, run:")
        + " /unverifyall\n\n"
        + font("Recommended Setup:")
        + "\n1. Make AZAI admin with delete, mute, invite-link and management permissions."
        + "\n2. Use /settings to configure group controls."
        + "\n3. Use /msettings to configure media controls."
        + "\n\n"
        + font("Media Control:")
        + " /setstartpic /setleaderpic /setitempic item_id /msettings"
        + "\n\n"
        + font("Powered By:")
        + " "
        + font("EGO Network - EST. 2026")
    )


async def group_join_welcome(event):
    try:
        me = await tbot.get_me()
        user = await event.get_user()
        users = list(event.users) if getattr(event, "users", None) else ([user] if user else [])
        if not any(int(getattr(u, "id", 0) or 0) == int(me.id) for u in users):
            return
        chat = await event.get_chat()
        title = getattr(chat, "title", None) or "this group"
        admins = await admin_mentions(event.chat_id)
        text = welcome_text(title, admins)
        media = await saved_pic()
        if media:
            await tbot.send_file(event.chat_id, media, caption=text, buttons=welcome_buttons())
        else:
            await tbot.send_message(event.chat_id, text, buttons=welcome_buttons())
    except Exception as exc:
        print(f"AZAI Group Welcome Error: {exc}")


async def group_welcome_callback(event):
    data = event.data.decode()
    if data == "azgw_close":
        try:
            await event.delete()
        except Exception:
            pass
        return
    if data == "azgw_settings":
        await event.answer("Run /settings in this group to configure AZAI controls.", alert=True)


if "azai_group_join_welcome" not in tbot.handlers_loaded:
    tbot.add_event_handler(group_join_welcome, events.ChatAction())
    tbot.add_event_handler(group_welcome_callback, events.CallbackQuery(pattern=b"^azgw_"))
    tbot.handlers_loaded.add("azai_group_join_welcome")
