import os
from telethon import events

from AloneX import font, prefix_cmds, tbot

try:
    from config import GROQ_API_KEY
except Exception:
    GROQ_API_KEY = None


def _has_value(value: str | None) -> bool:
    if not value:
        return False
    value = str(value).strip()
    if not value:
        return False
    return value.lower() not in {"0", "none", "null", "false", "your_groq_key", "your_groq_api_key"}


def ai_status_text() -> str:
    groq_key = GROQ_API_KEY or os.getenv("GROQ_API_KEY") or os.getenv("GQRI_API_KEY")
    configured = _has_value(groq_key)

    status = "Configured" if configured else "Missing"
    brain = "AI chat can be connected." if configured else "Add Groq key in hosting secrets first."

    return (
        font("❂ AZAI AI STATUS") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Provider:") + " Groq\n"
        + font("Key Status:") + f" {status}\n"
        + font("Secret Safety:") + " Hidden\n\n"
        + font("Result:") + f" {brain}\n\n"
        + font("Powered By:") + " EGO Network - EST. 2026"
    )


async def ai_status_handler(event):
    if event.is_channel and not event.is_group:
        return
    if event.fwd_from:
        return
    await event.reply(ai_status_text())


if "azai_ai_status" not in tbot.handlers_loaded:
    tbot.add_event_handler(
        ai_status_handler,
        events.NewMessage(pattern=f"^{prefix_cmds}aistatus$", incoming=True),
    )
    tbot.handlers_loaded.add("azai_ai_status")
