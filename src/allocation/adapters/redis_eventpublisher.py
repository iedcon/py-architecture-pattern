from dataclasses import asdict
import redis
import logging
import json

from allocation import config
from allocation.domain import events

r = redis.Redis(**config.get_redis_host_and_port())

def publish(channel, event: events.Event):
    logging.debug('publishing: channel=%s, event=%s', channel, event)
    r.publish(channel, json.dumps(asdict(event)))