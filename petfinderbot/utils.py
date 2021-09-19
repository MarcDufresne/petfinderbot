_CHARS_TO_ESCAPE = ["_", "*", "[", "]", "(", ")", "~", "`", ">", "#", "+", "-", "=", "|", "{", "}", ".", "!"]
_REPLACEMENTS = {c: "\\" + c for c in _CHARS_TO_ESCAPE}


def escape_telegram_text(text: str) -> str:
    return "".join([_REPLACEMENTS.get(c, c) for c in text])
