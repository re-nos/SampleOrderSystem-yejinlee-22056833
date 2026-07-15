import os

import pytest

from sample_order_system.app import build_app
from sample_order_system.models.order import OrderStatus
from sample_order_system.repository.order_repository import OrderRepository
from sample_order_system.repository.production_queue_repository import (
    ProductionQueueRepository,
)
from sample_order_system.repository.sample_repository import SampleRepository

ENTER = ""  # "[메뉴로 돌아가기]" 확인 프롬프트에 대한 입력


class ScriptedInput:
    def __init__(self, values):
        self._values = list(values)

    def __call__(self, prompt: str = "") -> str:
        return self._values.pop(0)


def _run_app(tmp_path, inputs):
    data_dir = os.path.join(tmp_path, "data")
    outputs = []
    app = build_app(data_dir=data_dir)
    app._input = ScriptedInput(inputs)
    app._output = outputs.append
    app.run()
    return app, outputs, data_dir


def test_exits_immediately_on_zero(tmp_path):
    _, outputs, _ = _run_app(tmp_path, ["0"])

    assert any("종료" in o or "Sample Order System" in o for o in outputs)


def test_invalid_main_menu_choice_does_not_require_return_confirmation(tmp_path):
    # 잘못된 메뉴 선택은 턴 진행/복귀 확인 없이 바로 메인 메뉴로 돌아간다 (추가 입력 불필요)
    _, outputs, _ = _run_app(tmp_path, ["9", "0"])

    assert any("오류" in o for o in outputs)


def test_register_sample_flow(tmp_path):
    _, outputs, data_dir = _run_app(
        tmp_path, ["1", "1", "S001", "시료A", "3.5", "0.8", ENTER, "0"]
    )

    assert any("S001" in o and "시료A" in o for o in outputs)
    sample_repo = SampleRepository(file_path=os.path.join(data_dir, "sample.json"))
    assert sample_repo.get("S001").name == "시료A"


def test_place_order_flow(tmp_path):
    _, outputs, data_dir = _run_app(
        tmp_path,
        ["1", "1", "S001", "시료A", "3.5", "0.8", ENTER, "2", "S001", "고객A", "10", ENTER, "0"],
    )

    assert any("O001" in o for o in outputs)
    order_repo = OrderRepository(file_path=os.path.join(data_dir, "order.json"))
    assert order_repo.get("O001").status is OrderStatus.RESERVED


def test_approve_order_with_insufficient_stock_starts_production(tmp_path):
    _, outputs, data_dir = _run_app(
        tmp_path,
        [
            "1", "1", "S001", "시료A", "3.5", "0.8", ENTER,  # 시료 등록 (재고 0)
            "2", "S001", "고객A", "10", ENTER,                # 주문 접수
            "3", "O001", "Y", ENTER,                          # 승인 (재고부족 -> PRODUCING)
            "0",
        ],
    )

    assert any("PRODUCING" in o for o in outputs)


def test_reject_order_flow(tmp_path):
    _, outputs, data_dir = _run_app(
        tmp_path,
        [
            "1", "1", "S001", "시료A", "3.5", "0.8", ENTER,
            "2", "S001", "고객A", "10", ENTER,
            "3", "O001", "N", ENTER,
            "0",
        ],
    )

    assert any("REJECTED" in o for o in outputs)
    order_repo = OrderRepository(file_path=os.path.join(data_dir, "order.json"))
    assert order_repo.get("O001").status is OrderStatus.REJECTED


def test_monitoring_flow_shows_counts(tmp_path):
    _, outputs, _ = _run_app(tmp_path, ["4", "1", ENTER, "0"])

    assert any("RESERVED" in o for o in outputs)


def test_monitoring_flow_shows_stock_status(tmp_path):
    _, outputs, _ = _run_app(
        tmp_path, ["1", "1", "S001", "시료A", "3.5", "0.8", ENTER, "4", "2", ENTER, "0"]
    )

    assert any("S001" in o for o in outputs)


def test_production_flow_shows_current_job_none(tmp_path):
    _, outputs, _ = _run_app(tmp_path, ["5", "1", ENTER, "0"])

    assert any("없습니다" in o for o in outputs)


def test_shipment_after_immediate_confirmation(tmp_path):
    data_dir = os.path.join(tmp_path, "data")
    app = build_app(data_dir=data_dir)

    # 사전 조건: 재고를 충분히 채워 승인 시 즉시 CONFIRMED가 되도록 함
    app.sample_controller.register_sample(
        sample_id="S001", name="시료A", avg_production_time=3.5, yield_rate=0.8
    )
    from sample_order_system.models.inventory import InventoryRecord

    app.approval_controller._inventory_repo.update(
        InventoryRecord(sample_id="S001", quantity=100)
    )
    order = app.order_controller.place_order(sample_id="S001", customer_name="고객A", quantity=10)
    app.approval_controller.approve(order.order_id)

    outputs = []
    app._input = ScriptedInput(["6", order.order_id, ENTER, "0"])
    app._output = outputs.append
    app.run()

    assert any("RELEASE" in o for o in outputs)


def test_invalid_sample_id_shows_error_without_crashing(tmp_path):
    _, outputs, _ = _run_app(tmp_path, ["2", "UNKNOWN", "고객A", "10", ENTER, "0"])

    assert any("오류" in o for o in outputs)


def test_advances_one_turn_after_each_command(tmp_path):
    data_dir = os.path.join(tmp_path, "data")
    app = build_app(data_dir=data_dir)

    app.sample_controller.register_sample(
        sample_id="S001", name="시료A", avg_production_time=0.5, yield_rate=1.0
    )
    order = app.order_controller.place_order(sample_id="S001", customer_name="고객A", quantity=1)
    app.approval_controller.approve(order.order_id)  # 재고 0 -> PRODUCING, total_turns=1

    production_queue_repo = ProductionQueueRepository(
        file_path=os.path.join(data_dir, "production_queue.json")
    )
    assert production_queue_repo.get(order.order_id).remaining_turns == 1

    outputs = []
    app._input = ScriptedInput(["4", "1", ENTER, "0"])  # 아무 명령이나 1회 수행
    app._output = outputs.append
    app.run()

    assert any("생산 완료" in o for o in outputs)
    with pytest.raises(Exception):
        production_queue_repo.get(order.order_id)  # 완료되어 큐에서 제거됨


def test_turn_advance_message_hidden_when_nothing_completed(tmp_path):
    _, outputs, _ = _run_app(tmp_path, ["4", "1", ENTER, "0"])

    assert not any("완료된 생산 작업이 없습니다" in o for o in outputs)
