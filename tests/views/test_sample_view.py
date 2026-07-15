from sample_order_system.models.sample import Sample, SampleSummary
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
