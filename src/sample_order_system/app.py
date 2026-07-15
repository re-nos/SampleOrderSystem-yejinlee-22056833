import os
from datetime import datetime

from sample_order_system.common.exceptions import DomainError, ValidationError
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
from sample_order_system.views import colors
from sample_order_system.views.approval_view import (
    format_approval_result,
    format_pending_orders,
    format_stock_check,
)
from sample_order_system.views.monitoring_view import (
    format_order_counts,
    format_stock_status_list,
)
from sample_order_system.views.order_view import (
    format_order_cancelled,
    format_order_confirmation,
    format_order_registration_success,
)
from sample_order_system.views.production_view import (
    format_current_job_detail,
    format_turn_advance_result,
    format_waiting_job_details,
)
from sample_order_system.views.sample_view import (
    format_registration_success,
    format_sample_list,
)
from sample_order_system.views.shipment_view import (
    format_release_result,
    format_releasable_orders,
)
from sample_order_system.views.text_width import pad

_SEPARATOR = "-" * 55
_MENU_COL_WIDTH = 24


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
            self._output(self._render_main_menu())
            choice = self._prompt("선택> ").strip()

            if choice == "0":
                self._output(colors.colorize("시스템을 종료합니다.", colors.SUCCESS))
                break

            handler = self._handlers().get(choice)
            if handler is None:
                self._output(colors.colorize("[오류] 올바른 메뉴 번호를 입력하세요.", colors.ERROR))
                continue

            try:
                handler()
            except DomainError as e:
                self._output(colors.colorize(f"[오류] {e}", colors.ERROR))

            self._advance_turn()
            self._wait_for_return_to_menu()

    def _handlers(self) -> dict:
        return {
            "1": self._handle_sample,
            "2": self._handle_order,
            "3": self._handle_approval,
            "4": self._handle_monitoring,
            "5": self._handle_production,
            "6": self._handle_shipment,
        }

    def _prompt(self, message: str) -> str:
        return self._input(colors.colorize(message, colors.PROMPT))

    def _select_by_number(self, items: list, prompt: str):
        raw = self._prompt(prompt).strip()
        try:
            index = int(raw) - 1
        except ValueError:
            raise ValidationError("올바른 번호를 입력하세요.")
        if index < 0 or index >= len(items):
            raise ValidationError("존재하지 않는 번호입니다.")
        return items[index]

    def _render_main_menu(self) -> str:
        samples = self.sample_controller.list_samples()
        total_stock = sum(s.quantity for s in samples)
        total_orders = sum(self.monitoring_controller.count_by_status().values())
        waiting_count = len(self.production_controller.waiting_jobs())
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        sep = colors.colorize(_SEPARATOR, colors.SEPARATOR)
        lines = [
            colors.colorize("반도체 시료 생산주문관리 시스템", colors.TITLE),
            sep,
            f"시스템 현황 {now}",
            "",
            f"등록 시료 {len(samples)}종 | 총 재고 {total_stock} ea",
            f"전체 주문 {total_orders}건 | 생산라인 {waiting_count}건 대기",
            sep,
            self._menu_row("1", "시료 관리", "2", "시료 주문"),
            self._menu_row("3", "주문 승인/거절", "4", "모니터링"),
            self._menu_row("5", "생산라인 조회", "6", "출고 처리"),
            self._menu_item("0", "종료"),
            sep,
        ]
        return "\n".join(lines)

    @staticmethod
    def _menu_item(num: str, label: str) -> str:
        return f"{colors.colorize(f'[{num}]', colors.HEADER)} {label}"

    @classmethod
    def _menu_row(cls, num1: str, label1: str, num2: str, label2: str) -> str:
        left_plain = f"[{num1}] {label1}"
        left = pad(left_plain, _MENU_COL_WIDTH).replace(
            f"[{num1}]", colors.colorize(f"[{num1}]", colors.HEADER), 1
        )
        right = cls._menu_item(num2, label2)
        return f"{left}{right}"

    def _advance_turn(self) -> None:
        completed = self.production_controller.advance_turns(1)
        if completed:
            self._output(format_turn_advance_result(completed))

    def _wait_for_return_to_menu(self) -> None:
        self._output("")
        self._prompt("[메뉴로 돌아가기] Enter 키를 누르세요...")

    def _handle_sample(self) -> None:
        self._output("[1] 시료 등록 [2] 시료 목록 [3] 시료 검색 [0] 뒤로")
        choice = self._prompt("선택> ").strip()

        if choice == "1":
            sample_id = self._prompt("시료 ID> ").strip()
            name = self._prompt("시료명> ").strip()
            avg_production_time = float(self._prompt("평균 생산시간> ").strip())
            yield_rate = float(self._prompt("수율> ").strip())
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
            keyword = self._prompt("검색어> ").strip()
            self._output(format_sample_list(self.sample_controller.search_by_name(keyword)))
        elif choice == "0":
            return
        else:
            self._output(colors.colorize("[오류] 올바른 메뉴 번호를 입력하세요.", colors.ERROR))

    def _handle_order(self) -> None:
        sample_id = self._prompt("시료 ID> ").strip()
        sample_summary = self.sample_controller.get_summary(sample_id)

        customer_name = self._prompt("고객명> ").strip()
        quantity = int(self._prompt("주문 수량> ").strip())

        self._output(format_order_confirmation(sample_summary, customer_name, quantity))
        decision = self._prompt("[Y] 예약 접수 [N] 취소> ").strip().upper()

        if decision != "Y":
            self._output(format_order_cancelled())
            return

        order = self.order_controller.place_order(
            sample_id=sample_id, customer_name=customer_name, quantity=quantity
        )
        self._output(format_order_registration_success(order))

    def _handle_approval(self) -> None:
        pending = self.approval_controller.list_pending_orders()
        self._output(format_pending_orders(pending))
        if not pending:
            return

        order = self._select_by_number(pending, "승인할 번호> ")
        check = self.approval_controller.check_stock(order.order_id)
        self._output(format_stock_check(check))

        decision = self._prompt("[Y] 승인 [N] 주문 거절> ").strip().upper()
        if decision == "Y":
            result = self.approval_controller.approve(order.order_id)
        else:
            result = self.approval_controller.reject(order.order_id)
        self._output(format_approval_result(result))

    def _handle_monitoring(self) -> None:
        self._output("[1] 주문량 확인 [2] 재고량 확인 [0] 뒤로")
        choice = self._prompt("선택> ").strip()

        if choice == "1":
            self._output(format_order_counts(self.monitoring_controller.count_by_status()))
        elif choice == "2":
            self._output(format_stock_status_list(self.monitoring_controller.stock_status()))
        elif choice == "0":
            return
        else:
            self._output(colors.colorize("[오류] 올바른 메뉴 번호를 입력하세요.", colors.ERROR))

    def _handle_production(self) -> None:
        self._output("[1] 현재 처리 중 [2] 대기 목록 [0] 뒤로")
        choice = self._prompt("선택> ").strip()

        if choice == "1":
            self._output(format_current_job_detail(self.production_controller.current_job_detail()))
        elif choice == "2":
            current = self.production_controller.current_job_detail()
            base_remaining = current.remaining_turns if current else 0
            details = self.production_controller.waiting_job_details()
            self._output(format_waiting_job_details(details, base_remaining))
        elif choice == "0":
            return
        else:
            self._output(colors.colorize("[오류] 올바른 메뉴 번호를 입력하세요.", colors.ERROR))

    def _handle_shipment(self) -> None:
        releasable = self.shipment_controller.list_releasable_orders()
        self._output(format_releasable_orders(releasable))
        if not releasable:
            return

        order = self._select_by_number(releasable, "출고할 번호> ")
        result = self.shipment_controller.release(order.order_id)
        self._output(format_release_result(result))


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
            order_repo, inventory_repo, production_queue_repo, sample_repo
        ),
        monitoring_controller=MonitoringController(sample_repo, inventory_repo, order_repo),
        shipment_controller=ShipmentController(order_repo),
    )


def main() -> None:
    setup_logging()
    build_app().run()


if __name__ == "__main__":
    main()
