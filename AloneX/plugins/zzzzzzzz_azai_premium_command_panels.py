from telethon import Button

from AloneX import font
from AloneX.plugins import aaa_azai_start_pic as p


def line(cmd: str, desc: str) -> str:
    return f"{cmd} - {font(desc)}\n"


def core_text() -> str:
    return (
        font("CORE COMMANDS") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + line("/start", "Open the official AZAI start panel")
        + line("/help", "Open the command help menu")
        + line("/ping", "Check bot speed and system response")
        + line("/alive", "Check if AZAI is online")
        + line("/repo", "View project repository information")
    )


def economy_text() -> str:
    return (
        font("ECONOMY COMMANDS") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + line("/balance or /bal", "Check your current EC balance and XP")
        + line("/daily", "Claim your daily EC reward")
        + line("/work", "Earn EC through activity jobs")
        + line("/give amount", "Transfer EC to another user by reply")
        + line("/leaderboard", "See the richest players globally")
        + line("/profile", "View your EGO Hustle profile")
    )


def media_text() -> str:
    return (
        font("MEDIA COMMANDS") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + line("/setstartpic", "Set start and help panel media")
        + line("/setitempic item_id", "Attach media to shop items")
        + line("/setleaderpic", "Set leaderboard media card")
        + line("/msettings", "Open media setup guide")
    )


def owner_text() -> str:
    return (
        font("OWNER COMMANDS") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + line("/owner", "Open MR EGO owner control panel")
        + line("/settings", "Open group settings panel")
        + line("/msettings", "Open media settings panel")
        + line("/broadcast", "Send official broadcast")
        + line("/logstatus", "Check logger status")
        + line("/logon or /logoff", "Control private logger")
    )


def family_text() -> str:
    return (
        font("FAMILY COMMANDS") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + line("/brother", "Send brother relation request")
        + line("/sister", "Send sister relation request")
        + line("/adopt", "Send adoption relation request")
        + line("/family", "View your family list")
        + line("/familytree", "Open family tree view")
        + line("/leavefamily", "Leave current family relation")
    )


def games_text() -> str:
    return (
        font("GAME COMMANDS") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + line("/hustle", "Open EGO Hustle game panel")
        + line("/dice", "Play Telegram dice game")
        + line("/dart", "Play dart mini game")
        + line("/basketball", "Play basketball mini game")
        + line("/slot", "Play slot mini game")
    )


def help_text() -> str:
    return (
        font("AZAI COMMAND CENTER") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Choose a command category below.") + "\n"
        + font("Every panel shows command usage with short professional details.")
    )


def help_buttons():
    return [
        [Button.inline(font("Core"), b"azai_help_core"), Button.inline(font("Owner"), b"azai_help_owner")],
        [Button.inline(font("Economy"), b"azai_help_economy"), Button.inline(font("Games"), b"azai_help_games")],
        [Button.inline(font("Family"), b"azai_help_family"), Button.inline(font("Media"), b"azai_help_media")],
        [Button.inline(font("System"), b"azai_system_stats"), Button.inline(font("Back"), b"azai_start_home")],
        [Button.inline(font("Close"), b"azai_close_panel")],
    ]


p.core_text = core_text
p.economy_text = economy_text
p.media_text = media_text
p.owner_text = owner_text
p.family_text = family_text
p.games_text = games_text
p.help_text = help_text
p.help_buttons = help_buttons
