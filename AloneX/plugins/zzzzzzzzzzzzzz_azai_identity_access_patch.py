import importlib
import os
import sys

import config


def _to_int(value, default=0):
    try:
        return int(str(value).strip())
    except Exception:
        return default


OWNER_ONLY_ID = _to_int(os.getenv("OWNER_ID") or getattr(config, "OWNER_ID", 0))
BHABHI_ONLY_ID = _to_int(os.getenv("BHABHI_ID") or os.getenv("ALIZA_ID") or getattr(config, "BHABHI_ID", 0) or getattr(config, "ALIZA_ID", 0))

setattr(config, "OWNER_ID", OWNER_ONLY_ID)
setattr(config, "ALONE_OWNER_ID", 0)
setattr(config, "BHABHI_ID", BHABHI_ONLY_ID)
setattr(config, "ALIZA_ID", BHABHI_ONLY_ID)


def owner_ids():
    return {OWNER_ONLY_ID} if OWNER_ONLY_ID else set()


def bhabhi_ids():
    return {BHABHI_ONLY_ID} if BHABHI_ONLY_ID else set()


async def is_owner(event):
    sender_id = getattr(event, "sender_id", None)
    if sender_id is None and hasattr(event, "get_sender"):
        try:
            sender = await event.get_sender()
            sender_id = getattr(sender, "id", None)
        except Exception:
            sender_id = None
    return bool(sender_id and sender_id in owner_ids())


def special_role(user_id):
    uid = _to_int(user_id)
    if uid and uid in owner_ids():
        return "OWNER"
    if uid and uid in bhabhi_ids():
        return "BHABHI"
    return None


TARGET_MODULES = (
    "AloneX.plugins.aa00_azai_premium_settings",
    "AloneX.plugins.aa000_azai_panel_media_manager",
    "AloneX.plugins.zzzz_azai_ego_hustle_core",
    "AloneX.plugins.zzzz_azai_broadcast",
    "AloneX.plugins.zzzz_azai_events",
    "AloneX.plugins.zzzz_azai_festivals",
    "AloneX.plugins.azai_owner_panel",
    "AloneX.plugins.azai_ai_chat",
)


def _patch_module(module):
    for name, value in (
        ("OWNER_ID", OWNER_ONLY_ID),
        ("ALONE_OWNER_ID", 0),
        ("BHABHI_ID", BHABHI_ONLY_ID),
        ("ALIZA_ID", BHABHI_ONLY_ID),
    ):
        if hasattr(module, name):
            try:
                setattr(module, name, value)
            except Exception:
                pass
    for name, value in (
        ("owner_ids", owner_ids),
        ("azai_owner_ids", owner_ids),
        ("bhabhi_ids", bhabhi_ids),
        ("azai_bhabhi_ids", bhabhi_ids),
        ("is_owner", is_owner),
        ("special_role", special_role),
        ("get_special_role", special_role),
    ):
        try:
            setattr(module, name, value)
        except Exception:
            pass


for mod_name in TARGET_MODULES:
    try:
        module = sys.modules.get(mod_name) or importlib.import_module(mod_name)
        _patch_module(module)
    except Exception:
        pass
