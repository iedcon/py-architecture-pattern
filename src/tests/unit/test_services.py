from src.domain import model
from src.adapters import repository
from src.service_layer import services
import pytest


class FakeRepository(repository.AbstractRepository):
    def __init__(self, batches):
        self._batches = set(batches)

    def add(self, batch):
        self._batches.add(batch)

    def get(self, reference):
        return next(b for b in self._batches if b.reference == reference)

    def list(self):
        return list(self._batches)


class FakeSession():
    committed = False

    def commit(self):
        self.committed = True


def test_add_batch():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch("b1", "CRUNCHY-ARMCHAIR", 100, None, repo, session)
    assert repo.get("b1") is not None
    assert session.committed


def test_returns_allocation():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch("b1", "COMPLICATED-LAMP", 100, None, repo, session)
    result = services.allocate("o1", "COMPLICATED-LAMP", 10, repo, session)

    assert result == "b1"


def test_error_for_invalid_sku():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch("b1", "AREALSKU", 100, None, repo, session)

    with pytest.raises(services.InvalidSku, match="Invalid sku NONEXISTENTSKU"):
        services.allocate("o1", "NONEXISTENTSKU", 10, repo, session)


def test_error_for_out_of_stock_sku():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch("b1", "AREALSKU", 10, None, repo, session)

    with pytest.raises(model.OutOfStock, match="Out of stock for sku AREALSKU"):
        services.allocate("o1", "AREALSKU", 20, repo, session)


def test_commits():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch('b1', 'OMINOUS-MIRROR', 100, None, repo, session)
    services.allocate('o1', 'OMINOUS-MIRROR', 10, repo, session)
    assert session.committed is True


def test_deallocate():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch('b1', 'OMINOUS-MIRROR', 100, None, repo, session)
    services.allocate('o1', 'OMINOUS-MIRROR', 10, repo, session)

    batch = repo.get('b1')
    assert batch.available_quantity == 90
    services.deallocate('o1', 'OMINOUS-MIRROR', 10, batch, session)
    assert batch.available_quantity == 100