"""AZAI owner panel media command patch."""

from AloneX import font
from AloneX.plugins import azai_owner_panel as owner_panel

BRAND = font("EGO Network - EST. 2026")


def market_text() -> str:
    return (
        font("MEDIA CONTROL")
        + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("Start / Help Panel:")
        + "\n"
        + font("Send image or video, reply, then use:")
        + " /setstartpic\n\n"
        + font("Shop Item Image:")
        + "\n"
        + font("Send item image, reply, then use:")
        + " /setitempic item_id\n\n"
        + font("Leaderboard Image:")
        + "\n"
        + font("Send leaderboard image, reply, then use:")
        + " /setleaderpic\n\n"
        + font("Media Settings Guide:")
        + " /msettings\n\n"
        + font("Powered By:")
        + " "
        + BRAND
    )


def guide_text() -> str:
    return (
        font("AZAI SETUP GUIDE")
        + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + font("MEDIA SETUP:")
        + "\n/setstartpic - set start and help panel media\n"
        + "/setitempic item_id - set shop item image\n"
        + "/setleaderpic - set leaderboard image\n"
        + "/msettings - open media setup guide\n\n"
        + font("OWNER MOD:")
        + "\n/ownermod on\n/ownermod off\n/ownermod status\n\n"
        + font("ANIME QUIZ:")
        + "\n/addanimeq answer | option1 | option2 | option3 | option4\n/animeguess\n\n"
        + font("EVENTS:")
        + "\n/events\n/addevent DD/MM | title | text\n"
    )


owner_panel.market_text = market_text
owner_panel.guide_text = guide_text
