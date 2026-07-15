from sample_order_system.views import colors


def test_colorize_wraps_text_with_color_and_reset():
    result = colors.colorize("hello", colors.SUCCESS)

    assert result == f"{colors.SUCCESS}hello{colors.RESET}"
    assert "hello" in result


def test_order_status_color_known_statuses():
    assert colors.order_status_color("RESERVED") == colors.Fore.BLUE
    assert colors.order_status_color("CONFIRMED") == colors.Fore.GREEN
    assert colors.order_status_color("REJECTED") == colors.Fore.RED


def test_order_status_color_unknown_status_returns_empty_string():
    assert colors.order_status_color("UNKNOWN") == ""


def test_stock_status_color_known_statuses():
    assert colors.stock_status_color("여유") == colors.Fore.GREEN
    assert colors.stock_status_color("부족") == colors.Fore.YELLOW
    assert colors.stock_status_color("고갈") == colors.Fore.RED


def test_stock_status_color_unknown_status_returns_empty_string():
    assert colors.stock_status_color("UNKNOWN") == ""
