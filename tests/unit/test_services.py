from allocation.domain import model
from allocation.adapters import repository
from allocation.service_layer import services, unit_of_work
import pytest


class FakeRepository(repository.AbstractProductRepository):
    def __init__(self, products):
        super().__init__()
        self._products = set(products)

    def _add(self, product):
        self._products.add(product)

    def _get(self, sku):
        return next((p for p in self._products if p.sku == sku), None)


class FakeUnitOfWork(unit_of_work.AbstractProductUnitOfWork):
    def __init__(self):
        self.products = FakeRepository([])
        self.committed = False

    def _commit(self):
        self.committed = True

    def rollback(self):
        pass


def test_add_batch():
    uow = FakeUnitOfWork()
    services.add_batch("b1", "CRUNCHY-ARMCHAIR", 100, None, uow)
    assert uow.products.get("CRUNCHY-ARMCHAIR") is not None
    assert uow.committed


def test_returns_allocation():
    uow = FakeUnitOfWork()
    services.add_batch("b1", "COMPLICATED-LAMP", 100, None, uow)
    result = services.allocate("o1", "COMPLICATED-LAMP", 10, uow)

    assert result == "b1"


def test_error_for_invalid_sku():
    uow = FakeUnitOfWork()
    services.add_batch("b1", "AREALSKU", 100, None, uow)

    with pytest.raises(services.InvalidSku, match="Invalid sku NONEXISTENTSKU"):
        services.allocate("o1", "NONEXISTENTSKU", 10, uow)


def test_error_for_out_of_stock_sku():
    uow = FakeUnitOfWork()
    services.add_batch("b1", "AREALSKU", 10, None, uow)
    ref = services.allocate("o1", "AREALSKU", 20, uow)

    assert ref is None


def test_allocate_commits():
    uow = FakeUnitOfWork()
    services.add_batch('b1', 'OMINOUS-MIRROR', 100, None, uow)
    services.allocate('o1', 'OMINOUS-MIRROR', 10, uow)
    assert uow.committed is True


def test_deallocate():
    uow = FakeUnitOfWork()
    services.add_batch('b1', 'OMINOUS-MIRROR', 100, None, uow)
    ref = services.allocate('o1', 'OMINOUS-MIRROR', 10, uow)

    batch = services.deallocate('o1', 'OMINOUS-MIRROR', 10, ref, uow)
    assert batch.available_quantity == 100
