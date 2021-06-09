from flask import Flask, jsonify, request
from sqlalchemy import create_engine
from datetime import datetime

from allocation.domain import model
from allocation.adapters import orm
from allocation.service_layer import services, unit_of_work


orm.start_mappers()
app = Flask(__name__)

@app.route("/batches", methods=['POST'])
def add_batch():
    eta = request.json['eta']
    if eta is not None:
        eta = datetime.fromisoformat(eta).date()
    services.add_batch(
        request.json['ref'], 
        request.json['sku'], 
        request.json['qty'], 
        eta, 
        uow = unit_of_work.ProductUnitOfWork()
    )
    return 'OK', 201


@app.route("/allocate", methods=['POST'])
def allocate_endpoint():
    try:
        batchref = services.allocate(
            request.json['orderid'],
            request.json['sku'],
            request.json['qty'],
            unit_of_work.ProductUnitOfWork()
        )
    except (model.OutOfStock, services.InvalidSku) as e:
        return jsonify({'message': str(e)}), 400

    return jsonify({'batchref': batchref}), 201