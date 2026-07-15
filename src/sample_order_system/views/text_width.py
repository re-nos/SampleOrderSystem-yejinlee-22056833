import unicodedata


def display_width(text: str) -> int:
    """한글 등 전각(East Asian Wide/Fullwidth) 문자를 2칸으로 계산한 터미널 표시 폭."""
    width = 0
    for ch in text:
        width += 2 if unicodedata.east_asian_width(ch) in ("F", "W") else 1
    return width


def pad(text: str, width: int) -> str:
    """전각 문자를 고려해 지정한 표시 폭에 맞도록 오른쪽에 공백을 채운다."""
    return text + " " * max(0, width - display_width(text))
