# Early loader for EGO HUSTLE.
# This imports the game modules before older economy handlers, so /daily, /bal,
# /leaderboard, and game commands are handled by the unified EGO HUSTLE system first.

from AloneX.plugins import zzzz_azai_ego_hustle_core  # noqa: F401
from AloneX.plugins import zzzz_azai_ego_hustle_actions  # noqa: F401
from AloneX.plugins import zzzz_azai_ego_hustle_media_extra  # noqa: F401
