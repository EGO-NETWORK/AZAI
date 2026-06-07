import random
from datetime import datetime

import pytz
from telethon import Button, events

from AloneX import database, font, prefix_cmds, tbot

IST = pytz.timezone("Asia/Kolkata")
AZAI_BOT_USERNAME = "Urxazaibot"
gate_db = database["azai_group_gate"]
active_gate = {}
