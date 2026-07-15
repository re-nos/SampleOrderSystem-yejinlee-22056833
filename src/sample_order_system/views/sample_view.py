from typing import List

from sample_order_system.models.sample import Sample, SampleSummary
from sample_order_system.views import colors
from sample_order_system.views.text_width import pad

_SEPARATOR = "-" * 71

_COLS = {"id": 8, "name": 16, "avg_time": 14, "yield_rate": 8, "quantity": 8}


def format_sample_list(summaries: List[SampleSummary]) -> str:
    if not summaries:
        return "등록된 시료가 없습니다."

    header = (
        pad("시료ID", _COLS["id"])
        + pad("이름", _COLS["name"])
        + pad("평균생산시간", _COLS["avg_time"])
        + pad("수율", _COLS["yield_rate"])
        + pad("재고", _COLS["quantity"])
    )

    lines = [colors.colorize(header, colors.HEADER), colors.colorize(_SEPARATOR, colors.SEPARATOR)]
    for s in summaries:
        row = (
            pad(s.sample_id, _COLS["id"])
            + pad(s.name, _COLS["name"])
            + pad(str(s.avg_production_time), _COLS["avg_time"])
            + pad(str(s.yield_rate), _COLS["yield_rate"])
            + pad(str(s.quantity), _COLS["quantity"])
        )
        lines.append(row)
    return "\n".join(lines)


def format_registration_success(sample: Sample) -> str:
    return colors.colorize(f"시료 등록 완료: {sample.sample_id} ({sample.name})", colors.SUCCESS)
