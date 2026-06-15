from telethon import events

from AloneX import font, prefix_cmds, tbot
from config import OWNER_ID

ABUSE_PARTS = ("madar", "bhos", "bsdk", "chuti", "gali")
SHORT_TEXT = {
    "hi": "Haan, bol. Kya kaam hai?",
    "hello": "Haan, main yahin hoon. Kaam batao.",
    "hu": "Haan, samjha. Ab kaam batao.",
    "hmm": "Seedha bolo, kya karna hai?",
    "j": "Haan, clear. Next batao.",
    "ok": "Done. Next?",
}


def is_owner_id(user_id):
    try:
        return int(user_id) == int(OWNER_ID)
    except Exception:
        return False


async def tone_guard(event):
    text = (event.raw_text or "").strip()
    if not text or text[0] in prefix_cmds:
        return
    low = text.lower()
    if any(part in low for part in ABUSE_PARTS):
        await event.reply(font("Gaali nahi. Kaam batao, main solve karta hoon."))
        raise events.StopPropagation
    key = low.replace(".", "").replace("!", "").strip()
    if key in SHORT_TEXT:
        reply = SHORT_TEXT[key]
        if is_owner_id(event.sender_id):
            reply = "MR EGO, " + reply
        await event.reply(font(reply))
        raise events.StopPropagation


if "aa0002_azai_ai_reply_tone_guard" not in tbot.handlers_loaded:
    tbot.add_event_handler(tone_guard, events.NewMessage(incoming=True))
    tbot.handlers_loaded.add("aa0002_azai_ai_reply_tone_guard")
