from flask import Flask, jsonify, request
from sqlalchemy import create_engine
from datetime import datetime

from allocation.domain import model, events
from allocation.adapters import orm
from allocation.service_layer import messagebus, unit_of_work
from allocation.service_layer.handlers import InvalidSku


app = Flask(__name__)
orm.start_mappers()

@app.route("/batches", methods=['POST'])
def add_batch():
    eta = request.json['eta']
    if eta is not None:
        eta = datetime.fromisoformat(eta).date()
    event = events.BatchCreated(
        request.json['ref'], 
        request.json['sku'], 
        request.json['qty'], 
        eta
    )
    messagebus.handle(event, unit_of_work.ProductUnitOfWork())
    return 'OK', 201


@app.route("/allocate", methods=['POST'])
def allocate_endpoint():
    try:
        event = events.AllocationRequired(
            request.json['orderid'],
            request.json['sku'],
            request.json['qty'],
        )
        results = messagebus.handle(event, unit_of_work.ProductUnitOfWork())
        batchref = results.pop(0)
    except InvalidSku as e:
        return jsonify({'message': str(e)}), 400

    return jsonify({'batchref': batchref}), 201