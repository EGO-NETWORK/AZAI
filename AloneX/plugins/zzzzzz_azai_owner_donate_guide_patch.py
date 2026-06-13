from AloneX import font
from AloneX.plugins import azai_owner_panel as owner_panel

_old_guide_text = owner_panel.guide_text


def guide_text() -> str:
    return (
        _old_guide_text()
        + "\n\n"
        + font("DONATE / TELEGRAM STARS:") + "\n"
        + font("Current mode:") + " " + font("Telegram Stars only") + "\n"
        + font("Minimum:") + " 10 Stars\n"
        + font("Public command:") + " /donate 10\n"
        + font("Start panel:") + " " + font("Donate button opens Stars donate guide") + "\n"
        + font("Later setup:") + " " + font("Add more star amount buttons after testing 10 Stars live.")
    )


owner_panel.guide_text = guide_text
