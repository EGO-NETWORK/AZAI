import os
import tempfile

from telethon import events

from AloneX import font, prefix_cmds, tbot
import AloneX.plugins.zzzz_azai_ego_hustle_core as core

try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
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


def _name(row):
    return row.get("name") or row.get("username") or f"User {row.get('user_id')}"


def _circle_crop(img, size):
    img = img.convert("RGB").resize((size, size))
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size, size), fill=255)
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.paste(img, (0, 0), mask)
    return out


def _draw_glow_circle(draw, x, y, r, color):
    for i in range(7, 0, -1):
        alpha = 30 + i * 8
        c = tuple(min(255, v + i * 6) for v in color)
        draw.ellipse((x - r - i * 5, y - r - i * 5, x + r + i * 5, y + r + i * 5), outline=c, width=2)
    draw.ellipse((x - r, y - r, x + r, y + r), outline=color, width=6)


async def _download_pfp(user_id):
    try:
        entity = await tbot.get_entity(int(user_id))
        temp_dir = tempfile.mkdtemp()
        path = await tbot.download_profile_photo(entity, file=temp_dir)
        return path
    except Exception:
        return None


async def _make_card(rows):
    if Image is None:
        return None

    bg = Image.new("RGB", (CARD_W, CARD_H), (7, 9, 18))
    draw = ImageDraw.Draw(bg)

    # premium dark gradient
    for y in range(CARD_H):
        ratio = y / CARD_H
        r = int(8 + ratio * 10)
        g = int(10 + ratio * 12)
        b = int(22 + ratio * 28)
        draw.line((0, y, CARD_W, y), fill=(r, g, b))

    # neon panels
    draw.rounded_rectangle((40, 40, 1240, 680), radius=32, outline=(210, 170, 65), width=3)
    draw.rounded_rectangle((70, 90, 560, 635), radius=30, fill=(12, 15, 32), outline=(70, 115, 190), width=2)
    draw.rounded_rectangle((600, 105, 1210, 635), radius=28, fill=(13, 16, 33), outline=(70, 115, 190), width=2)

    title_font = _font(64, True)
    sub_font = _font(27, False)
    rank_font = _font(42, True)
    name_font = _font(36, True)
    small_font = _font(25, False)
    row_font = _font(26, True)

    draw.text((75, 42), "EGO HUSTLE", font=title_font, fill=(245, 207, 90))
    draw.text((80, 112), "LEADERBOARD • TOP PLAYERS", font=sub_font, fill=(190, 220, 255))
    draw.text((80, 640), "EGO Network · EST. 2026   |   MR EGO", font=small_font, fill=(160, 170, 190))

    if not rows:
        draw.text((165, 330), "NO PLAYERS YET", font=name_font, fill=(235, 235, 235))
    else:
        top = rows[0]
        top_name = _name(top)[:22]
        top_balance = int(top.get("balance", 0) or 0)
        top_power = int(top.get("power", 100) or 100)
        top_level = int(top.get("level", 1) or 1)

        # rank one crown and frame
        draw.text((210, 165), "#1", font=rank_font, fill=(245, 207, 90))
        draw.text((155, 215), "TOP PLAYER", font=small_font, fill=(190, 220, 255))
        _draw_glow_circle(draw, 315, 360, 118, (245, 207, 90))

        pfp_path = await _download_pfp(top.get("user_id"))
        if pfp_path and os.path.exists(pfp_path):
            try:
                pfp = Image.open(pfp_path)
                pfp = _circle_crop(pfp, 218)
                bg.paste(pfp, (206, 251), pfp)
            except Exception:
                draw.ellipse((206, 251, 424, 469), fill=(31, 38, 65))
                draw.text((278, 330), "AZ", font=rank_font, fill=(245, 207, 90))
        else:
            draw.ellipse((206, 251, 424, 469), fill=(31, 38, 65))
            draw.text((278, 330), "AZ", font=rank_font, fill=(245, 207, 90))

        draw.text((115, 500), top_name, font=name_font, fill=(255, 255, 255))
        draw.text((115, 548), f"{top_balance} EC", font=rank_font, fill=(245, 207, 90))
        draw.text((115, 600), f"Power {top_power}  •  Level {top_level}", font=small_font, fill=(190, 220, 255))

        y = 135
        for idx, row in enumerate(rows[:10], 1):
            name = _name(row)[:24]
            balance = int(row.get("balance", 0) or 0)
            power = int(row.get("power", 100) or 100)
            color = (245, 207, 90) if idx == 1 else (210, 220, 240)
            fill = (20, 26, 48) if idx % 2 else (16, 20, 38)
            draw.rounded_rectangle((630, y, 1180, y + 45), radius=15, fill=fill, outline=(45, 65, 105), width=1)
            draw.text((650, y + 8), f"#{idx}", font=row_font, fill=color)
            draw.text((720, y + 8), name, font=row_font, fill=(235, 240, 255))
            draw.text((1010, y + 8), f"{balance} EC", font=row_font, fill=(245, 207, 90))
            y += 49

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
