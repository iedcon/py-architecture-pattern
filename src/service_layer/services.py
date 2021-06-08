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


def allocate(line: model.OrderLine, repo: repository.AbstractRepository, session) -> str:
    batches = repo.list()
    if not is_valid_sku(line.sku, batches):
        raise InvalidSku(f'Invalid sku {line.sku}')
    batchref = model.allocate(line, batches)
    session.commit()

    return batchref


def deallocate(line: model.OrderLine, batch: model.Batch, session):
    batch.deallocate(line)