from typing import List

from sample_order_system.models.sample import Sample, SampleSummary


def format_sample_list(summaries: List[SampleSummary]) -> str:
    if not summaries:
        return "등록된 시료가 없습니다."

    lines = ["시료ID | 이름 | 평균생산시간 | 수율 | 재고"]
    for s in summaries:
        lines.append(
            f"{s.sample_id} | {s.name} | {s.avg_production_time} | {s.yield_rate} | {s.quantity}"
        )
    return "\n".join(lines)


def format_registration_success(sample: Sample) -> str:
    return f"시료 등록 완료: {sample.sample_id} ({sample.name})"
