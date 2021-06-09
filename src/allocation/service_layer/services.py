from typing import List, Optional
from datetime import date
from allocation.domain import model
from allocation.adapters import repository
from allocation.service_layer import unit_of_work


class InvalidSku(Exception):
    pass


def is_valid_sku(sku: str, batches: List[model.Batch]) -> bool:
    return sku in {b.sku for b in batches}


def add_batch(
    ref: str, sku: str, qty: int, eta: Optional[date],
    uow: unit_of_work.AbstractUnitOfWork
):
    with uow:
        uow.batches.add(model.Batch(ref, sku, qty, eta))
        uow.commit()


def allocate(orderid: str, sku: str, qty: int, uow: unit_of_work.AbstractUnitOfWork) -> str:
    line = model.OrderLine(orderid, sku, qty)
    with uow:
        batches = uow.batches.list()
        if not is_valid_sku(line.sku, batches):
            raise InvalidSku(f'Invalid sku {line.sku}')
        batchref = model.allocate(line, batches)
        uow.commit()

    return batchref


def deallocate(orderid: str, sku: str, qty: int, ref: str, uow: unit_of_work.AbstractUnitOfWork):
    line = model.OrderLine(orderid, sku, qty)
    with uow:
        batch = uow.batches.get(ref)
        batch.deallocate(line)
        uow.commit()


def reallocate(orderid: str, sku: str, qty: int, uow: unit_of_work.AbstractUnitOfWork):
    line = model.OrderLine(orderid, sku, qty)
    with uow:
        batch = uow.batches.get_by_sku(sku=line.sku)
        if batch is None:
            raise InvalidSku(f'Invalid sku {line.sku}')
        batch.deallocate(line)
        batch.allocate(line)
        uow.commit()