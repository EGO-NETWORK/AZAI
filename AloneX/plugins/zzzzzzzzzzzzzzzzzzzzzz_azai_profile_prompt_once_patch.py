import time

from telethon import Button, events

from AloneX import font
from AloneX.plugins import azai_ai_chat as ai


async def ask_profile_mode_once(event):
    sender = await event.get_sender()
    if not sender:
        return

    # Save neutral fallback immediately so AZAI asks only once.
    # If user clicks a button, profile_mode_callback will overwrite this with the selected mode.
    await ai.profile_db.update_one(
        {"user_id": int(sender.id)},
        {
            "$set": {
                "user_id": int(sender.id),
                "mode": "neutral",
                "profile_prompted": True,
                "updated_at": int(time.time()),
            }
        },
        upsert=True,
    )

    buttons = [[
        Button.inline(font("Bhai Mode"), b"azai_ai_profile_male"),
        Button.inline(font("Ma'am Mode"), b"azai_ai_profile_female"),
    ], [
        Button.inline(font("Neutral"), b"azai_ai_profile_neutral"),
        Button.inline(font("Skip"), b"azai_ai_profile_skip"),
    ]]

    await event.reply(
        font("Profile tone clear nahi hai. Ek baar mode choose kar do, phir AZAI repeat nahi puchega."),
        buttons=buttons,
    )
    raise events.StopPropagation


# Patch the actual AI chat module's profile prompt function.
ai.ask_profile_mode = ask_profile_mode_once
