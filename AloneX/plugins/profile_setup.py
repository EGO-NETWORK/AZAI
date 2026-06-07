import re
from datetime import datetime

import pytz
from telethon import Button, events

from AloneX import database, font, prefix_cmds, tbot

IST = pytz.timezone("Asia/Kolkata")
profiles = database["azai_profiles"]

GENDERS = {"male", "female", "skip"}
RELIGIONS = {"hindu", "muslim", "christian", "sikh", "buddhist", "jain", "other", "skip"}


def now_ist() -> str:
    return datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S")


def clean_value(value: str, limit: int = 40) -> str:
    value = " ".join(str(value).strip().split())
    return value[:limit]


def valid_birthday(value: str) -> bool:
    return bool(re.match(r"^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])$", value))


async def get_profile(user_id: int) -> dict:
    data = await profiles.find_one({"user_id": user_id})
    return data or {}


async def update_profile(user_id: int, **fields):
    fields["updated_at"] = now_ist()
    await profiles.update_one(
        {"user_id": user_id},
        {"$set": fields, "$setOnInsert": {"user_id": user_id, "created_at": now_ist()}},
        upsert=True,
    )


def setup_text(data: dict | None = None) -> str:
    data = data or {}
    name = data.get("name", "Not Set")
    gender = data.get("gender", "Not Set")
    birthday = data.get("birthday", "Not Set")
    religion = data.get("religion", "Not Set")
    return (
        font("❂ AZAI PROFILE SETUP") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Name:") + f" {name}\n"
        + font("Gender:") + f" {gender}\n"
        + font("Birthday:") + f" {birthday}\n"
        + font("Preference:") + f" {religion}\n\n"
        + font("Commands:") + "\n"
        + "/setname Your Name\n"
        + "/setbirthday DD/MM\n"
        + "/setgender male/female/skip\n"
        + "/setreligion hindu/muslim/christian/sikh/buddhist/jain/other/skip\n\n"
        + font("Powered By:") + " EGO Network - EST. 2026"
    )


def profile_text(user, data: dict) -> str:
    fallback_name = getattr(user, "first_name", None) or getattr(user, "username", None) or "User"
    name = data.get("name") or fallback_name
    gender = data.get("gender", "Not Set")
    birthday = data.get("birthday", "Not Set")
    religion = data.get("religion", "Not Set")
    updated = data.get("updated_at", "Not Set")
    return (
        font("❂ AZAI PROFILE") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Name:") + f" {name}\n"
        + font("User ID:") + f" {user.id}\n"
        + font("Username:") + f" @{user.username if user.username else 'Not Set'}\n"
        + font("Gender:") + f" {gender}\n"
        + font("Birthday:") + f" {birthday}\n"
        + font("Preference:") + f" {religion}\n"
        + font("Updated:") + f" {updated}\n\n"
        + font("Powered By:") + " EGO Network - EST. 2026"
    )


def setup_buttons():
    return [
        [Button.inline(font("Male"), b"azai_gender_male"), Button.inline(font("Female"), b"azai_gender_female")],
        [Button.inline(font("Prefer Not To Say"), b"azai_gender_skip")],
        [Button.inline(font("Religion Menu"), b"azai_religion_menu")],
        [Button.inline(font("Close"), b"azai_profile_close")],
    ]


def religion_buttons():
    return [
        [Button.inline(font("Hindu"), b"azai_religion_hindu"), Button.inline(font("Muslim"), b"azai_religion_muslim")],
        [Button.inline(font("Christian"), b"azai_religion_christian"), Button.inline(font("Sikh"), b"azai_religion_sikh")],
        [Button.inline(font("Buddhist"), b"azai_religion_buddhist"), Button.inline(font("Jain"), b"azai_religion_jain")],
        [Button.inline(font("Other"), b"azai_religion_other"), Button.inline(font("Skip"), b"azai_religion_skip")],
        [Button.inline(font("Back"), b"azai_profile_back")],
    ]


async def setup_handler(event):
    if event.is_channel and not event.is_group:
        return
    user = await event.get_sender()
    data = await get_profile(user.id)
    await event.reply(setup_text(data), buttons=setup_buttons())


async def profile_handler(event):
    if event.is_channel and not event.is_group:
        return
    user = await event.get_sender()
    data = await get_profile(user.id)
    await event.reply(profile_text(user, data))


async def setname_handler(event):
    user = await event.get_sender()
    parts = event.raw_text.split(maxsplit=1)
    if len(parts) < 2:
        await event.reply(font("Use: /setname Your Name"))
        return
    name = clean_value(parts[1], 35)
    await update_profile(user.id, name=name)
    data = await get_profile(user.id)
    await event.reply(setup_text(data), buttons=setup_buttons())


async def setbirthday_handler(event):
    user = await event.get_sender()
    parts = event.raw_text.split(maxsplit=1)
    if len(parts) < 2 or not valid_birthday(parts[1].strip()):
        await event.reply(font("Use birthday format: /setbirthday DD/MM"))
        return
    birthday = parts[1].strip()
    await update_profile(user.id, birthday=birthday)
    data = await get_profile(user.id)
    await event.reply(setup_text(data), buttons=setup_buttons())


async def setgender_handler(event):
    user = await event.get_sender()
    parts = event.raw_text.split(maxsplit=1)
    if len(parts) < 2:
        await event.reply(font("Use: /setgender male/female/skip"))
        return
    gender = parts[1].strip().lower()
    if gender not in GENDERS:
        await event.reply(font("Gender option must be male, female, or skip."))
        return
    await update_profile(user.id, gender=gender.title())
    data = await get_profile(user.id)
    await event.reply(setup_text(data), buttons=setup_buttons())


async def setreligion_handler(event):
    user = await event.get_sender()
    parts = event.raw_text.split(maxsplit=1)
    if len(parts) < 2:
        await event.reply(font("Use: /setreligion hindu/muslim/christian/sikh/buddhist/jain/other/skip"))
        return
    religion = parts[1].strip().lower()
    if religion not in RELIGIONS:
        await event.reply(font("Invalid preference option."))
        return
    await update_profile(user.id, religion=religion.title())
    data = await get_profile(user.id)
    await event.reply(setup_text(data), buttons=setup_buttons())


async def gender_callback(event):
    user = await event.get_sender()
    value = event.data.decode().replace("azai_gender_", "")
    if value in GENDERS:
        await update_profile(user.id, gender=value.title())
    data = await get_profile(user.id)
    await event.edit(setup_text(data), buttons=setup_buttons())


async def religion_menu_callback(event):
    await event.edit(font("❂ SELECT PREFERENCE") + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━", buttons=religion_buttons())


async def religion_callback(event):
    user = await event.get_sender()
    value = event.data.decode().replace("azai_religion_", "")
    if value in RELIGIONS:
        await update_profile(user.id, religion=value.title())
    data = await get_profile(user.id)
    await event.edit(setup_text(data), buttons=setup_buttons())


async def profile_back_callback(event):
    user = await event.get_sender()
    data = await get_profile(user.id)
    await event.edit(setup_text(data), buttons=setup_buttons())


async def profile_close_callback(event):
    await event.delete()


if "azai_profile_setup" not in tbot.handlers_loaded:
    tbot.add_event_handler(setup_handler, events.NewMessage(pattern=f"^{prefix_cmds}setup$", incoming=True))
    tbot.add_event_handler(profile_handler, events.NewMessage(pattern=f"^{prefix_cmds}profile$", incoming=True))
    tbot.add_event_handler(setname_handler, events.NewMessage(pattern=f"^{prefix_cmds}setname(?: .*)?$", incoming=True))
    tbot.add_event_handler(setbirthday_handler, events.NewMessage(pattern=f"^{prefix_cmds}setbirthday(?: .*)?$", incoming=True))
    tbot.add_event_handler(setgender_handler, events.NewMessage(pattern=f"^{prefix_cmds}setgender(?: .*)?$", incoming=True))
    tbot.add_event_handler(setreligion_handler, events.NewMessage(pattern=f"^{prefix_cmds}setreligion(?: .*)?$", incoming=True))
    tbot.add_event_handler(gender_callback, events.CallbackQuery(pattern=b"azai_gender_"))
    tbot.add_event_handler(religion_menu_callback, events.CallbackQuery(pattern=b"azai_religion_menu"))
    tbot.add_event_handler(religion_callback, events.CallbackQuery(pattern=b"azai_religion_"))
    tbot.add_event_handler(profile_back_callback, events.CallbackQuery(pattern=b"azai_profile_back"))
    tbot.add_event_handler(profile_close_callback, events.CallbackQuery(pattern=b"azai_profile_close"))
    tbot.handlers_loaded.add("azai_profile_setup")
