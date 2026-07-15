from colorama import Fore, Style

RESET = Style.RESET_ALL
TITLE = Fore.CYAN + Style.BRIGHT
SEPARATOR = Fore.CYAN
HEADER = Fore.CYAN + Style.BRIGHT
SUCCESS = Fore.GREEN
ERROR = Fore.RED + Style.BRIGHT
PROMPT = Fore.CYAN

_ORDER_STATUS_COLORS = {
    "RESERVED": Fore.BLUE,
    "PRODUCING": Fore.YELLOW,
    "CONFIRMED": Fore.GREEN,
    "RELEASE": Fore.MAGENTA,
    "REJECTED": Fore.RED,
}

_STOCK_STATUS_COLORS = {
    "여유": Fore.GREEN,
    "부족": Fore.YELLOW,
    "고갈": Fore.RED,
}


def colorize(text: str, color: str) -> str:
    return f"{color}{text}{RESET}"


def order_status_color(status: str) -> str:
    return _ORDER_STATUS_COLORS.get(status, "")


def stock_status_color(status: str) -> str:
    return _STOCK_STATUS_COLORS.get(status, "")
