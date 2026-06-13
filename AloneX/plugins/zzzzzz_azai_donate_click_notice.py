from telethon import events

from AloneX import font, tbot

PATCH_FLAG = "zzzzzz_azai_donate_click_notice"


async def donate_click_notice(event):
    await event.answer(font("Telegram Stars donate setup is being prepared. Minimum: 10 Stars."), alert=True)
    raise events.StopPropagation


if PATCH_FLAG not in getattr(tbot, "handlers_loaded", set()):
    tbot.add_event_handler(donate_click_notice, events.CallbackQuery(pattern=b"^azai_donate_stars_10$"))
    tbot.handlers_loaded.add(PATCH_FLAG)
