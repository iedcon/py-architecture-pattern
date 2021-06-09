import abc
from allocation.domain import model


class AbstractProductRepository(abc.ABC):

    @abc.abstractmethod
    def add(self, batch: model.Batch):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, reference: str) -> model.Batch:
        raise NotImplementedError


class ProductRepository(AbstractProductRepository):
    def __init__(self, session):
        self.session = session

    def add(self, product: model.Product):
        self.session.add(product)

    def get(self, sku: str) -> model.Batch:
        return self.session.query(model.Product).filter_by(sku=sku).first()
