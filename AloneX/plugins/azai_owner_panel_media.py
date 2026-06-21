"""AZAI owner panel media, games, and economy command guide."""

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
        font("AZAI SETUP GUIDE")
        + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("MAIN MEDIA:")
        + "\n/setstartpic - start, help, and group welcome media\n"
        + "/setitempic item_id - shop item image\n"
        + "/setleaderpic - leaderboard image\n"
        + "/msettings - media setup guide\n\n"
        + font("EGO HUSTLE MEDIA:")
        + "\n/sethustlepic /setwalletpic /setdailypic /setworkpic\n"
        + "/setraidpic /setattackpic /setluckpic /setheistpic /setprotectpic\n\n"
        + font("CUSTOM FUN MEDIA:")
        + "\n/addfuncmd command | response text\n"
        + "/setfuncmdpic command\n"
        + "/delfuncmd command\n/funcmds\n\n"
        + font("FUN & GAMES:")
        + "\n/hustle /raid /attack /luck /heist /protect\n"
        + "/dice /dart /basketball /slot /huggy /pat /highfive\n\n"
        + font("ECONOMY:")
        + "\n/wallet /daily /work /send amount /inventory /leaderboard\n\n"
        + font("SECURITY:")
        + "\n/verify /verifyall /unverifyall /ownermod status\n\n"
        + font("OWNER MOD:")
        + "\n/ownermod on\n/ownermod off\n/ownermod status\n"
    )


owner_panel.market_text = market_text
owner_panel.games_text = games_text
owner_panel.economy_text = economy_text
owner_panel.guide_text = guide_text
