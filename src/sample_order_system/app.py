import os

from sample_order_system.common.exceptions import DomainError
from sample_order_system.common.logging_config import setup_logging
from sample_order_system.controllers.approval_controller import ApprovalController
from sample_order_system.controllers.monitoring_controller import MonitoringController
from sample_order_system.controllers.order_controller import OrderController
from sample_order_system.controllers.production_controller import ProductionController
from sample_order_system.controllers.sample_controller import SampleController
from sample_order_system.controllers.shipment_controller import ShipmentController
from sample_order_system.repository.inventory_repository import InventoryRepository
from sample_order_system.repository.order_repository import OrderRepository
from sample_order_system.repository.production_queue_repository import (
    ProductionQueueRepository,
)
from sample_order_system.repository.sample_repository import SampleRepository
from sample_order_system.views.approval_view import format_approval_result
from sample_order_system.views.monitoring_view import (
    format_order_counts,
    format_stock_status_list,
)
from sample_order_system.views.order_view import format_order_registration_success
from sample_order_system.views.production_view import (
    format_current_job,
    format_turn_advance_result,
    format_waiting_jobs,
)
from sample_order_system.views.sample_view import (
    format_registration_success,
    format_sample_list,
)
from sample_order_system.views.shipment_view import format_release_result

MAIN_MENU_TEXT = """
==================== Sample Order System ====================
[1] 시료 관리
[2] 시료 주문
[3] 주문 승인/거절
[4] 모니터링
[5] 생산 라인
[6] 출고 처리
[0] 종료
===============================================================""".strip()


class App:
    """콘솔 메인 메뉴 진입점. 명령 처리 후 생산 라인을 1턴씩 자동 진행시킨다."""

    def __init__(
        self,
        sample_controller: SampleController,
        order_controller: OrderController,
        approval_controller: ApprovalController,
        production_controller: ProductionController,
        monitoring_controller: MonitoringController,
        shipment_controller: ShipmentController,
        input_func=input,
        output_func=print,
    ) -> None:
        self.sample_controller = sample_controller
        self.order_controller = order_controller
        self.approval_controller = approval_controller
        self.production_controller = production_controller
        self.monitoring_controller = monitoring_controller
        self.shipment_controller = shipment_controller
        self._input = input_func
        self._output = output_func

    def run(self) -> None:
        while True:
            self._output(MAIN_MENU_TEXT)
            choice = self._input("메뉴 선택> ").strip()
            if choice == "0":
                break

            try:
                self._dispatch(choice)
            except DomainError as e:
                self._output(f"오류: {e}")

            self._advance_turn()

    def _dispatch(self, choice: str) -> None:
        handlers = {
            "1": self._handle_sample,
            "2": self._handle_order,
            "3": self._handle_approval,
            "4": self._handle_monitoring,
            "5": self._handle_production,
            "6": self._handle_shipment,
        }
        handler = handlers.get(choice)
        if handler is None:
            self._output("잘못된 선택입니다.")
            return
        handler()

    def _advance_turn(self) -> None:
        completed = self.production_controller.advance_turns(1)
        self._output(format_turn_advance_result(completed))

    def _handle_sample(self) -> None:
        self._output("[1] 등록 [2] 목록 [3] 이름 검색")
        choice = self._input("선택> ").strip()

        if choice == "1":
            sample_id = self._input("시료 ID> ").strip()
            name = self._input("이름> ").strip()
            avg_production_time = float(self._input("평균 생산시간> ").strip())
            yield_rate = float(self._input("수율> ").strip())
            sample = self.sample_controller.register_sample(
                sample_id=sample_id,
                name=name,
                avg_production_time=avg_production_time,
                yield_rate=yield_rate,
            )
            self._output(format_registration_success(sample))
        elif choice == "2":
            self._output(format_sample_list(self.sample_controller.list_samples()))
        elif choice == "3":
            keyword = self._input("검색어> ").strip()
            self._output(format_sample_list(self.sample_controller.search_by_name(keyword)))
        else:
            self._output("잘못된 선택입니다.")

    def _handle_order(self) -> None:
        sample_id = self._input("시료 ID> ").strip()
        customer_name = self._input("고객명> ").strip()
        quantity = int(self._input("수량> ").strip())
        order = self.order_controller.place_order(
            sample_id=sample_id, customer_name=customer_name, quantity=quantity
        )
        self._output(format_order_registration_success(order))

    def _handle_approval(self) -> None:
        order_id = self._input("주문 ID> ").strip()
        decision = self._input("승인 [Y] / 거절 [N]> ").strip().upper()

        if decision == "Y":
            order = self.approval_controller.approve(order_id)
        else:
            order = self.approval_controller.reject(order_id)
        self._output(format_approval_result(order))

    def _handle_monitoring(self) -> None:
        self._output("[1] 상태별 건수 [2] 재고 현황")
        choice = self._input("선택> ").strip()

        if choice == "1":
            self._output(format_order_counts(self.monitoring_controller.count_by_status()))
        elif choice == "2":
            self._output(format_stock_status_list(self.monitoring_controller.stock_status()))
        else:
            self._output("잘못된 선택입니다.")

    def _handle_production(self) -> None:
        self._output("[1] 현재 작업 [2] 대기열")
        choice = self._input("선택> ").strip()

        if choice == "1":
            self._output(format_current_job(self.production_controller.current_job()))
        elif choice == "2":
            self._output(format_waiting_jobs(self.production_controller.waiting_jobs()))
        else:
            self._output("잘못된 선택입니다.")

    def _handle_shipment(self) -> None:
        order_id = self._input("주문 ID> ").strip()
        order = self.shipment_controller.release(order_id)
        self._output(format_release_result(order))


def build_app(data_dir: str = "data") -> App:
    sample_repo = SampleRepository(file_path=os.path.join(data_dir, "sample.json"))
    order_repo = OrderRepository(file_path=os.path.join(data_dir, "order.json"))
    inventory_repo = InventoryRepository(file_path=os.path.join(data_dir, "inventory.json"))
    production_queue_repo = ProductionQueueRepository(
        file_path=os.path.join(data_dir, "production_queue.json")
    )

    return App(
        sample_controller=SampleController(sample_repo, inventory_repo),
        order_controller=OrderController(sample_repo, order_repo),
        approval_controller=ApprovalController(
            sample_repo, order_repo, inventory_repo, production_queue_repo
        ),
        production_controller=ProductionController(
            order_repo, inventory_repo, production_queue_repo
        ),
        monitoring_controller=MonitoringController(sample_repo, inventory_repo, order_repo),
        shipment_controller=ShipmentController(order_repo),
    )


def main() -> None:
    setup_logging()
    build_app().run()


if __name__ == "__main__":
    main()
