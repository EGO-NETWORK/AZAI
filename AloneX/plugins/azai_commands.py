from telethon import Button, events

from AloneX import font, prefix_cmds, tbot


BRAND = font("EGO Network - EST. 2026")


def commands_home_text() -> str:
    return (
        font("AZAI COMMAND CENTER") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Choose a command section below.") + "\n"
        + font("Owner-only commands are hidden from public help.") + "\n\n"
        + font("Powered By:") + " " + BRAND
    )


def user_commands_text() -> str:
    return (
        font("USER COMMANDS") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + "/start - " + font("Open AZAI start panel") + "\n"
        + "/help - " + font("Open help menu") + "\n"
        + "/commands - " + font("Open command center") + "\n"
        + "/aistatus - " + font("Check AI key status safely") + "\n"
        + "/logstatus - " + font("Check logger guard status") + "\n\n"
        + font("Powered By:") + " " + BRAND
    )


def profile_commands_text() -> str:
    return (
        font("PROFILE COMMANDS") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + "/setup - " + font("Open profile setup") + "\n"
        + "/profile - " + font("Show your saved profile") + "\n"
        + "/setname Your Name - " + font("Save your name") + "\n"
        + "/setgender male/female/skip - " + font("Save gender option") + "\n"
        + "/setbirthday DD/MM - " + font("Save real birthday date") + "\n"
        + "/setreligion option - " + font("Save preference option") + "\n\n"
        + font("Rule:") + " " + font("AZAI never auto-detects personal profile data.") + "\n\n"
        + font("Powered By:") + " " + BRAND
    )


def verification_commands_text() -> str:
    return (
        font("VERIFICATION COMMANDS") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + "/verify - " + font("Verify yourself in current group") + "\n"
        + "/verified - " + font("Admin: show verified count") + "\n"
        + "/unverified - " + font("Admin: show known unverified count") + "\n"
        + "/verifyall - " + font("Admin: mark current group members verified") + "\n"
        + "/unverifyall - " + font("Admin: force known members to verify again") + "\n\n"
        + font("Rule:") + " " + font("Every group has separate verification.") + "\n\n"
        + font("Powered By:") + " " + BRAND
    )


def admin_commands_text() -> str:
    return (
        font("ADMIN COMMANDS") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Currently active:") + "\n"
        + "/verifyall\n"
        + "/unverifyall\n"
        + "/verified\n"
        + "/unverified\n\n"
        + font("Coming next:") + "\n"
        + "/group\n"
        + "/settings\n"
        + "/rules\n\n"
        + font("Powered By:") + " " + BRAND
    )


def coming_soon_text() -> str:
    return (
        font("COMING SOON") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("AI Chat Base") + "\n"
        + font("Economy Base") + "\n"
        + font("Shop And Vault Base") + "\n"
        + font("Anime Quiz And GK Quiz") + "\n"
        + font("Birthday And Festival System") + "\n"
        + font("Owner Panel And Group Panel") + "\n\n"
        + font("Images, banners, items, and economy names will be added only after owner approval.") + "\n\n"
        + font("Powered By:") + " " + BRAND
    )


def command_buttons():
    return [
        [Button.inline(font("User"), b"azcmd_user"), Button.inline(font("Profile"), b"azcmd_profile")],
        [Button.inline(font("Verification"), b"azcmd_verify"), Button.inline(font("Admin"), b"azcmd_admin")],
        [Button.inline(font("Coming Soon"), b"azcmd_soon")],
        [Button.inline(font("Close"), b"azcmd_close")],
    ]


def back_buttons():
    return [[Button.inline(font("Back"), b"azcmd_home"), Button.inline(font("Close"), b"azcmd_close")]]


async def commands_handler(event):
    if event.is_channel and not event.is_group:
        return
    await event.reply(commands_home_text(), buttons=command_buttons())


async def commands_callback(event):
    data = event.data.decode()
    if data == "azcmd_home":
        await event.edit(commands_home_text(), buttons=command_buttons())
    elif data == "azcmd_user":
        await event.edit(user_commands_text(), buttons=back_buttons())
    elif data == "azcmd_profile":
        await event.edit(profile_commands_text(), buttons=back_buttons())
    elif data == "azcmd_verify":
        await event.edit(verification_commands_text(), buttons=back_buttons())
    elif data == "azcmd_admin":
        await event.edit(admin_commands_text(), buttons=back_buttons())
    elif data == "azcmd_soon":
        await event.edit(coming_soon_text(), buttons=back_buttons())
    elif data == "azcmd_close":
        await event.delete()


if "azai_commands" not in tbot.handlers_loaded:
    tbot.add_event_handler(commands_handler, events.NewMessage(pattern=f"^{prefix_cmds}commands$", incoming=True))
    tbot.add_event_handler(commands_callback, events.CallbackQuery(pattern=b"^azcmd_"))
    tbot.handlers_loaded.add("azai_commands")
