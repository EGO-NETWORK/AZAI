from telethon import Button, events

from AloneX import font, prefix_cmds, tbot

BRAND = font("EGO Network - EST. 2026")


def home_text():
    return (
        font("AZAI COMMAND CENTER") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Choose a category below to see commands.") + "\n"
        + font("All current and planned AZAI sections are organized here.") + "\n\n"
        + font("Powered By:") + " " + BRAND
    )


PAGES = {
    "core": "CORE COMMANDS\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n/start - Open start panel\n/help - Open help menu\n/commands - Open command center\n/group - Open group panel\n/settings - Open settings\n/rules - Show group rules",
    "profile": "PROFILE COMMANDS\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n/setup - Create profile\n/profile - Show saved profile\n/setname - Save name\n/setgender - Save gender option\n/setbirthday - Save birthday\n/setreligion - Save preference option",
    "verify": "VERIFY COMMANDS\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n/verify - Verify yourself\n/verifyall - Admin group verify\n/unverifyall - Admin reset verify\n/verified - Show verified count\n/unverified - Show unverified count",
    "mod": "MODERATION COMMANDS\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n/mod - Open moderation panel\n/antilink on/off - Toggle link guard\n/warn - Warn replied user\n/unwarn - Remove warning\n/warnings - Check warnings\n/resetwarns - Reset warnings\n/mute - Mute replied user\n/unmute - Unmute replied user\n/ban - Ban replied user\n/unban - Unban replied user",
    "eco": "ECONOMY COMMANDS\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n/wallet - Show wallet\n/balance - Show balance\n/daily - Claim daily EC\n/send amount - Send EC by reply\n/rep - Give daily REP\n/myrep - Show REP\n/leaderboard - Show leaderboard\n/inventory - Show inventory\n/refer - Create referral code\n/redeemref CODE - Redeem referral code",
    "market": "MARKET COMMANDS\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n/shop - Open market\n/garage - Show vehicles\n/vault - Open vault\n/setcar item_id - Set active car\n/setbike item_id - Set active bike\n/gift item_name - Gift by reply",
    "family": "FAMILY COMMANDS\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n/brother - Send brother link request\n/sister - Send sister link request\n/adopt - Send member link request\n/family - Show saved links\n/familytree - Show profile buttons\n/leavefamily - Remove saved family links",
    "stickers": "STICKER COMMANDS\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n/stickerpack - Manage sticker packs\n/stickerpack add pack mood - Add mood pack\n/stickerpack remove pack - Remove pack\n/stickerpack list - Show saved packs\n/stickermood mood - Random sticker from mood",
    "quiz": "QUIZ COMMANDS\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n/animeguess - Anime guess quiz\n/quiz - Quiz panel\n/quizon - Enable auto quiz\n/quizoff - Disable auto quiz\n/quizstats - Show quiz stats",
    "events": "EVENT COMMANDS\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n/events - Open event panel\n/birthday - Birthday setup/status\n/setbirthday DD/MM - Save birthday\n/todayevents - Show today's events\n/eventon - Enable event wishes\n/eventoff - Disable event wishes",
    "ai": "AI COMMANDS\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\nDM - Chat directly with AZAI\nGroup - Mention AZAI or reply to AZAI\n/aistatus - Check AI status\n/toneguard - Check tone guard",
    "owner": "OWNER COMMANDS\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n/owner - Open owner panel\n/logstatus - Check log guard",
}


def home_buttons():
    return [
        [Button.inline(font("Core"), b"aznew_core"), Button.inline(font("Profile"), b"aznew_profile")],
        [Button.inline(font("Verify"), b"aznew_verify"), Button.inline(font("Moderation"), b"aznew_mod")],
        [Button.inline(font("Economy"), b"aznew_eco"), Button.inline(font("Market"), b"aznew_market")],
        [Button.inline(font("Family"), b"aznew_family"), Button.inline(font("Stickers"), b"aznew_stickers")],
        [Button.inline(font("Quiz"), b"aznew_quiz"), Button.inline(font("Events"), b"aznew_events")],
        [Button.inline(font("AI"), b"aznew_ai"), Button.inline(font("Owner"), b"aznew_owner")],
        [Button.inline(font("Close"), b"aznew_close")],
    ]


def back_buttons():
    return [[Button.inline(font("Back"), b"aznew_home"), Button.inline(font("Close"), b"aznew_close")]]


async def new_commands_handler(event):
    await event.reply(home_text(), buttons=home_buttons())
    raise events.StopPropagation


async def new_commands_callback(event):
    data = event.data.decode().replace("aznew_", "", 1)
    if data == "home":
        await event.edit(home_text(), buttons=home_buttons())
        return
    if data == "close":
        await event.delete()
        return
    text = PAGES.get(data)
    if text:
        await event.edit(font(text) + "\n\n" + font("Powered By:") + " " + BRAND, buttons=back_buttons())


if "aaa_azai_commands_menu" not in tbot.handlers_loaded:
    tbot.add_event_handler(new_commands_handler, events.NewMessage(pattern=f"^{prefix_cmds}commands(?:@\\w+)?$", incoming=True))
    tbot.add_event_handler(new_commands_callback, events.CallbackQuery(pattern=b"^aznew_"))
    tbot.handlers_loaded.add("aaa_azai_commands_menu")
