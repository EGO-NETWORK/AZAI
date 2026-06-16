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

# Coordinates are tuned for the EGO HUSTLE leaderboard template:
# top-center empty circle + right-side top 10 table.
PFP_CENTER = (1056, 190)
PFP_SIZE = 226
ROW_Y = 408
ROW_STEP = 43
NAME_X = 865
USERNAME_X = 1128
BALANCE_X = 1360


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


def _scale(v, w):
    return int(v * w / BASE_W)


def _name(row):
    return (row.get("name") or row.get("username") or f"User {row.get('user_id')}")[:20]


def _username(row):
    username = row.get("username")
    if not username:
        return "-"
    username = str(username)
    if not username.startswith("@"):
        username = "@" + username
    return username[:18]


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
        data = await core.media_db.find_one({"key": "leaderboard"})
        if not data:
            return None
        msg = await tbot.get_messages(int(data["chat_id"]), ids=int(data["msg_id"]))
        if not msg or not msg.media:
            return None
        temp_dir = tempfile.mkdtemp()
        return await tbot.download_media(msg, file=temp_dir)
    except Exception:
        return None


def _blank_template():
    bg = Image.new("RGB", (BASE_W, BASE_H), (7, 9, 18))
    draw = ImageDraw.Draw(bg)
    for y in range(BASE_H):
        ratio = y / BASE_H
        draw.line((0, y, BASE_W, y), fill=(int(7 + ratio * 12), int(9 + ratio * 14), int(20 + ratio * 35)))
    title = _font(64, True)
    sub = _font(34, True)
    draw.text((70, 65), "EGO HUSTLE", font=title, fill=(245, 207, 90))
    draw.text((130, 155), "LEADERBOARD", font=sub, fill=(80, 200, 255))
    draw.ellipse((945, 77, 1167, 299), outline=(245, 207, 90), width=8)
    draw.text((970, 40), "#1 TOP PLAYER", font=_font(28, True), fill=(245, 207, 90))
    draw.rounded_rectangle((630, 330, 1505, 805), radius=22, outline=(245, 207, 90), width=3)
    for i in range(10):
        y = ROW_Y + i * ROW_STEP
        draw.rounded_rectangle((740, y - 5, 1470, y + 30), radius=10, outline=(75, 85, 110), width=1)
        draw.text((685, y), str(i + 1), font=_font(24, True), fill=(245, 207, 90))
    return bg


def _draw_placeholder_pfp(bg, x, y, size):
    draw = ImageDraw.Draw(bg)
    draw.ellipse((x, y, x + size, y + size), fill=(20, 24, 45), outline=(245, 207, 90), width=5)
    draw.text((x + size * 0.36, y + size * 0.38), "EC", font=_font(max(28, size // 5), True), fill=(245, 207, 90))


async def _make_card(rows):
    if Image is None:
        return None

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

    # Player PFP in the empty #1 circle.
    cx, cy = _scale_xy(PFP_CENTER[0], PFP_CENTER[1], w, h)
    pfp_size = max(120, int(PFP_SIZE * w / BASE_W))
    pfp_x, pfp_y = cx - pfp_size // 2, cy - pfp_size // 2

    if rows:
        top = rows[0]
        pfp_path = await _download_pfp(top.get("user_id"))
        if pfp_path and os.path.exists(pfp_path):
            try:
                pfp = _circle_crop(Image.open(pfp_path), pfp_size)
                bg.paste(pfp, (pfp_x, pfp_y), pfp)
            except Exception:
                _draw_placeholder_pfp(bg, pfp_x, pfp_y, pfp_size)
        else:
            _draw_placeholder_pfp(bg, pfp_x, pfp_y, pfp_size)

    # Top 10 real data rows.
    row_font = _font(max(16, int(24 * w / BASE_W)), True)
    for idx, row in enumerate(rows[:10], 0):
        y = int((ROW_Y + idx * ROW_STEP) * h / BASE_H)
        name_x = int(NAME_X * w / BASE_W)
        username_x = int(USERNAME_X * w / BASE_W)
        balance_x = int(BALANCE_X * w / BASE_W)
        name = _name(row)
        username = _username(row)
        balance = int(row.get("balance", 0) or 0)
        draw.text((name_x, y), name, font=row_font, fill=(238, 244, 255))
        draw.text((username_x, y), username, font=row_font, fill=(130, 220, 255))
        draw.text((balance_x, y), f"{balance} EC", font=row_font, fill=(245, 207, 90))

    if not rows:
        draw.text(_scale_xy(850, 430, w, h), "NO PLAYERS YET", font=_font(max(24, int(34 * w / BASE_W)), True), fill=(245, 207, 90))

    out = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    bg.save(out.name, "PNG")
    return out.name


async def dynamic_leaderboard(event):
    rows = await core.wallet_db.find({}).sort("balance", -1).limit(10).to_list(length=10)
    path = await _make_card(rows)
    if not path:
        await core.send(event, "leaderboard", await core.top_text(), core.back())
        return
    try:
        await tbot.send_file(event.chat_id, path, caption=font("EGO HUSTLE LEADERBOARD"), buttons=core.back())
    finally:
        try:
            os.remove(path)
        except Exception:
            pass
    raise events.StopPropagation


if "zzzzzzzzzzzzzzzzzzzzz_azai_dynamic_leaderboard_card" not in tbot.handlers_loaded:
    try:
        tbot.remove_event_handler(core.top)
    except Exception:
        pass
    tbot.add_event_handler(dynamic_leaderboard, events.NewMessage(pattern=f"^{prefix_cmds}(leaderboard|top)(?:@\\w+)?$", incoming=True))
    tbot.handlers_loaded.add("zzzzzzzzzzzzzzzzzzzzz_azai_dynamic_leaderboard_card")
