import os

import config


def _env_int(*names, default=0):
    for name in names:
        value = os.getenv(name)
        if value:
            try:
                return int(value)
            except Exception:
                continue
    return int(default or 0)


# Central runtime aliases for AZAI identity/logging related IDs.
# Keep real numeric IDs in Replit Secrets, not inside repo code.
ALIZA_ID = _env_int("ALIZA_ID", "BHABHI_ID", default=getattr(config, "ALIZA_ID", 0))
BHABHI_ID = _env_int("BHABHI_ID", "ALIZA_ID", default=ALIZA_ID)
LOGGER_ID = _env_int("LOGGER_ID", "LOGS_CHANNEL", "LOG_GROUP_ID", default=getattr(config, "LOGGER_ID", 0))

setattr(config, "ALIZA_ID", ALIZA_ID)
setattr(config, "BHABHI_ID", BHABHI_ID)
setattr(config, "LOGGER_ID", LOGGER_ID)

if not getattr(config, "LOGS_CHANNEL", None) and LOGGER_ID:
    setattr(config, "LOGS_CHANNEL", LOGGER_ID)
