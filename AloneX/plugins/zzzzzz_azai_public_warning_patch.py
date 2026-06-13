_module_name = "".join(chr(x) for x in [65,108,111,110,101,88,46,112,108,117,103,105,110,115,46,122,122,122,122,95,97,122,97,105,95,109,105,114,114,111,114,95,114,117,108,101])
_m = __import__(_module_name, fromlist=["*"])
_old_font = _m.font
_title = "".join(chr(x) for x in [65,90,65,73,32,77,73,82,82,79,82,32,82,85,76,69])
_old_line = "".join(chr(x) for x in [67,108,101,97,110,32,108,97,110,103,117,97,103,101,32,114,101,113,117,105,114,101,100,46,32,82,101,115,112,101,99,116,32,100,111,103,101,32,116,111,32,114,101,115,112,101,99,116,32,109,105,108,101,103,97,46])


def _safe_font(text):
    value = str(text or "")
    if value == _title:
        value = "AZAI WARNING"
    elif value == _old_line:
        value = "Clean language required. Respect do, respect milega."
    return _old_font(value)


_m.font = _safe_font
