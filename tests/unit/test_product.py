from allocation.domain.model import Product, Batch, OrderLine, OutOfStock
from datetime import date, timedelta
import pytest


today = date.today()
tomorrow = today + timedelta(days=1)
later = today + timedelta(days=10)


def test_prefers_current_stock_batches_to_shipments():
    sku = "RETRO-CLOCK"
    in_stock_batch = Batch("in-stock-batch", sku, 100, eta=None)
    shipment_batch = Batch("shipment-batch", sku, 100, eta=tomorrow)
    product = Product(sku=sku, batches=[in_stock_batch, shipment_batch])
    line = OrderLine("oref", sku, 10)

    product.allocate(line)

    assert in_stock_batch.available_quantity == 90
    assert shipment_batch.available_quantity == 100


def test_prefers_earlier_batches():
    sku = "MINIMALIST-SPOON"
    earliest = Batch("speedy-batch", sku, 100, eta=today)
    medium = Batch("normal-batch", sku, 100, eta=tomorrow)
    latest = Batch("slow-batch", sku, 100, eta=later)
    product = Product(sku=sku, batches=[earliest, medium, latest])
    line = OrderLine("order1", sku, 10)

    product.allocate(line)

    assert earliest.available_quantity == 90
    assert medium.available_quantity == 100
    assert latest.available_quantity == 100


def test_returns_allocated_batch_ref():
    sku = "HIGHBROW-POSTER"
    in_stock_batch = Batch("in-stock-batch-ref", sku, 100, eta=None)
    shipment_batch = Batch("shipment-batch-ref", sku, 100, eta=tomorrow)
    product = Product(sku=sku, batches=[in_stock_batch, shipment_batch])
    line = OrderLine("oref", sku, 10)
    allocation = product.allocate(line)

    assert allocation == in_stock_batch.reference


def test_raises_out_of_stock_exception_if_cannot_allocate():
    sku = 'SMALL-FORK'
    batch = Batch('batch1', sku, 10, eta=today)
    product = Product(sku=sku, batches=[batch])
    product.allocate(OrderLine('order1', sku, 10))

    with pytest.raises(OutOfStock, match=sku):
        product.allocate(OrderLine('order2', sku, 1))