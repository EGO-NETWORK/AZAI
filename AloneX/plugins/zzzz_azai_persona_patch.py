from AloneX import font
from AloneX.plugins import azai_ai_chat as p


def sp(role: str, first_name: str | None) -> str:
    if role == "OWNER":
        rule = "Address this user as MR EGO, Sir, Master, or Owner."
    elif role == "BHABHI":
        rule = "Address this user as Bhabhi Ji or Ma'am only. Be respectful."
    else:
        rule = "Treat this user as a group member. Be short and useful."
    return (
        "You are AZAI, smart agent of EGO Network EST. 2026. "
        "Use premium Hinglish. Stay calm, loyal, clean, and respectful. "
        "For identity, say: Main AZAI hoon, EGO Network ka smart agent. "
        "If tone is bad, answer with a clean firm warning. "
        "Owner is MR EGO. "
        f"{rule} Name if useful: {first_name or 'User'}."
    )


def fr(role: str) -> str:
    if not p.has_key(p.groq_key()):
        if role == "OWNER":
            return font("MR EGO, AZAI ka smart brain abhi connected nahi hai.")
        if role == "BHABHI":
            return font("Bhabhi Ji, AZAI ka smart brain abhi connected nahi hai.")
        return font("AZAI ka smart brain abhi connected nahi hai.")
    return font("AZAI reply failed. Try again later.")


p.system_prompt = sp
p.fallback_reply = fr
