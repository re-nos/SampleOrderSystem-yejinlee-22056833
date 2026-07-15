import os

from sample_order_system.dummy_data import generate
from sample_order_system.repository.inventory_repository import InventoryRepository
from sample_order_system.repository.order_repository import OrderRepository
from sample_order_system.repository.sample_repository import SampleRepository


def _repos(data_dir):
    return (
        SampleRepository(file_path=os.path.join(data_dir, "sample.json")),
        InventoryRepository(file_path=os.path.join(data_dir, "inventory.json")),
        OrderRepository(file_path=os.path.join(data_dir, "order.json")),
    )


def test_generate_creates_requested_counts(tmp_path):
    data_dir = os.path.join(tmp_path, "data")

    generate(sample_count=5, order_count=12, seed=42, data_dir=data_dir)

    sample_repo, inventory_repo, order_repo = _repos(data_dir)
    assert len(sample_repo.list()) == 5
    assert len(order_repo.list()) == 12
    assert len(inventory_repo.list()) == 5


def test_generate_orders_reference_existing_samples(tmp_path):
    data_dir = os.path.join(tmp_path, "data")

    generate(sample_count=3, order_count=10, seed=1, data_dir=data_dir)

    sample_repo, _, order_repo = _repos(data_dir)
    sample_ids = {s.sample_id for s in sample_repo.list()}

    assert all(order.sample_id in sample_ids for order in order_repo.list())


def test_generate_orders_are_all_reserved(tmp_path):
    data_dir = os.path.join(tmp_path, "data")

    generate(sample_count=2, order_count=5, seed=7, data_dir=data_dir)

    _, _, order_repo = _repos(data_dir)

    from sample_order_system.models.order import OrderStatus

    assert all(order.status is OrderStatus.RESERVED for order in order_repo.list())


def test_generate_uses_ui_example_style_sample_names_and_ids(tmp_path):
    data_dir = os.path.join(tmp_path, "data")

    generate(sample_count=5, order_count=3, seed=1, data_dir=data_dir)

    sample_repo, _, order_repo = _repos(data_dir)
    samples = sample_repo.list()

    assert samples[0].sample_id == "S-001"
    assert "웨이퍼" in samples[0].name or "에피택셜" in samples[0].name or "기판" in samples[0].name
    assert all(order.order_id.startswith("ORD-") for order in order_repo.list())


def test_generate_is_reproducible_with_same_seed(tmp_path):
    data_dir_a = os.path.join(tmp_path, "a")
    data_dir_b = os.path.join(tmp_path, "b")

    generate(sample_count=4, order_count=8, seed=99, data_dir=data_dir_a)
    generate(sample_count=4, order_count=8, seed=99, data_dir=data_dir_b)

    sample_repo_a, inventory_repo_a, order_repo_a = _repos(data_dir_a)
    sample_repo_b, inventory_repo_b, order_repo_b = _repos(data_dir_b)

    assert sample_repo_a.list() == sample_repo_b.list()
    assert inventory_repo_a.list() == inventory_repo_b.list()
    assert order_repo_a.list() == order_repo_b.list()
