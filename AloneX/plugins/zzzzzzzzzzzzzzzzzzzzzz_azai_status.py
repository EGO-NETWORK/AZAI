# AZAI STATUS COMMAND
# EGO NETWORK · MR EGO
# OWNER-ONLY VPS/PRODUCTION HEALTH SNAPSHOT

import os
from datetime import datetime, timezone, timedelta
from pathlib import Path

from telethon import events

try:
    from zoneinfo import ZoneInfo
except Exception:
    ZoneInfo = None

try:
    from AloneX import tbot
except Exception:
    tbot = None


IST = ZoneInfo("Asia/Kolkata") if ZoneInfo else timezone(timedelta(hours=5, minutes=30))
ROOT = Path(__file__).resolve().parents[2]


def _ids_from_env(*keys: str) -> set[int]:
    ids: set[int] = set()
    for key in keys:
        raw = os.getenv(key, "")
        for part in str(raw).replace(",", " ").split():
            part = part.strip()
            if part.isdigit():
                ids.add(int(part))
    return ids


OWNER_IDS = _ids_from_env("OWNER_ID", "ALONE_OWNER_ID", "SUDO_USERS")
BHABHI_IDS = _ids_from_env("ALIZA_ID", "BHABHI_ID")


def _yes_no(value: bool) -> str:
    return "OK" if value else "MISSING"


def _mask(value: str | None) -> str:
    if not value:
        return "MISSING"
    value = str(value).strip()
    if len(value) <= 8:
        return "SET"
    return f"SET ({value[:4]}...{value[-4:]})"


def _env_any(*keys: str) -> str:
    for key in keys:
        value = os.getenv(key)
        if value:
            return value
    return ""


def _time_mood(now: datetime) -> str:
    hour = now.hour
    if 4 <= hour < 7:
        return "EARLY MORNING"
    if 7 <= hour < 11:
        return "MORNING"
    if 11 <= hour < 17:
        return "DAY WORK MODE"
    if 17 <= hour < 20:
        return "EVENING"
    if 20 <= hour < 23:
        return "NIGHT"
    return "LATE NIGHT"


def _festival_name(now: datetime) -> str:
    fixed = {
        "01-01": "NEW YEAR",
        "01-26": "REPUBLIC DAY",
        "08-15": "INDEPENDENCE DAY",
        "10-02": "GANDHI JAYANTI",
        "12-25": "CHRISTMAS",
    }
    manual = os.getenv("AZAI_TODAY_FESTIVAL", "").strip().upper()
    if manual:
        return manual
    return fixed.get(now.strftime("%m-%d"), "NONE")


def _exists(path: str) -> bool:
    try:
        return (ROOT / path).exists()
    except Exception:
        return False


def _line(label: str, value: str) -> str:
    return f"{label}: {value}"


def _status_text() -> str:
    now = datetime.now(IST)
    ai_key = _env_any("GROQ_API_KEY", "GQRI_API_KEY")
    db_url = _env_any("DB_URL", "MONGO_URL", "DATABASE_URL")
    db_url2 = _env_any("DB_URL2", "MONGO_URL2", "DATABASE_URL2")
    token = _env_any("TOKEN", "BOT_TOKEN")

    files = {
        "PERSONALITY": _exists("AloneX/plugins/zzzzzzzzzzzzzzzzzzzz_azai_strong_personality_patch.py"),
        "REACTIONS": _exists("AloneX/plugins/zzzzzzzzzzzzzzzzzzzzzz_azai_real_alive_reactions.py"),
        "EGO HUSTLE CORE": _exists("AloneX/plugins/zzzz_azai_ego_hustle_core.py"),
        "EGO HUSTLE ACTIONS": _exists("AloneX/plugins/zzzzzzzzzzzzzzzzzzzz_azai_ego_hustle_actions.py"),
        "DYNAMIC PROFILE": _exists("AloneX/plugins/zzzzzzzzzzzzzzzzzzzzz_azai_dynamic_profile_card.py"),
        "DYNAMIC LEADERBOARD": _exists("AloneX/plugins/zzzzzzzzzzzzzzzzzzzzz_azai_dynamic_leaderboard_card.py"),
        "ANIME QUIZ": _exists("AloneX/plugins/zzzzzzzzzzzzzzzzzzzz_azai_anime_quiz_auto.py"),
        "BROADCAST GUARD": _exists("AloneX/plugins/0000_azai_single_broadcast_guard.py"),
    }

    file_lines = "\n".join(_line(k, _yes_no(v)) for k, v in files.items())

    return (
        "AZAI STATUS REPORT\n"
        "EGO NETWORK · MR EGO\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"TIME: {now.strftime('%d %B %Y · %I:%M %p')} IST\n"
        f"MODE: {_time_mood(now)}\n"
        f"FESTIVAL: {_festival_name(now)}\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"BOT TOKEN: {_mask(token)}\n"
        f"AI KEY: {_mask(ai_key)}\n"
        f"DB_URL: {_mask(db_url)}\n"
        f"DB_URL2: {_mask(db_url2)}\n"
        f"OWNER IDS: {len(OWNER_IDS)} LOADED\n"
        f"BHABHI IDS: {len(BHABHI_IDS)} LOADED\n"
        f"LOG GROUP: {_mask(_env_any('LOG_GROUP_ID', 'LOGGER_ID', 'LOGS_CHANNEL'))}\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"{file_lines}\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "VPS READY CHECK: USE python -m compileall AloneX/plugins BEFORE START."
    )


async def _is_owner(event) -> bool:
    try:
        sender_id = int(getattr(event, "sender_id", 0) or 0)
        return bool(sender_id in OWNER_IDS)
    except Exception:
        return False


if tbot:
    @tbot.on(events.NewMessage(pattern=r"^/azstatus(?:@\w+)?$"))
    async def azai_status_handler(event):
        try:
            if OWNER_IDS and not await _is_owner(event):
                await event.reply("YE OWNER-ONLY STATUS HAI BHAI.")
                return
            await event.reply(_status_text())
        except Exception as exc:
            await event.reply(f"AZAI STATUS ERROR: {type(exc).__name__}")
