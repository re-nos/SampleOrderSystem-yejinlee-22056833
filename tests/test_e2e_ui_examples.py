"""UI_Console_Examples.md의 7개 예시 화면을 실제로 재현하는 E2E 테스트.

더미 데이터로 초기 상태를 구성한 뒤, 콘솔 입력을 스크립트로 주입해 다음 흐름을 검증한다.
  1. 메인 메뉴(시스템 현황판)
  2. 시료 관리 - 등록/목록
  3. 시료 주문 - 입력 내용 확인 후 접수
  4. 주문 승인/거절 - 번호 선택 -> 재고 확인 -> 승인(재고 부족 시 생산 등록)
  5. 모니터링 - 주문량 확인 / 재고량 확인
  6. 생산라인 조회 - 현재 처리 중 / 대기 목록
  7. 출고 처리 - 번호 선택 출고

실제 예시의 구체적인 수치(재고량, 주문번호 등)는 더미 데이터에 따라 달라지므로,
화면 구조와 핵심 문구(레이블/단위/흐름 순서)가 예시와 일치하는지를 검증한다.
"""

import os

import pytest

from sample_order_system import dummy_data
from sample_order_system.app import build_app
from sample_order_system.models.inventory import InventoryRecord
from sample_order_system.models.order import OrderStatus
from sample_order_system.repository.order_repository import OrderRepository

ENTER = ""


class ScriptedInput:
    def __init__(self, values):
        self._values = list(values)

    def __call__(self, prompt: str = "") -> str:
        return self._values.pop(0)


@pytest.fixture
def data_dir(tmp_path):
    path = os.path.join(tmp_path, "data")
    dummy_data.generate(sample_count=5, order_count=0, seed=1, data_dir=path)
    return path


def test_full_console_ui_walkthrough_matches_example_screens(data_dir):
    app = build_app(data_dir=data_dir)

    # "재고 충분" 시나리오(화면 7 출고 처리)를 재현하기 위해 별도 시료의 재고를 미리 채워둔다.
    # (등록 직후 재고는 항상 0이며, 정상적인 콘솔 메뉴만으로는 즉시 재고를 채울 수 없어 사전 설정한다)
    app.sample_controller.register_sample(
        sample_id="S-STOCK", name="재고여유 테스트 시료", avg_production_time=1.0, yield_rate=0.9
    )
    app.approval_controller._inventory_repo.update(
        InventoryRecord(sample_id="S-STOCK", quantity=1000)
    )

    outputs = []
    inputs = [
        # [화면 1] 메인 메뉴 -> [화면 2] 시료 관리 - 목록 조회
        "1", "2", ENTER,
        # [화면 2 연장] 시료 관리 - 신규 시료 등록
        "1", "1", "S-999", "테스트 시료", "0.5", "0.9", ENTER,
        # [화면 3] 시료 주문 - 입력 내용 확인 후 접수 (수량을 크게 주어 재고 부족을 확정)
        "2", "S-001", "삼성전자 파운드리", "999999", "Y", ENTER,
        # [화면 4] 주문 승인/거절 - 번호 선택 -> 재고 확인 -> 승인(재고 부족 -> PRODUCING)
        "3", "1", "Y", ENTER,
        # [화면 5] 모니터링 - 주문량 확인 / 재고량 확인
        "4", "1", ENTER,
        "4", "2", ENTER,
        # [화면 6] 생산라인 조회 - 현재 처리 중 / 대기 목록
        "5", "1", ENTER,
        "5", "2", ENTER,
        # 출고 처리(화면 7) 준비: 재고가 충분한 시료로 주문 접수 후 즉시 승인(CONFIRMED)
        "2", "S-STOCK", "LG이노텍", "10", "Y", ENTER,
        "3", "1", "Y", ENTER,
        # [화면 7] 출고 처리 - 번호 선택 출고
        "6", "1", ENTER,
        "0",
    ]

    app._input = ScriptedInput(inputs)
    app._output = outputs.append
    app.run()

    text = "\n".join(outputs)

    # 화면 1: 메인 메뉴 (시스템 현황판)
    assert "반도체 시료 생산주문관리 시스템" in text
    assert "등록 시료" in text and "종" in text
    assert "전체 주문" in text
    assert "생산라인" in text and "대기" in text
    assert "시료 관리" in text
    assert "출고 처리" in text

    # 화면 2: 시료 관리 - 목록 (단위 표시 포함)
    assert "등록 시료 목록" in text
    assert "min/ea" in text
    assert " ea" in text
    assert "시료 등록 완료" in text

    # 화면 3: 시료 주문 - 확인 단계 존재
    assert "입력 내용 확인" in text
    assert "예약 접수 완료" in text
    assert "RESERVED" in text

    # 화면 4: 주문 승인/거절 - 번호 선택 목록 + 재고 확인 + 부족분 + 실생산량
    assert "승인 대기 중인 예약 목록" in text
    assert "[1]" in text
    assert "부족분" in text
    assert "실생산량" in text
    assert "PRODUCING" in text

    # 화면 5: 모니터링 - 주문 현황 + 재고 현황
    assert "상태별 주문 현황" in text
    assert "재고 현황" in text
    assert any(status in text for status in ("여유", "부족", "고갈"))

    # 화면 6: 생산라인 - 진행률 + 완료 예정 시각 + 대기 목록
    assert "현재 처리 중" in text
    assert "% 진행" in text
    assert "완료 예정" in text
    assert "대기 중인 주문" in text or "대기 목록" in text or "없습니다" in text

    # 화면 7: 출고 처리 - 번호 선택 + 완료
    assert "출고 가능 주문" in text
    assert "출고 완료" in text
    assert "RELEASE" in text

    # 최종 데이터 정합성 확인
    order_repo = OrderRepository(file_path=os.path.join(data_dir, "order.json"))
    orders = order_repo.list()
    statuses = {o.status for o in orders}
    assert OrderStatus.PRODUCING in statuses
    assert OrderStatus.RELEASE in statuses


def test_main_menu_reflects_registered_samples_and_orders(data_dir):
    app = build_app(data_dir=data_dir)

    menu_before = app._render_main_menu()
    assert "등록 시료 5종" in menu_before

    app.sample_controller.register_sample(
        sample_id="S-999", name="추가 시료", avg_production_time=1.0, yield_rate=0.9
    )

    menu_after = app._render_main_menu()
    assert "등록 시료 6종" in menu_after
