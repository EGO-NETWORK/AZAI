from telethon import events

from AloneX import tbot
from AloneX.plugins.azai_commands import commands_handler
from AloneX.plugins.azai_economy import daily_handler, inventory_handler, leaderboard_handler, wallet_handler
from AloneX.plugins.azai_market import garage_handler, shop_handler, vault_handler


def mention_pattern(command: str) -> str:
    return rf"^[/!.]{command}(?:@\w+)?$"


async def shop_mention(event):
    await shop_handler(event)
    raise events.StopPropagation


async def vault_mention(event):
    await vault_handler(event)
    raise events.StopPropagation


async def garage_mention(event):
    await garage_handler(event)
    raise events.StopPropagation


async def inventory_mention(event):
    await inventory_handler(event)
    raise events.StopPropagation


async def wallet_mention(event):
    await wallet_handler(event)
    raise events.StopPropagation


async def daily_mention(event):
    await daily_handler(event)
    raise events.StopPropagation


async def leaderboard_mention(event):
    await leaderboard_handler(event)
    raise events.StopPropagation


async def commands_mention(event):
    await commands_handler(event)
    raise events.StopPropagation


if "aaa_azai_mention_commands" not in tbot.handlers_loaded:
    tbot.add_event_handler(shop_mention, events.NewMessage(pattern=mention_pattern("shop"), incoming=True))
    tbot.add_event_handler(vault_mention, events.NewMessage(pattern=mention_pattern("vault"), incoming=True))
    tbot.add_event_handler(garage_mention, events.NewMessage(pattern=mention_pattern("garage"), incoming=True))
    tbot.add_event_handler(inventory_mention, events.NewMessage(pattern=mention_pattern("inventory"), incoming=True))
    tbot.add_event_handler(wallet_mention, events.NewMessage(pattern=mention_pattern("wallet|balance"), incoming=True))
    tbot.add_event_handler(daily_mention, events.NewMessage(pattern=mention_pattern("daily"), incoming=True))
    tbot.add_event_handler(leaderboard_mention, events.NewMessage(pattern=mention_pattern("leaderboard"), incoming=True))
    tbot.add_event_handler(commands_mention, events.NewMessage(pattern=mention_pattern("commands"), incoming=True))
    tbot.handlers_loaded.add("aaa_azai_mention_commands")
