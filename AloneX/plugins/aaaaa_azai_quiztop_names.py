from telethon import events

from AloneX import database, font, prefix_cmds, tbot

score_db = database["azai_anime_quiz_scores"]


async def name_for(uid):
    try:
        user = await tbot.get_entity(int(uid))
        name = getattr(user, "first_name", None) or getattr(user, "username", None) or "Unknown User"
        username = getattr(user, "username", None)
        return f"{name} (@{username})" if username else name
    except Exception:
        return "Unknown User"


async def quiztop_handler(event):
    rows = await score_db.find({}).sort("correct", -1).to_list(length=10)
    text = font("ANIME QUIZ TOP") + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    if not rows:
        text += font("No scores yet.")
    else:
        key = "user" + "_id"
        for index, row in enumerate(rows, 1):
            display = await name_for(row.get(key, 0) or 0)
            text += f"{index}. {display} - {row.get('correct', 0)} {font('correct')}\n"
    await event.reply(text)
    raise events.StopPropagation


if "aaaaa_azai_quiztop_names" not in tbot.handlers_loaded:
    tbot.add_event_handler(quiztop_handler, events.NewMessage(pattern=f"^{prefix_cmds}quiztop(?:@\\w+)?$", incoming=True))
    tbot.handlers_loaded.add("aaaaa_azai_quiztop_names")
