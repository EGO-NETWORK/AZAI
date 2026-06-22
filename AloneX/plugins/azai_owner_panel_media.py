"""AZAI owner panel media, games, economy, and full manual setup guide."""

from AloneX import font
from AloneX.plugins import azai_owner_panel as owner_panel

BRAND = font("EGO Network - EST. 2026")


def market_text() -> str:
    return (
        font("MEDIA & COMMAND CONTROL")
        + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Main Media:")
        + "\n/setstartpic - start, help, and group welcome media"
        + "\n/setleaderpic - leaderboard image"
        + "\n/setitempic item_id - shop/item image"
        + "\n/msettings - media setup guide\n\n"
        + font("EGO Hustle Media:")
        + "\n/sethustlepic /setwalletpic /setdailypic /setworkpic"
        + "\n/setraidpic /setattackpic /setluckpic /setheistpic /setprotectpic\n\n"
        + font("Custom Fun Commands:")
        + "\n/addfuncmd command | response text"
        + "\n/setfuncmdpic command"
        + "\n/delfuncmd command /funcmds\n\n"
        + font("Fun Commands:")
        + "\n/dice /dart /basketball /slot /huggy /pat /highfive\n\n"
        + font("Economy & EGO Hustle:")
        + "\n/wallet /daily /work /send amount"
        + "\n/hustle /raid /attack /luck /heist /protect\n\n"
        + font("Powered By:")
        + " "
        + BRAND
    )


def games_text() -> str:
    return (
        font("GAME & FUN CONTROL")
        + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("EGO Hustle:")
        + " /hustle\n"
        + font("Actions:")
        + " /raid /attack /luck /heist /protect\n"
        + font("Telegram Fun:")
        + " /dice /dart /basketball /slot\n"
        + font("Custom Fun:")
        + " /huggy /pat /highfive /funcmds\n\n"
        + font("Owner Setup:")
        + " /addfuncmd /setfuncmdpic /delfuncmd\n\n"
        + font("Powered By:")
        + " "
        + BRAND
    )


def economy_text() -> str:
    return (
        font("ECONOMY & HUSTLE CONTROL")
        + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Wallet:")
        + " /wallet /balance /bal\n"
        + font("Rewards:")
        + " /daily /work\n"
        + font("Transfer:")
        + " /send amount\n"
        + font("EGO Hustle:")
        + " /hustle /raid /attack /luck /heist /protect\n"
        + font("Inventory:")
        + " /inventory /garage /vault\n"
        + font("Market:")
        + " /shop /setcar /setbike /gift\n\n"
        + font("Media:")
        + " /setdailypic /setraidpic /setattackpic /setheistpic\n\n"
        + font("Currency:")
        + " EGO CREDIT (EC)"
    )


def guide_text() -> str:
    return (
        font("AZAI FULL OWNER GUIDE")
        + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("BASIC FLOW")
        + "\nSend photo/video/sticker/GIF, reply to it, then run the matching setup command.\n\n"
        + font("COMMAND AUDIT")
        + "\n/cmdaudit command - check command category when available"
        + "\nExample: /cmdaudit huggy\n\n"
        + font("MAIN MEDIA")
        + "\n/setstartpic - start/help/welcome panel media"
        + "\n/setleaderpic - leaderboard card"
        + "\n/setprofilepic - profile card when supported"
        + "\n/setvideo - video media when supported"
        + "\n/setsticker - sticker media when supported"
        + "\n/msettings - media settings panel\n\n"
        + font("EGO HUSTLE MEDIA")
        + "\n/sethustlepic /setwalletpic /setdailypic /setworkpic"
        + "\n/setraidpic /setattackpic /setluckpic /setheistpic /setprotectpic\n\n"
        + font("SHOP / ITEMS")
        + "\n/shop or /market - open shop"
        + "\n/inventory or /inv - user inventory"
        + "\n/gift item_id - reply to user and gift item"
        + "\n/setitempic item_id - reply to item image and set item media"
        + "\n/additem item_id | name | price | description - add shop item when supported"
        + "\n/delitem item_id or /removeitem item_id - remove shop item when supported"
        + "\n/addvaultitem item_id | name | price | stock | description - add limited item when supported"
        + "\n/delvaultitem item_id - remove limited item when supported"
        + "\nIf remove media command is missing, overwrite media with /setitempic.\n\n"
        + font("GARAGE")
        + "\n/garage - open garage panel"
        + "\n/mygarage - owned garage items when supported"
        + "\n/setcar item_id or /setbike item_id - vehicle item setup when supported"
        + "\nUse clean item IDs like duke390, cat, rose.\n\n"
        + font("CUSTOM FUN COMMANDS")
        + "\n/addfuncmd command | response text"
        + "\nExample: /addfuncmd huggy | gives a cute hug"
        + "\n/setfuncmdpic command - reply to photo/sticker/GIF first"
        + "\n/delfuncmd command - remove custom fun command"
        + "\n/funcmds - list all custom fun commands"
        + "\nReady fun: /huggy /hug /pat /highfive /dice /dart /basketball /slot\n\n"
        + font("EVENTS / FESTIVALS")
        + "\n/addfestival title | religion | message"
        + "\n/delfestival title"
        + "\n/festivals - list saved festivals"
        + "\n/todayfestivals - check today"
        + "\n/religion hindu/muslim/christian/sikh/buddhist/jain/all"
        + "\n/myreligion - check preference"
        + "\n/festivalauto on/off/status\n\n"
        + font("REACTION / CHAT-OFF")
        + "\nKeep brain/personality/tone/real_alive/reaction_mode chat plugins disabled."
        + "\nKeep only reaction.py for emoji reactions."
        + "\n/reaction on - enable emoji reactions"
        + "\n/reaction off - disable emoji reactions"
        + "\nNormal text chat stays OFF. Commands still reply.\n\n"
        + font("OWNER SAFETY")
        + "\nOWNER_ID and ALONE_OWNER_ID must match your numeric Telegram user ID."
        + "\nLOG_GROUP_ID can stay 0 until logger group is ready."
        + "\nKeep private credentials hidden."
    )


owner_panel.market_text = market_text
owner_panel.games_text = games_text
owner_panel.economy_text = economy_text
owner_panel.guide_text = guide_text
