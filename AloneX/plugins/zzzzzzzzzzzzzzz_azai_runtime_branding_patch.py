import os

import config


BRAND_DEFAULTS = {
    "BOT_NAME": "AZAI",
    "SUPPORT_CHAT": "EGOxSUPPORT",
    "UPDATE_CHANNEL": "EGOxUPDATES",
    "SUPPORT_GROUP": "https://t.me/EGOxSUPPORT",
    "BOT_USERNAME": os.getenv("BOT_USERNAME", getattr(config, "BOT_USERNAME", "AZAI")),
    "START_IMG_URL": os.getenv("START_IMG_URL", getattr(config, "START_IMG_URL", "")),
}


for key, value in BRAND_DEFAULTS.items():
    try:
        setattr(config, key, value)
    except Exception:
        pass
