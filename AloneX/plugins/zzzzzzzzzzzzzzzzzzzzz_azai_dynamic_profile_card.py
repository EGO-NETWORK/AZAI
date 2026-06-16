import os
import tempfile

from telethon import events

from AloneX import font, prefix_cmds, tbot
import AloneX.plugins.zzzz_azai_ego_hustle_core as core

try:
    from PIL import Image, ImageDraw, ImageFont
except Exception:
    Image = None

CARD_W, CARD_H = 1280, 720


def _font(size, bold=False):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/dejavu/DejaVuSans.ttf",
    ]
    for path in paths:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            pass
    return ImageFont.load_default()


def _display_name(user, data):
    username = getattr(user, "username", None) or data.get("username")
    name = getattr(user, "first_name", None) or data.get("name") or "EGO Player"
    return f"{name} (@{username})" if username else name


def _circle_crop(img, size):
    img = img.convert("RGB").resize((size, size))
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size, size), fill=255)
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.paste(img, (0, 0), mask)
    return out


def _draw_meter(draw, x, y, w, h, value, max_value=250, label=""):
    value = max(0, min(int(value), max_value))
    fill_w = int(w * value / max_value)
    draw.rounded_rectangle((x, y, x + w, y + h), radius=14, fill=(20, 28, 50), outline=(65, 90, 140), width=2)
    draw.rounded_rectangle((x, y, x + fill_w, y + h), radius=14, fill=(236, 190, 74))
    if label:
        draw.text((x, y - 32), label, font=_font(24, True), fill=(205, 220, 255))


async def _download_pfp(user_id):
    try:
        entity = await tbot.get_entity(int(user_id))
        temp_dir = tempfile.mkdtemp()
        return await tbot.download_profile_photo(entity, file=temp_dir)
    except Exception:
        return None


async def _rank_for(balance):
    try:
        return await core.wallet_db.count_documents({"balance": {"$gt": int(balance)}}) + 1
    except Exception:
        return 0


async def _make_profile_card(user, data):
    if Image is None:
        return None

    balance = int(data.get("balance", 0) or 0)
    power = int(data.get("power", 100) or 100)
    level = int(data.get("level", 1) or 1)
    game = data.get("game", {}) or {}
    rank = await _rank_for(balance)
    protect_until = core.active_protect(data)
    protection = "Active" if protect_until > core.ts() else "Inactive"

    bg = Image.new("RGB", (CARD_W, CARD_H), (7, 9, 18))
    draw = ImageDraw.Draw(bg)

    for y in range(CARD_H):
        ratio = y / CARD_H
        draw.line((0, y, CARD_W, y), fill=(int(7 + ratio * 12), int(9 + ratio * 14), int(20 + ratio * 35)))

    draw.rounded_rectangle((40, 40, 1240, 680), radius=34, outline=(236, 190, 74), width=3)
    draw.rounded_rectangle((75, 95, 485, 635), radius=32, fill=(12, 15, 32), outline=(75, 115, 185), width=2)
    draw.rounded_rectangle((525, 95, 1205, 635), radius=32, fill=(13, 16, 33), outline=(75, 115, 185), width=2)

    title = _font(58, True)
    sub = _font(27, False)
    big = _font(52, True)
    name_font = _font(36, True)
    small = _font(25, False)
    stat = _font(30, True)

    draw.text((70, 42), "EGO HUSTLE PROFILE", font=title, fill=(245, 207, 90))
    draw.text((75, 110), "Player Identity • Wallet • Power • Rank", font=sub, fill=(190, 220, 255))

    # PFP frame
    cx, cy, r = 280, 315, 130
    for i in range(7, 0, -1):
        draw.ellipse((cx - r - i * 5, cy - r - i * 5, cx + r + i * 5, cy + r + i * 5), outline=(90 + i * 18, 75 + i * 14, 20), width=2)
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(245, 207, 90), width=7)

    pfp_path = await _download_pfp(data.get("user_id"))
    if pfp_path and os.path.exists(pfp_path):
        try:
            pfp = _circle_crop(Image.open(pfp_path), 246)
            bg.paste(pfp, (157, 192), pfp)
        except Exception:
            draw.ellipse((157, 192, 403, 438), fill=(32, 38, 65))
            draw.text((230, 284), "AZ", font=big, fill=(245, 207, 90))
    else:
        draw.ellipse((157, 192, 403, 438), fill=(32, 38, 65))
        draw.text((230, 284), "AZ", font=big, fill=(245, 207, 90))

    draw.text((165, 470), _display_name(user, data)[:24], font=name_font, fill=(255, 255, 255))
    draw.text((175, 520), f"Rank #{rank}" if rank else "Rank -", font=big, fill=(245, 207, 90))
    draw.text((160, 590), "EGO Network · EST. 2026", font=small, fill=(160, 170, 190))

    # Stats section
    draw.text((565, 135), f"{balance} EC", font=big, fill=(245, 207, 90))
    draw.text((570, 195), "Current Wallet Balance", font=small, fill=(190, 220, 255))

    _draw_meter(draw, 570, 280, 560, 28, power, 250, "Power Meter")
    draw.text((1145, 270), str(power), font=stat, fill=(245, 207, 90))

    y = 350
    rows = [
        ("Level", level),
        ("Protection", protection),
        ("Raid Wins", int(game.get("raid_wins", 0) or 0)),
        ("Attack Wins", int(game.get("attack_wins", 0) or 0)),
        ("Heist Wins", int(game.get("heist_wins", 0) or 0)),
    ]
    for label, value in rows:
        draw.rounded_rectangle((570, y, 1130, y + 45), radius=15, fill=(18, 24, 45), outline=(48, 70, 115), width=1)
        draw.text((595, y + 8), str(label), font=stat, fill=(215, 225, 245))
        draw.text((925, y + 8), str(value), font=stat, fill=(245, 207, 90))
        y += 54

    draw.text((570, 620), "AZAI • EGO HUSTLE • MR EGO", font=small, fill=(160, 170, 190))

    out = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    bg.save(out.name, "PNG")
    return out.name


async def profile_card(event):
    reply = await event.get_reply_message()
    user = await reply.get_sender() if reply else await event.get_sender()
    data = await core.wallet(user.id, user)
    path = await _make_profile_card(user, data)
    if not path:
        await core.send(event, "profile", await core.profile_text(user, data), core.back())
        return
    try:
        await tbot.send_file(event.chat_id, path, caption=font("EGO HUSTLE PROFILE"), buttons=core.back())
    finally:
        try:
            os.remove(path)
        except Exception:
            pass
    raise events.StopPropagation


if "zzzzzzzzzzzzzzzzzzzzz_azai_dynamic_profile_card" not in tbot.handlers_loaded:
    try:
        tbot.remove_event_handler(core.profile)
    except Exception:
        pass
    tbot.add_event_handler(profile_card, events.NewMessage(pattern=f"^{prefix_cmds}(profile|myprofile|profilecard)(?:@\\w+)?$", incoming=True))
    tbot.handlers_loaded.add("zzzzzzzzzzzzzzzzzzzzz_azai_dynamic_profile_card")
