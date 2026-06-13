import re
from types import MethodType

from telethon import Button

from AloneX import app, font, tbot

_PROTECT_RE = re.compile(r"(`[^`]*`|https?://\S+|t\.me/\S+|@[A-Za-z0-9_]{3,32}|/[A-Za-z0-9_@]+)")
_PATCH_FLAG = "zzzzzz_azai_global_font_guard"


def _safe_font_text(value):
    if value is None or not isinstance(value, str) or not value.strip():
        return value
    if not any(ch.isalpha() for ch in value):
        return value

    saved = []

    def hold(match):
        saved.append(match.group(0))
        return f"\ue000{len(saved) - 1}\ue001"

    protected = _PROTECT_RE.sub(hold, value)
    styled = font(protected)

    for idx, original in enumerate(saved):
        styled = styled.replace(f"\ue000{idx}\ue001", original)
    return styled


def _skip_kwargs(kwargs):
    parse_mode = kwargs.get("parse_mode")
    if parse_mode:
        return True
    return False


def _patch_async_method(obj, attr, *, text_kw=None, caption_kw=None, text_index=None):
    if not obj or not hasattr(obj, attr):
        return
    current = getattr(obj, attr)
    if getattr(current, "_azai_font_guard", False):
        return

    async def wrapper(self, *args, **kwargs):
        if not _skip_kwargs(kwargs):
            args = list(args)
            if text_kw and text_kw in kwargs:
                kwargs[text_kw] = _safe_font_text(kwargs[text_kw])
            if caption_kw and caption_kw in kwargs:
                kwargs[caption_kw] = _safe_font_text(kwargs[caption_kw])
            if text_index is not None and len(args) > text_index:
                args[text_index] = _safe_font_text(args[text_index])
            args = tuple(args)
        return await current(*args, **kwargs)

    wrapper._azai_font_guard = True
    setattr(obj, attr, MethodType(wrapper, obj))


def _patch_button_inline():
    original = getattr(Button, "inline", None)
    if not original or getattr(original, "_azai_font_guard", False):
        return

    def inline(text, *args, **kwargs):
        return original(_safe_font_text(text), *args, **kwargs)

    inline._azai_font_guard = True
    Button.inline = staticmethod(inline)


if _PATCH_FLAG not in getattr(tbot, "handlers_loaded", set()):
    _patch_async_method(tbot, "send_message", text_kw="message", text_index=1)
    _patch_async_method(tbot, "send_file", caption_kw="caption")
    _patch_async_method(tbot, "edit_message", text_kw="text", text_index=2)

    try:
        bot = app.bot
        _patch_async_method(bot, "send_message", text_kw="text", text_index=1)
        _patch_async_method(bot, "edit_message_text", text_kw="text", text_index=0)
    except Exception:
        pass

    _patch_button_inline()
    tbot.handlers_loaded.add(_PATCH_FLAG)
