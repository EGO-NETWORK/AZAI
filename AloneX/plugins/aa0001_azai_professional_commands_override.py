from telethon import Button, events

from AloneX import font, prefix_cmds, tbot

COMMAND_TEXT = """
AZAI COMMANDS
━━━━━━━━━━━━━━━━━━━━

CORE
/start - Open AZAI start panel.
/help - Open help menu.
/commands - Show this command guide.
/ping - Check bot speed/status.
/owner - Show official owner info.
/settings - Open group settings panel.

ECONOMY / EGO HUSTLE
/hustle - Open premium economy game panel.
/bal - Check your EC balance.
/bal reply - Check another member balance.
/daily - Claim daily EC reward.
/work - Work and earn EC.
/raid reply - Raid another user's wallet.
/protect - Buy wallet protection.
/luck - Try a luck reward.
/heist - High risk EC game.
/leaderboard - Show top users.
/profile - Show your game profile.

GAMES
/dice - Roll a dice and get score.
/dart - Throw a dart and get score.
/basketball - Take a shot and get score.
/slot - Spin symbols for fun.

FUN ZONE
/hug reply - Send a friendly hug.
/pat reply - Cheer someone up.
/dance reply - Start a fun dance vibe.
/highfive reply - Give a high-five.
/cheer reply - Send good energy.

FESTIVALS
/religion <option> - Save your festival preference.
/myreligion - Check saved preference.
/festivals - Show saved festivals.
/todayfestivals - Show today's festivals.

OWNER TOOLS
/msettings - Owner media/settings panel.
/panelmedia - Panel media guide.
/cmdaudit - Owner command audit.
/loadcalendarfull YEAR - Load fixed-date festival pack.
/festivalauto on/off/now - Control festival auto wishes.

NOTE
Some commands need reply-to-user. Use /help for panels.
""".strip()


def command_buttons():
    return [[Button.inline(font("Help Menu"), b"azai_start_help"), Button.inline(font("Close"), b"azai_close_panel")]]


async def commands_override(event):
    await event.reply(font(COMMAND_TEXT), buttons=command_buttons())
    raise events.StopPropagation


if "aa0001_azai_professional_commands_override" not in tbot.handlers_loaded:
    tbot.add_event_handler(commands_override, events.NewMessage(pattern=f"^{prefix_cmds}(commands|cmds|helpme)(?:@\\w+)?$", incoming=True))
    tbot.handlers_loaded.add("aa0001_azai_professional_commands_override")
