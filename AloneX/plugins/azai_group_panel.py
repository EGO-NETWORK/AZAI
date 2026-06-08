from telethon import Button, events

from AloneX import font, prefix_cmds, tbot

try:
    from AloneX.plugins.azai_group_gate import gate_db
except Exception:
    gate_db = None

BRAND = font("EGO Network - EST. 2026")


async def is_group_admin(event) -> bool:
    if event.is_private:
        await event.reply(font("This panel works only inside groups."))
        return False
    if event.is_channel and not event.is_group:
        return False
    try:
        sender = await event.get_sender()
        if getattr(sender, "bot", False):
            return True
        perms = await event.client.get_permissions(event.chat_id, sender.id)
        if getattr(perms, "is_admin", False) or getattr(perms, "is_creator", False):
            return True
    except Exception:
        pass
    await event.reply(font("Only group admins can open this panel."))
    return False


async def group_counts(chat_id: int) -> tuple[int, int]:
    if gate_db is None:
        return 0, 0
    verified = await gate_db.count_documents({"chat_id": chat_id, "done": True})
    unverified = await gate_db.count_documents({"chat_id": chat_id, "done": False})
    return verified, unverified


def group_home_text(chat_title: str, verified: int, unverified: int) -> str:
    return (
        font("AZAI GROUP PANEL") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Group:") + f" {chat_title}\n"
        + font("Verified Users:") + f" {verified}\n"
        + font("Known Unverified:") + f" {unverified}\n\n"
        + font("Use this panel to control group verification and basic settings.") + "\n\n"
        + font("Powered By:") + " " + BRAND
    )


def verification_text(verified: int, unverified: int) -> str:
    return (
        font("GROUP VERIFICATION STATUS") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Verified Users:") + f" {verified}\n"
        + font("Known Unverified:") + f" {unverified}\n\n"
        + font("Rule:") + " " + font("Unverified users can only send /verify before chatting.") + "\n"
        + font("Group-specific:") + " " + font("Yes, every group verifies separately.") + "\n\n"
        + font("Powered By:") + " " + BRAND
    )


def rules_text() -> str:
    return (
        font("AZAI GROUP RULES") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("1. Complete verification before chatting.") + "\n"
        + font("2. Do not spam links or repeated messages.") + "\n"
        + font("3. Respect group admins and members.") + "\n"
        + font("4. Profile setup is optional but recommended.") + "\n\n"
        + font("Custom rules editor is coming later.") + "\n\n"
        + font("Powered By:") + " " + BRAND
    )


def settings_text() -> str:
    return (
        font("GROUP SETTINGS") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Verification Lock:") + " " + font("Active") + "\n"
        + font("Anti-Spam:") + " " + font("Coming Soon") + "\n"
        + font("Warnings:") + " " + font("Coming Soon") + "\n"
        + font("Auto Quiz:") + " " + font("Coming Soon") + "\n"
        + font("Economy Rewards:") + " " + font("Coming Soon") + "\n\n"
        + font("Powered By:") + " " + BRAND
    )


def group_buttons():
    return [
        [Button.inline(font("Verification Status"), b"azgrp_verify_status")],
        [Button.inline(font("Verified Count"), b"azgrp_verified"), Button.inline(font("Unverified Count"), b"azgrp_unverified")],
        [Button.inline(font("Rules"), b"azgrp_rules"), Button.inline(font("Settings"), b"azgrp_settings")],
        [Button.inline(font("Close"), b"azgrp_close")],
    ]


def back_buttons():
    return [[Button.inline(font("Back"), b"azgrp_home"), Button.inline(font("Close"), b"azgrp_close")]]


async def group_panel_handler(event):
    if not await is_group_admin(event):
        return
    chat = await event.get_chat()
    title = getattr(chat, "title", None) or "Current Group"
    verified, unverified = await group_counts(event.chat_id)
    await event.reply(group_home_text(title, verified, unverified), buttons=group_buttons())


async def group_callback(event):
    sender = await event.get_sender()
    try:
        perms = await event.client.get_permissions(event.chat_id, sender.id)
        allowed = bool(getattr(perms, "is_admin", False) or getattr(perms, "is_creator", False))
    except Exception:
        allowed = False
    if not allowed:
        await event.answer(font("Only group admins can use this panel."), alert=True)
        return

    data = event.data.decode()
    verified, unverified = await group_counts(event.chat_id)
    if data == "azgrp_home":
        chat = await event.get_chat()
        title = getattr(chat, "title", None) or "Current Group"
        await event.edit(group_home_text(title, verified, unverified), buttons=group_buttons())
    elif data == "azgrp_verify_status":
        await event.edit(verification_text(verified, unverified), buttons=back_buttons())
    elif data == "azgrp_verified":
        await event.answer(font(f"Verified users: {verified}"), alert=True)
    elif data == "azgrp_unverified":
        await event.answer(font(f"Known unverified users: {unverified}"), alert=True)
    elif data == "azgrp_rules":
        await event.edit(rules_text(), buttons=back_buttons())
    elif data == "azgrp_settings":
        await event.edit(settings_text(), buttons=back_buttons())
    elif data == "azgrp_close":
        await event.delete()


if "azai_group_panel" not in tbot.handlers_loaded:
    tbot.add_event_handler(group_panel_handler, events.NewMessage(pattern=f"^{prefix_cmds}group$", incoming=True))
    tbot.add_event_handler(group_callback, events.CallbackQuery(pattern=b"^azgrp_"))
    tbot.handlers_loaded.add("azai_group_panel")
