import os
import tempfile

from telethon import events

from AloneX import font, prefix_cmds, tbot
import AloneX.plugins.zzzz_azai_ego_hustle_core as core

try:
    from PIL import Image, ImageDraw, ImageFont
except Exception:
    Image = None

BASE_W, BASE_H = 1536, 864

# Coordinates tuned for the EGO HUSTLE Elite Player Profile template.
PFP_CENTER = (365, 335)
PFP_SIZE = 360
NAMEPLATE_CENTER = (360, 665)
VALUE_X = 930
ROWS = {
    "player": 208,
    "username": 258,
    "rank": 309,
    "balance": 359,
    "power": 411,
    "level": 461,
    "protection": 512,
    "raid": 562,
    "attack": 613,
    "heist": 664,
}


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


def _scale_xy(x, y, w, h):
    return int(x * w / BASE_W), int(y * h / BASE_H)


def _scale_size(v, w):
    return int(v * w / BASE_W)


def _display_name(user, data):
    name = getattr(user, "first_name", None) or data.get("name") or "EGO Player"
    return str(name)[:24]


def _username(user, data):
    username = getattr(user, "username", None) or data.get("username")
    if not username:
        return "-"
    username = str(username)
    if not username.startswith("@"):
        username = "@" + username
    return username[:22]


def _circle_crop(img, size):
    img = img.convert("RGB").resize((size, size))
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size, size), fill=255)
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.paste(img, (0, 0), mask)
    return out


async def _download_pfp(user_id):
    try:
        entity = await tbot.get_entity(int(user_id))
        temp_dir = tempfile.mkdtemp()
        return await tbot.download_profile_photo(entity, file=temp_dir)
    except Exception:
        return None


async def _download_template():
    try:
        data = await core.media_db.find_one({"key": "profile"})
        if not data:
            return None
        msg = await tbot.get_messages(int(data["chat_id"]), ids=int(data["msg_id"]))
        if not msg or not msg.media:
            return None
        temp_dir = tempfile.mkdtemp()
        return await tbot.download_media(msg, file=temp_dir)
    except Exception:
        return None


async def _rank_for(balance):
    try:
        return await core.wallet_db.count_documents({"balance": {"$gt": int(balance)}}) + 1
    except Exception:
        return 0


def _blank_template():
    bg = Image.new("RGB", (BASE_W, BASE_H), (7, 9, 18))
    draw = ImageDraw.Draw(bg)
    for y in range(BASE_H):
        ratio = y / BASE_H
        draw.line((0, y, BASE_W, y), fill=(int(7 + ratio * 12), int(9 + ratio * 14), int(20 + ratio * 35)))
    draw.rounded_rectangle((30, 30, 1505, 835), radius=32, outline=(245, 207, 90), width=3)
    draw.text((690, 60), "EGO HUSTLE", font=_font(64, True), fill=(245, 207, 90))
    draw.text((745, 135), "ELITE PLAYER PROFILE", font=_font(32, True), fill=(245, 207, 90))
    draw.ellipse((185, 155, 545, 515), outline=(245, 207, 90), width=8)
    draw.rounded_rectangle((120, 620, 620, 710), radius=24, outline=(245, 207, 90), width=3)
    for label, y in ROWS.items():
        draw.rounded_rectangle((900, y - 8, 1465, y + 28), radius=12, outline=(80, 105, 145), width=1)
    return bg


def _draw_placeholder_pfp(bg, x, y, size):
    draw = ImageDraw.Draw(bg)
    draw.ellipse((x, y, x + size, y + size), fill=(20, 24, 45), outline=(245, 207, 90), width=5)
    draw.text((x + size * 0.36, y + size * 0.38), "EC", font=_font(max(30, size // 5), True), fill=(245, 207, 90))


def _draw_value(draw, w, h, key, value, color=(235, 242, 255), bold=True):
    x, y = _scale_xy(VALUE_X, ROWS[key], w, h)
    size = max(16, int(26 * w / BASE_W))
    draw.text((x, y), str(value)[:28], font=_font(size, bold), fill=color)


def _draw_nameplate(draw, w, h, value):
    size = max(16, int(30 * w / BASE_W))
    fnt = _font(size, True)
    cx, cy = _scale_xy(NAMEPLATE_CENTER[0], NAMEPLATE_CENTER[1], w, h)
    try:
        box = draw.textbbox((0, 0), value, font=fnt)
        tw = box[2] - box[0]
    except Exception:
        tw = len(value) * size // 2
    draw.text((cx - tw // 2, cy - size // 2), value[:24], font=fnt, fill=(245, 207, 90))


async def _make_profile_card(user, data):
    if Image is None:
        return None

    balance = int(data.get("balance", 0) or 0)
    power = int(data.get("power", 100) or 100)
    level = int(data.get("level", 1) or 1)
    game = data.get("game", {}) or {}
    rank = await _rank_for(balance)
    protect_until = core.active_protect(data)
    protection = "ACTIVE" if protect_until > core.ts() else "INACTIVE"

    template_path = await _download_template()
    if template_path and os.path.exists(template_path):
        try:
            bg = Image.open(template_path).convert("RGB")
        except Exception:
            bg = _blank_template()
    else:
        bg = _blank_template()

    w, h = bg.size
    draw = ImageDraw.Draw(bg)

    # PFP inside the left premium circle.
    cx, cy = _scale_xy(PFP_CENTER[0], PFP_CENTER[1], w, h)
    pfp_size = max(170, _scale_size(PFP_SIZE, w))
    pfp_x, pfp_y = cx - pfp_size // 2, cy - pfp_size // 2

    pfp_path = await _download_pfp(data.get("user_id"))
    if pfp_path and os.path.exists(pfp_path):
        try:
            pfp = _circle_crop(Image.open(pfp_path), pfp_size)
            bg.paste(pfp, (pfp_x, pfp_y), pfp)
        except Exception:
            _draw_placeholder_pfp(bg, pfp_x, pfp_y, pfp_size)
    else:
        _draw_placeholder_pfp(bg, pfp_x, pfp_y, pfp_size)

    name = _display_name(user, data)
    username = _username(user, data)

    _draw_nameplate(draw, w, h, name)
    _draw_value(draw, w, h, "player", name)
    _draw_value(draw, w, h, "username", username, color=(130, 220, 255))
    _draw_value(draw, w, h, "rank", f"#{rank}" if rank else "-")
    _draw_value(draw, w, h, "balance", f"{balance} EC", color=(245, 207, 90))
    _draw_value(draw, w, h, "power", str(power), color=(245, 207, 90))
    _draw_value(draw, w, h, "level", str(level))
    _draw_value(draw, w, h, "protection", protection, color=(90, 225, 155) if protection == "ACTIVE" else (230, 150, 95))
    _draw_value(draw, w, h, "raid", int(game.get("raid_wins", 0) or 0))
    _draw_value(draw, w, h, "attack", int(game.get("attack_wins", 0) or 0))
    _draw_value(draw, w, h, "heist", int(game.get("heist_wins", 0) or 0))

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
