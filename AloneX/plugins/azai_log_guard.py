from telethon import events

import AloneX
from AloneX import font, prefix_cmds, tbot

try:
    import config
except Exception:
    config = None


def disable_public_log_targets() -> None:
    """Disable legacy public log targets for safer AZAI runtime behavior."""
    for target in (AloneX, config):
        if not target:
            continue
        for name, value in {
            "LOGS_CHANNEL": None,
            "LOG_GROUP_ID": 0,
            "LOGGER_ID": 0,
        }.items():
            try:
                setattr(target, name, value)
            except Exception:
                pass


def log_status_text() -> str:
    return (
        font("AZAI LOG GUARD") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Public log target:") + " " + font("Disabled") + "\n"
        + font("Normal user-message logging:") + " " + font("Blocked where legacy modules use shared config") + "\n"
        + font("Important logs:") + " " + font("Owner-safe mode pending") + "\n\n"
        + font("Powered By:") + " " + font("EGO Network - EST. 2026")
    )


async def logstatus_handler(event):
    if event.is_channel and not event.is_group:
        return
    await event.reply(log_status_text())


disable_public_log_targets()

if "azai_log_guard" not in tbot.handlers_loaded:
    tbot.add_event_handler(logstatus_handler, events.NewMessage(pattern=f"^{prefix_cmds}logstatus$", incoming=True))
    tbot.handlers_loaded.add("azai_log_guard")
