"""Early AZAI environment aliases.

This keeps private IDs in Replit/GitHub environment secrets while making
legacy imports like `from config import ALIZA_ID, BHABHI_ID` safe for plugins.
"""

import os

import config


def _env_int(*names: str, default: int = 0) -> int:
    for name in names:
        value = os.getenv(name)
        if value is None or str(value).strip() == "":
            continue
        try:
            return int(str(value).strip())
        except Exception:
            continue
    return default


_aliza_id = _env_int("ALIZA_ID", "BHABHI_ID")
_bhabhi_id = _env_int("BHABHI_ID", "ALIZA_ID", default=_aliza_id)
_logger_id = _env_int("LOGGER_ID", "LOG_GROUP_ID", "LOGS_CHANNEL")

config.ALIZA_ID = _aliza_id
config.BHABHI_ID = _bhabhi_id

if not getattr(config, "LOGGER_ID", 0):
    config.LOGGER_ID = _logger_id

if not getattr(config, "LOG_GROUP_ID", 0) and _logger_id:
    config.LOG_GROUP_ID = _logger_id

if not getattr(config, "LOGS_CHANNEL", None) and _logger_id:
    config.LOGS_CHANNEL = _logger_id
