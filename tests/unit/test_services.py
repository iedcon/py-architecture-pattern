from allocation.domain import model
from allocation.adapters import repository
from allocation.service_layer import services, unit_of_work
import pytest


class FakeRepository(repository.AbstractRepository):
    def __init__(self, batches):
        self._batches = set(batches)

    def add(self, batch):
        self._batches.add(batch)

    def get(self, reference):
        return next(b for b in self._batches if b.reference == reference)

    def get_by_sku(self, sku):
        return next(b for b in self._batches if b.sku == sku)

    def list(self):
        return list(self._batches)


class FakeUnitOfWork(unit_of_work.AbstractUnitOfWork):
    def __init__(self):
        self.batches = FakeRepository([])
        self.committed = False

    def commit(self):
        self.committed = True

    def rollback(self):
        pass


def test_add_batch():
    uow = FakeUnitOfWork()
    services.add_batch("b1", "CRUNCHY-ARMCHAIR", 100, None, uow)
    assert uow.batches.get("b1") is not None
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

    with pytest.raises(model.OutOfStock, match="Out of stock for sku AREALSKU"):
        services.allocate("o1", "AREALSKU", 20, uow)


def test_allocate_commits():
    uow = FakeUnitOfWork()
    services.add_batch('b1', 'OMINOUS-MIRROR', 100, None, uow)
    services.allocate('o1', 'OMINOUS-MIRROR', 10, uow)
    assert uow.committed is True


def test_deallocate():
    uow = FakeUnitOfWork()
    services.add_batch('b1', 'OMINOUS-MIRROR', 100, None, uow)
    services.allocate('o1', 'OMINOUS-MIRROR', 10, uow)

    batch = uow.batches.get('b1')
    assert batch.available_quantity == 90
    services.deallocate('o1', 'OMINOUS-MIRROR', 10, batch.reference, uow)
    assert batch.available_quantity == 100


def test_reallocate():
    uow = FakeUnitOfWork()
    services.add_batch('b1', 'OMINOUS-MIRROR', 100, None, uow)
    services.allocate('o1', 'OMINOUS-MIRROR', 10, uow)

    batch = uow.batches.get('b1')
    assert batch.available_quantity == 90
    services.reallocate('o1', 'OMINOUS-MIRROR', 10, uow)
    assert batch.available_quantity == 90