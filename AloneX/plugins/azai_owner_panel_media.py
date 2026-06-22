"""AZAI owner panel media, games, economy, and manual setup guide."""

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
        font("AZAI MANUAL SETUP GUIDE")
        + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("1. MAIN MEDIA SETUP")
        + "\nSend image/video in chat, reply to it, then use:"
        + "\n/setstartpic - Start, help, and welcome panel media"
        + "\n/setleaderpic - Leaderboard card media"
        + "\n/msettings - Open media settings panel\n\n"
        + font("2. EGO HUSTLE MEDIA")
        + "\nReply to image/video, then use the matching command:"
        + "\n/sethustlepic - EGO HUSTLE home"
        + "\n/setwalletpic - Wallet card"
        + "\n/setdailypic - Daily reward"
        + "\n/setworkpic - Work mode"
        + "\n/setraidpic - Raid mode"
        + "\n/setattackpic - Attack mode"
        + "\n/setluckpic - Luck mode"
        + "\n/setheistpic - Heist mode"
        + "\n/setprotectpic - Protection mode\n\n"
        + font("3. SHOP / ITEM MEDIA")
        + "\nReply to item image, then use:"
        + "\n/setitempic item_id"
        + "\nExample: /setitempic cat"
        + "\nThen users can see/purchase/gift that item from shop/market.\n\n"
        + font("4. CUSTOM FUN COMMANDS")
        + "\n/addfuncmd command | response text"
        + "\nExample: /addfuncmd huggy | hugs you softly"
        + "\n/setfuncmdpic command - reply to image/sticker/GIF first"
        + "\n/delfuncmd command - delete custom fun command"
        + "\n/funcmds - list custom fun commands\n\n"
        + font("5. READY FUN COMMANDS")
        + "\n/huggy /hug /pat /highfive /dice /dart /basketball /slot"
        + "\nIf a fun command does not show media, set its media with /setfuncmdpic when supported.\n\n"
        + font("6. GARAGE / MARKET")
        + "\n/garage - open garage panel when available"
        + "\n/shop or /market - open item shop"
        + "\n/inventory or /inv - user inventory"
        + "\n/gift item_id - reply to a user and gift item\n\n"
        + font("7. EVENTS / FESTIVALS")
        + "\n/addfestival title | religion | message"
        + "\n/delfestival title"
        + "\n/festivals - list saved festivals"
        + "\n/religion hindu/muslim/christian/sikh/buddhist/jain/all"
        + "\n/festivalauto on/off/status\n\n"
        + font("8. OWNER SAFETY")
        + "\nNever paste token, API hash, Mongo URL, or cookies in public."
        + "\nOwner commands require correct OWNER_ID and ALONE_OWNER_ID in .env."
        + "\nIf /owner says owner-only, check numeric Telegram ID and anonymous admin mode.\n\n"
        + font("9. CHAT-OFF MODE")
        + "\nKeep brain/personality/tone/real_alive chat plugins disabled."
        + "\nKeep reaction.py for emoji reactions."
        + "\nUse /reaction on to enable emoji reactions."
    )


owner_panel.market_text = market_text
owner_panel.games_text = games_text
owner_panel.economy_text = economy_text
owner_panel.guide_text = guide_text
