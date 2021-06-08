from typing import List, Optional
from datetime import date
from src.domain import model
from src.adapters import repository


class InvalidSku(Exception):
    pass


def is_valid_sku(sku: str, batches: List[model.Batch]) -> bool:
    print(batches)
    return sku in {b.sku for b in batches}


def add_batch(
    ref: str, sku: str, qty: int, eta: Optional[date],
    repo: repository.AbstractRepository, session,
) -> None:
    repo.add(model.Batch(ref, sku, qty, eta))
    session.commit()


def allocate(orderid: str, sku: str, qty: int, repo: repository.AbstractRepository, session) -> str:
    line = model.OrderLine(orderid, sku, qty)
    batches = repo.list()
    if not is_valid_sku(line.sku, batches):
        raise InvalidSku(f'Invalid sku {line.sku}')
    batchref = model.allocate(line, batches)
    session.commit()

    return batchref


def deallocate(orderid: str, sku: str, qty: int, batch: model.Batch, session):
    line = model.OrderLine(orderid, sku, qty)
    batch.deallocate(line)
    session.commit()