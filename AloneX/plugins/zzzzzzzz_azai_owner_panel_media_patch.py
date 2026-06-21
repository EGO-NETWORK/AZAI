"""AZAI owner panel media, games, and economy command patch."""

from AloneX import font
from AloneX.plugins import azai_owner_panel as owner_panel

BRAND = font("EGO Network - EST. 2026")


def market_text() -> str:
    return (
        font("MEDIA & COMMAND CONTROL")
        + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Media Setup:")
        + "\n/setstartpic - set start, help, and group welcome media"
        + "\n/setleaderpic - set leaderboard image"
        + "\n/setitempic item_id - set shop/item image"
        + "\n/msettings - open media setup guide\n\n"
        + font("Fun Commands:")
        + "\n/dice /dart /basketball /slot\n\n"
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
        + " /dice /dart /basketball /slot\n\n"
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
        + font("Currency:")
        + " EGO CREDIT (EC)"
    )


def guide_text() -> str:
    return (
        font("AZAI SETUP GUIDE")
        + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("MEDIA SETUP:")
        + "\n/setstartpic - set start, help, and group welcome media\n"
        + "/setitempic item_id - set shop item image\n"
        + "/setleaderpic - set leaderboard image\n"
        + "/msettings - open media setup guide\n\n"
        + font("FUN & GAMES:")
        + "\n/hustle /raid /attack /luck /heist /protect\n"
        + "/dice /dart /basketball /slot\n\n"
        + font("ECONOMY:")
        + "\n/wallet /daily /work /send amount /inventory /leaderboard\n\n"
        + font("SECURITY:")
        + "\n/verify /verifyall /unverifyall /ownermod status\n\n"
        + font("OWNER MOD:")
        + "\n/ownermod on\n/ownermod off\n/ownermod status\n\n"
        + font("ANIME QUIZ:")
        + "\n/addanimeq answer | option1 | option2 | option3 | option4\n/animeguess\n\n"
        + font("EVENTS:")
        + "\n/events\n/addevent DD/MM | title | text\n"
    )


owner_panel.market_text = market_text
owner_panel.games_text = games_text
owner_panel.economy_text = economy_text
owner_panel.guide_text = guide_text
