from AloneX import tbot

__module__ = "AZAI Personality Guard"

__help__ = """
Final safety guard for AZAI personality patches.
Keeps public replies natural and avoids public AI/bot identity wording in fallback text.
"""


def _patch_final_public_guard():
    try:
        from AloneX.plugins import azai_ai_chat as chat
    except Exception:
        return

    def final_fallback_reply(role: str, mode: str | None) -> str:
        if role == "OWNER":
            return "Boss, network abhi blink kar raha hai. Core system active hai."
        if role == "BHABHI":
            return "Bhabhi Ji, network abhi blink kar raha hai. Commands ready hain."
        if mode == "female":
            return "Scene clear batao, sorted karte hain."
        return "Bhai, network abhi blink kar raha hai. Scene clear bol."

    chat.fallback_reply = final_fallback_reply

    try:
        from AloneX.plugins import azai_personality_master as master
        # Public scenes should not make AZAI sound like he is identifying himself as a bot.
        if len(master.AZAI_AYU_SCENES) > 1 and master.AZAI_AYU_SCENES[1]:
            master.AZAI_AYU_SCENES[1][0] = "AZAI: Aaj college, hotel work, gym, aur project ka code... dimaag ka server garam hai."
    except Exception:
        pass


_patch_final_public_guard()

if "zz_azai_personality_guard" not in tbot.handlers_loaded:
    tbot.handlers_loaded.add("zz_azai_personality_guard")
