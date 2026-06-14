from telethon import events

from AloneX import database, font, prefix_cmds, tbot

score_db = database["azai_anime_quiz_scores"]


async def quiztop_single(event):
    rows = await score_db.find({}).sort("correct", -1).to_list(length=10)
    text = font("ANIME QUIZ TOP") + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    if not rows:
        text += font("No scores yet.")
    else:
        for i, row in enumerate(rows, 1):
            name = row.get("name") or row.get("username") or str(row.get("user_id"))
            text += f"{i}. {name} - {row.get('correct', 0)} {font('correct')}\n"
    await event.reply(text)
    raise events.StopPropagation


if "aa02_azai_quiztop_single" not in tbot.handlers_loaded:
    tbot.add_event_handler(quiztop_single, events.NewMessage(pattern=f"^{prefix_cmds}quiztop(?:@\\w+)?$", incoming=True))
    tbot.handlers_loaded.add("aa02_azai_quiztop_single")
