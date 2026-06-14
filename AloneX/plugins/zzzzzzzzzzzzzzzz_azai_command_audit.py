from telethon import events

from AloneX import font, prefix_cmds, tbot
from config import OWNER_ID


def owner_ids():
    try:
        owner = int(OWNER_ID)
        return {owner} if owner else set()
    except Exception:
        return set()


async def is_owner(event):
    sender = await event.get_sender()
    return bool(sender and int(sender.id) in owner_ids())


AUDIT_TEXT = """
AZAI COMMAND AUDIT
━━━━━━━━━━━━━━━━━━━━

PUBLIC CORE
/start
/help
/settings
/commands
/ping
/owner

PROFILE / IDENTITY
/religion <option>
/myreligion

ECONOMY / EGO HUSTLE
/hustle
/bal
/daily
/work
/protect
/luck
/leaderboard
/profile

FUN ZONE
/hug
/pat
/dance
/highfive
/cheer
Owner setup: /addfun, /funlist, /delfun

FESTIVAL / EVENTS
/festivals
/todayfestivals
Owner setup: /addfestival, /delfestival, /seedfestivals, /festivalauto, /loadcalendar, /loadcalendarfull, /calendarstatus, /calendarfullstatus

MEDIA / PANELS
Owner setup only: /msettings, /panelmedia, /setstartpic, /setitempic, /setleaderpic, /sethelppic, /setsettingspic, /seteconomypic, /setgamespic, /setfamilypic, /setquizpic, /setownerpic, /setcorepic

SECURITY / MODERATION
/verify
/verifyall
/unverifyall
/mod
/warn
/mute
/ban
/antilink

REACTION MODE
Auto reacts on friendly, soft, or rough messages.

OWNER IDENTITY
OWNER_ID only.
BHABHI_ID / ALIZA_ID supported.
""".strip()


async def cmdaudit(event):
    if not await is_owner(event):
        await event.reply(font("Owner only."))
        raise events.StopPropagation
    await event.reply(font(AUDIT_TEXT))
    raise events.StopPropagation


if "zzzzzzzzzzzzzzzz_azai_command_audit" not in tbot.handlers_loaded:
    tbot.add_event_handler(cmdaudit, events.NewMessage(pattern=f"^{prefix_cmds}cmdaudit(?:@\\w+)?$", incoming=True))
    tbot.handlers_loaded.add("zzzzzzzzzzzzzzzz_azai_command_audit")
