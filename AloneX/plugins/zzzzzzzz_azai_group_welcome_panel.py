"""AZAI group add welcome panel.

Sends a professional setup message with the saved start media whenever AZAI is
added to a group.
"""

from telethon import Button, events

from AloneX import font, tbot
from AloneX.plugins import aaa_azai_start_pic as start_panel

SUPPORT_LINK = "https://t.me/EGOxSUPPORT"
UPDATE_LINK = "https://t.me/EGOxUPDATES"


def mention_plain(user) -> str:
    if not user:
        return "Group Admin"
    username = getattr(user, "username", None)
    if username:
        return f"@{username}"
    return getattr(user, "first_name", None) or "Group Admin"


def welcome_buttons():
    return [
        [Button.url(font("Support"), SUPPORT_LINK), Button.url(font("Updates"), UPDATE_LINK)],
        [Button.inline(font("Settings"), b"azgw_settings"), Button.inline(font("Close"), b"azgw_close")],
    ]


def welcome_text(admin_name: str) -> str:
    return (
        font("AZAI HAS JOINED YOUR GROUP")
        + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + f"{admin_name}, "
        + font("thank you for adding AZAI to your group.")
        + "\n\n"
        + font("AZAI is ready to help with verification, moderation, economy, media, and clean group management.")
        + "\n\n"
        + font("Recommended setup:")
        + "\n1. "
        + font("Make AZAI admin with delete, mute, ban, and invite permissions.")
        + "\n2. "
        + font("Use")
        + " /settings "
        + font("to configure group controls.")
        + "\n3. "
        + font("If you do not want existing members blocked by verification, run")
        + " /verifyall"
        + "\n4. "
        + font("If you want everyone to verify again, run")
        + " /unverifyall"
        + "\n\n"
        + font("Owner media controls:")
        + " /setstartpic /setleaderpic /setitempic item_id /msettings"
        + "\n\n"
        + font("Powered By:")
        + " "
        + font("EGO Network - EST. 2026")
    )


async def send_welcome(chat_id: int, text: str):
    pic = await start_panel.saved_pic()
    if pic:
        await tbot.send_file(chat_id, pic, caption=text, buttons=welcome_buttons())
    else:
        await tbot.send_message(chat_id, text, buttons=welcome_buttons())


async def group_welcome_handler(event):
    try:
        me = await tbot.get_me()
        user = await event.get_user()
        users = list(event.users) if getattr(event, "users", None) else ([user] if user else [])
        if not any(int(getattr(u, "id", 0)) == int(me.id) for u in users):
            return
        added_by = None
        try:
            added_by = await event.get_added_by()
        except Exception:
            pass
        await send_welcome(event.chat_id, welcome_text(mention_plain(added_by)))
    except Exception as e:
        print(f"AZAI Group Welcome Error: {e}")


async def group_welcome_callback(event):
    data = event.data.decode()
    if data == "azgw_close":
        try:
            await event.delete()
        except Exception:
            pass
        return
    if data == "azgw_settings":
        await event.answer(
            font("Admins/Owner: use /settings in this group. Use /verifyall to allow current members without verification, or /unverifyall to make them verify again."),
            alert=True,
        )


if "azai_group_welcome_panel" not in tbot.handlers_loaded:
    tbot.add_event_handler(group_welcome_handler, events.ChatAction())
    tbot.add_event_handler(group_welcome_callback, events.CallbackQuery(pattern=b"^azgw_"))
    tbot.handlers_loaded.add("azai_group_welcome_panel")
