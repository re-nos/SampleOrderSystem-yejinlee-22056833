from sample_order_system.views.text_width import display_width, pad


def test_display_width_ascii():
    assert display_width("abc") == 3


def test_display_width_korean_counts_as_double():
    assert display_width("가나다") == 6


def test_display_width_mixed():
    assert display_width("ab가") == 4


def test_pad_adds_trailing_spaces_to_reach_width():
    result = pad("abc", 6)

    assert result == "abc   "


def test_pad_accounts_for_korean_display_width():
    result = pad("가나", 6)

    assert result == "가나  "


def test_pad_does_not_truncate_when_text_exceeds_width():
    result = pad("abcdef", 3)

    assert result == "abcdef"
