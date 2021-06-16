from allocation.service_layer import unit_of_work

def allocations(orderid: str, uow: unit_of_work.ProductUnitOfWork):
    with uow:
        results = list(uow.session.execute(
            'SELECT sku, batchref FROM allocations_view WHERE orderid = :orderid',
            dict(orderid=orderid)
        ))
    return [dict(r) for r in results]