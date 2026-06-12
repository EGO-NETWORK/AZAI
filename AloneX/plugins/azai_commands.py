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
        + "/logstatus - " + font("Check logger guard status") + "\n"
        + "/toneguard - " + font("Check AZAI tone mode") + "\n\n"
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
        + font("Group:") + "\n"
        + "/group\n/settings\n/setting\n/rules\n\n"
        + font("Verification:") + "\n"
        + "/verifyall\n/unverifyall\n/verified\n/unverified\n\n"
        + font("Owner:") + "\n"
        + "/owner\n\n"
        + font("Powered By:") + " " + BRAND
    )


def moderation_commands_text() -> str:
    return (
        font("MODERATION COMMANDS") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + "/mod - " + font("Open moderation panel") + "\n"
        + "/antilink on - " + font("Enable link protection") + "\n"
        + "/antilink off - " + font("Disable link protection") + "\n"
        + "/warn - " + font("Warn replied user") + "\n"
        + "/unwarn - " + font("Remove one warning from replied user") + "\n"
        + "/warnings - " + font("Check warnings") + "\n"
        + "/resetwarns - " + font("Reset replied user's warnings") + "\n"
        + "/mute - " + font("Mute replied user for 10 minutes") + "\n"
        + "/unmute - " + font("Unmute replied user") + "\n"
        + "/ban - " + font("Ban replied user") + "\n"
        + "/unban - " + font("Unban replied user") + "\n\n"
        + font("Use admin permissions properly. AZAI cannot moderate without admin rights.") + "\n\n"
        + font("Powered By:") + " " + BRAND
    )


def economy_commands_text() -> str:
    return (
        font("ECONOMY COMMANDS") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + "/wallet - " + font("Show your wallet") + "\n"
        + "/balance - " + font("Show your balance") + "\n"
        + "/daily - " + font("Claim 100 EC daily reward") + "\n"
        + "/send amount - " + font("Reply to a user and send credits with 3% fee") + "\n"
        + "/rep - " + font("Reply to a user and give daily REP") + "\n"
        + "/myrep - " + font("Show your REP") + "\n"
        + "/leaderboard - " + font("Open richest, XP, and REP leaderboard") + "\n"
        + "/inventory - " + font("Show saved inventory") + "\n"
        + "/refer - " + font("Referral system, coming next") + "\n"
        + "/redeemref - " + font("Redeem referral code, coming next") + "\n\n"
        + font("Currency:") + " EGO CREDIT (EC)\n"
        + font("Powered By:") + " " + BRAND
    )


def market_commands_text() -> str:
    return (
        font("MARKET COMMANDS") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + "/shop - " + font("Open market panel") + "\n"
        + "/garage - " + font("Show your bought cars and bikes") + "\n"
        + "/vault - " + font("Open rare and owner-gifted item vault") + "\n"
        + "/setcar item_id - " + font("Set active car") + "\n"
        + "/setbike item_id - " + font("Set active bike") + "\n"
        + "/gift item_name - " + font("Reply to a user and send a gift") + "\n\n"
        + font("Current market:") + "\n"
        + font("Cars, Bikes, Gifts, Boosters, Garage, Inventory, Vault") + "\n\n"
        + font("Powered By:") + " " + BRAND
    )


def events_commands_text() -> str:
    return (
        font("EVENT COMMANDS") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + "/events - " + font("Open event panel") + "\n"
        + "/birthday DD/MM - " + font("Save your birthday") + "\n"
        + "/birthdays - " + font("Show today's saved dates") + "\n"
        + "/todayevents - " + font("Show today's events and saved dates") + "\n"
        + "/addevent DD/MM | title | text - " + font("Owner: add event") + "\n"
        + "/delevent title - " + font("Owner: delete event") + "\n"
        + "/eventauto on | off | status - " + font("Owner: control auto wishes") + "\n\n"
        + font("Powered By:") + " " + BRAND
    )


def games_commands_text() -> str:
    return (
        font("GAME COMMANDS") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + "/games - " + font("Open game panel") + "\n"
        + "/dice - " + font("Free clean dice mini-game") + "\n"
        + "/dart - " + font("Free clean dart mini-game") + "\n"
        + "/basketball - " + font("Free clean basketball mini-game") + "\n\n"
        + font("Rule:") + " " + font("No betting, no wager, no unsafe game logic.") + "\n\n"
        + font("Powered By:") + " " + BRAND
    )


def media_commands_text() -> str:
    return (
        font("STICKER COMMANDS") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + "/stickerpack - " + font("Open sticker help") + "\n"
        + "/stickerpack add <pack> <mood> - " + font("Add mood pack") + "\n"
        + "/stickerpack remove <pack> - " + font("Remove pack") + "\n"
        + "/stickerpack list - " + font("Show saved packs") + "\n"
        + "/stickermood <mood> - " + font("Send random sticker from mood") + "\n\n"
        + font("Auto:") + " " + font("Sticker echo works when a user sends a sticker.") + "\n\n"
        + font("Powered By:") + " " + BRAND
    )


def coming_soon_text() -> str:
    return (
        font("COMING SOON") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Refer Earn Full Logic") + "\n"
        + font("Family Tree / Social Tree") + "\n"
        + font("Festival Auto Wishes") + "\n"
        + font("Full Owner Panel Actions") + "\n\n"
        + font("Powered By:") + " " + BRAND
    )


def command_buttons():
    return [
        [Button.inline(font("User"), b"azcmd_user"), Button.inline(font("Profile"), b"azcmd_profile")],
        [Button.inline(font("Verification"), b"azcmd_verify"), Button.inline(font("Admin"), b"azcmd_admin")],
        [Button.inline(font("Moderation"), b"azcmd_mod"), Button.inline(font("Economy"), b"azcmd_eco")],
        [Button.inline(font("Market"), b"azcmd_market"), Button.inline(font("Events"), b"azcmd_events")],
        [Button.inline(font("Games"), b"azcmd_games"), Button.inline(font("Stickers"), b"azcmd_media")],
        [Button.inline(font("Coming Soon"), b"azcmd_soon"), Button.inline(font("Close"), b"azcmd_close")],
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
    elif data == "azcmd_mod":
        await event.edit(moderation_commands_text(), buttons=back_buttons())
    elif data == "azcmd_eco":
        await event.edit(economy_commands_text(), buttons=back_buttons())
    elif data == "azcmd_market":
        await event.edit(market_commands_text(), buttons=back_buttons())
    elif data == "azcmd_events":
        await event.edit(events_commands_text(), buttons=back_buttons())
    elif data == "azcmd_games":
        await event.edit(games_commands_text(), buttons=back_buttons())
    elif data == "azcmd_media":
        await event.edit(media_commands_text(), buttons=back_buttons())
    elif data == "azcmd_soon":
        await event.edit(coming_soon_text(), buttons=back_buttons())
    elif data == "azcmd_close":
        await event.delete()


if "azai_commands" not in tbot.handlers_loaded:
    tbot.add_event_handler(commands_handler, events.NewMessage(pattern=f"^{prefix_cmds}commands$", incoming=True))
    tbot.add_event_handler(commands_callback, events.CallbackQuery(pattern=b"^azcmd_"))
    tbot.handlers_loaded.add("azai_commands")
