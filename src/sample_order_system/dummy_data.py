import argparse
import random
import os

from sample_order_system.models.inventory import InventoryRecord
from sample_order_system.models.order import Order, OrderStatus
from sample_order_system.models.sample import Sample
from sample_order_system.repository.inventory_repository import InventoryRepository
from sample_order_system.repository.order_repository import OrderRepository
from sample_order_system.repository.sample_repository import SampleRepository

_CUSTOMER_NAMES = [
    "LG이노텍",
    "SK하이닉스",
    "삼성전자 파운드리",
    "DB하이텍",
    "고려대학교",
    "카이스트",
    "포항공대",
]

_SAMPLE_NAMES = [
    "실리콘 웨이퍼-8인치",
    "GaN 에피택셜-4인치",
    "SiC 파워기판-6인치",
    "포토레지스트-PR7",
    "산화막 웨이퍼-SiO2",
]

_ORDER_DATE = "20260416"


def generate(sample_count: int, order_count: int, seed: int, data_dir: str) -> None:
    rng = random.Random(seed)

    sample_repo = SampleRepository(file_path=os.path.join(data_dir, "sample.json"))
    inventory_repo = InventoryRepository(file_path=os.path.join(data_dir, "inventory.json"))
    order_repo = OrderRepository(file_path=os.path.join(data_dir, "order.json"))

    sample_ids = []
    for i in range(sample_count):
        sample_id = f"S-{i + 1:03d}"
        sample_ids.append(sample_id)
        base_name = _SAMPLE_NAMES[i % len(_SAMPLE_NAMES)]
        name = base_name if i < len(_SAMPLE_NAMES) else f"{base_name} ({i + 1})"

        sample_repo.add(
            Sample(
                sample_id=sample_id,
                name=name,
                avg_production_time=round(rng.uniform(0.2, 0.8), 1),
                yield_rate=round(rng.uniform(0.7, 0.95), 2),
            )
        )
        inventory_repo.add(InventoryRecord(sample_id=sample_id, quantity=rng.randint(0, 900)))

    for i in range(order_count):
        order_repo.add(
            Order(
                order_id=f"ORD-{_ORDER_DATE}-{i + 1:04d}",
                sample_id=rng.choice(sample_ids),
                customer_name=rng.choice(_CUSTOMER_NAMES),
                quantity=rng.randint(50, 300),
                status=OrderStatus.RESERVED,
                created_at="2026-04-16T09:00:00",
            )
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="더미 데이터 생성기")
    parser.add_argument("--samples", type=int, default=10)
    parser.add_argument("--orders", type=int, default=30)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--output-dir", type=str, default="data")
    args = parser.parse_args()

    generate(
        sample_count=args.samples,
        order_count=args.orders,
        seed=args.seed,
        data_dir=args.output_dir,
    )


if __name__ == "__main__":
    main()
