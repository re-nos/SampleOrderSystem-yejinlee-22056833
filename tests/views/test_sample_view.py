from sample_order_system.models.sample import Sample, SampleSummary
from sample_order_system.views import colors
from sample_order_system.views.sample_view import (
    format_registration_success,
    format_sample_list,
)


def test_format_sample_list_empty_shows_guidance_message():
    result = format_sample_list([])

    assert "없습니다" in result


def test_format_sample_list_includes_all_fields():
    summaries = [
        SampleSummary(
            sample_id="S001",
            name="시료A",
            avg_production_time=3.5,
            yield_rate=0.8,
            quantity=5,
        )
    ]

    result = format_sample_list(summaries)

    assert "S001" in result
    assert "시료A" in result
    assert "3.5" in result
    assert "0.8" in result
    assert "5" in result


def test_format_registration_success_includes_sample_info():
    sample = Sample(sample_id="S001", name="시료A", avg_production_time=3.5, yield_rate=0.8)

    result = format_registration_success(sample)

    assert "S001" in result
    assert "시료A" in result


def test_format_registration_success_uses_success_color():
    sample = Sample(sample_id="S001", name="시료A", avg_production_time=3.5, yield_rate=0.8)

    result = format_registration_success(sample)

    assert result.startswith(colors.SUCCESS)
    assert result.endswith(colors.RESET)


def test_format_sample_list_header_is_aligned_and_colored():
    summaries = [
        SampleSummary(
            sample_id="S001", name="시료A", avg_production_time=3.5, yield_rate=0.8, quantity=5
        )
    ]

    result = format_sample_list(summaries)
    lines = result.splitlines()

    assert lines[0].startswith(colors.HEADER)
    assert "총 1종" in lines[0]
    assert lines[1].startswith(colors.HEADER)
    assert "ID" in lines[1]

    data_line = lines[3]
    assert data_line.index("시료A") == 8  # id 컬럼 폭(8) 뒤에 이름 컬럼 시작


def test_format_sample_list_shows_units():
    summaries = [
        SampleSummary(
            sample_id="S001", name="시료A", avg_production_time=3.5, yield_rate=0.8, quantity=5
        )
    ]

    result = format_sample_list(summaries)

    assert "min/ea" in result
    assert "5 ea" in result
