from AloneX import font
from AloneX.plugins import azai_owner_panel as p


def media_text() -> str:
    return (
        font("MEDIA SETUP") + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + "/setstartpic - " + font("Set start and help panel media") + "\n"
        + "/setitempic item_id - " + font("Attach media to shop items") + "\n"
        + "/setleaderpic - " + font("Set leaderboard media card") + "\n"
        + "/msettings - " + font("Open media setup guide") + "\n\n"
        + font("How to use:") + "\n"
        + font("Send image or video, reply to it, then run the set command.")
    )


p.market_text = media_text
