"""Compatibility shim for old azai_economy imports.

The old duplicate economy module is removed. Main economy now uses EGO HUSTLE.
This shim keeps older mention/utility plugins from crashing when they import
legacy handler names.
"""

from AloneX import font
from AloneX.plugins.zzzz_azai_ego_hustle_core import (
    bal as wallet_handler,
    daily as daily_handler,
    top as leaderboard_handler,
)


async def inventory_handler(event):
    await event.reply(
        font("EGO HUSTLE INVENTORY")
        + "\n━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Inventory has moved into the EGO HUSTLE system.")
        + "\n\n"
        + font("Use:")
        + " /hustle /wallet /profile"
    )
