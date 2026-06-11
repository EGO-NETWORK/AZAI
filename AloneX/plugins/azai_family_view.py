from telethon import Button, events

from AloneX import database, font, prefix_cmds, tbot

BRAND = font("EGO Network - EST. 2026")
family_db = database["azai_family_tree"]
name_db = database["azai_identity_cache"]

LINK_LABELS = {
    "brother": "Brother Link",
    "sister": "Sister Link",
    "adopt": "Adopted Member Link",
}


def profile_url(user_id: int) -> str:
    return f"tg://user?id={int(user_id)}"


async def display_name(user_id: int) -> str:
    user_id = int(user_id)
    name = "Unknown User"
    username = None
    try:
        user = await tbot.get_entity(user_id)
        name = getattr(user, "first_name", None) or getattr(user, "username", None) or name
        username = getattr(user, "username", None)
        await name_db.update_one({"user_id": user_id}, {"$set": {"user_id": user_id, "name": name, "username": username}}, upsert=True)
    except Exception:
        data = await name_db.find_one({"user_id": user_id})
        if data:
            name = data.get("name") or name
            username = data.get("username")
    if username:
        return f"{name} (@{username})"
    return name


def build_profile_buttons(links: list):
    rows = []
    row = []
    for item in links[:10]:
        label = item.get("label", "Profile")
        user_id = int(item.get("user_id"))
        row.append(Button.url(font(label), profile_url(user_id)))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    return rows or None


async def familytree_handler(event):
    if event.is_private:
        await event.reply(font("Use /familytree inside a group."))
        return
    sender = await event.get_sender()
    rows = family_db.find({"chat_id": int(event.chat_id), "$or": [{"user_a": int(sender.id)}, {"user_b": int(sender.id)}]})
    text = font("FAMILY TREE") + "\n" + "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    links = []
    count = 0
    async for row in rows:
        other = row["user_b"] if int(row.get("user_a")) == int(sender.id) else row["user_a"]
        label = LINK_LABELS.get(row.get("link_type"), "Saved Link")
        text += f"• {label}: {await display_name(other)}\n"
        links.append({"label": label, "user_id": int(other)})
        count += 1
    if count == 0:
        text += font("No saved links yet.")
    else:
        text += "\n" + font("Tap profile buttons below to view linked users and their PFP.")
    text += "\n\n" + font("Powered By:") + " " + BRAND
    await event.reply(text, buttons=build_profile_buttons(links), link_preview=False)


if "azai_family_view" not in tbot.handlers_loaded:
    tbot.add_event_handler(familytree_handler, events.NewMessage(pattern=f"^{prefix_cmds}familytree(?:@\\w+)?$", incoming=True))
    tbot.handlers_loaded.add("azai_family_view")
