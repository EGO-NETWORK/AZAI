import os

import config


def _safe_int(value, default=0):
    try:
        return int(str(value or default).strip())
    except Exception:
        return int(default or 0)


# Public config-level identity IDs loaded from Replit/GitHub environment.
# Do not hardcode private IDs in the repository. Put real values in Secrets.
config.ALIZA_ID = _safe_int(os.getenv("ALIZA_ID") or getattr(config, "ALIZA_ID", 0))
config.BHABHI_ID = _safe_int(os.getenv("BHABHI_ID") or config.ALIZA_ID)

# Logger fallback chain: LOGGER_ID -> LOG_GROUP_ID -> LOGS_CHANNEL when numeric.
config.LOGGER_ID = _safe_int(os.getenv("LOGGER_ID") or os.getenv("LOG_GROUP_ID") or getattr(config, "LOGGER_ID", 0))

if not getattr(config, "LOGS_CHANNEL", None) and config.LOGGER_ID:
    config.LOGS_CHANNEL = config.LOGGER_ID
