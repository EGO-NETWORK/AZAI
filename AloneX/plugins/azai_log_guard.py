from telethon import events

import AloneX
from AloneX import font, prefix_cmds, tbot

try:
    import config
except Exception:
    config = None


def owner_ids() -> set[int]:
    ids = set()
    for name in ("ALONE_OWNER_ID", "OWNER_ID"):
        for target in (config, AloneX):
            if not target:
                continue
            try:
                value = int(getattr(target, name, 0) or 0)
                if value:
                    ids.add(value)
            except Exception:
                pass
    return ids


async def is_owner(event) -> bool:
    sender = await event.get_sender()
    return bool(sender and int(sender.id) in owner_ids())


def set_log_state(enabled: bool) -> None:
    for target in (AloneX, config):
        if not target:
            continue
        try:
            setattr(target, "AZAI_LOGGER_ENABLED", bool(enabled))
        except Exception:
            pass


def log_target_status() -> str:
    values = []
    for target in (config, AloneX):
        if not target:
            continue
        for name in ("LOG_GROUP_ID", "LOGS_CHANNEL", "LOGGER_ID"):
            try:
                value = getattr(target, name, None)
                if value:
                    values.append(f"{name}: Set")
            except Exception:
                pass
    return "\n".join(values) if values else "No log target set in config/env"


def log_status_text() -> str:
    return (
        font("AZAI LOGGER") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Access:") + " " + font("Owner Only") + "\n"
        + font("Owner control:") + " /logon /logoff /logstatus\n"
        + font("Targets:") + "\n" + log_target_status() + "\n\n"
        + font("Powered By:") + " " + font("EGO Network - EST. 2026")
    )


async def logstatus_handler(event):
    if event.is_channel and not event.is_group:
        return
    if not await is_owner(event):
        await event.reply(font("Owner only."))
        raise events.StopPropagation
    await event.reply(log_status_text())
    raise events.StopPropagation


async def logon_handler(event):
    if not await is_owner(event):
        await event.reply(font("Owner only."))
        raise events.StopPropagation
    set_log_state(True)
    await event.reply(font("Logger allowed. Make sure LOG_GROUP_ID is numeric in env/config."))
    raise events.StopPropagation


async def logoff_handler(event):
    if not await is_owner(event):
        await event.reply(font("Owner only."))
        raise events.StopPropagation
    set_log_state(False)
    await event.reply(font("Logger disabled by owner switch."))
    raise events.StopPropagation


if "azai_log_guard" not in tbot.handlers_loaded:
    tbot.add_event_handler(logstatus_handler, events.NewMessage(pattern=f"^{prefix_cmds}logstatus(?:@\\w+)?$", incoming=True))
    tbot.add_event_handler(logon_handler, events.NewMessage(pattern=f"^{prefix_cmds}logon(?:@\\w+)?$", incoming=True))
    tbot.add_event_handler(logoff_handler, events.NewMessage(pattern=f"^{prefix_cmds}logoff(?:@\\w+)?$", incoming=True))
    tbot.handlers_loaded.add("azai_log_guard")
