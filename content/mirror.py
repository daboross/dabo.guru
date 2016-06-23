# This is a backend for turt2live's uuid.turt2live.com api
import json
import logging
import time

from flask import request
from redis.client import StrictRedis
import requests

from content import app, redis

a = 3
# How long to keep logs for, in seconds
keep_log_for = 600
# How many requests per 10 minutes
maximum_requests = 600
requests_key = "dabo.guru:mirror:log"
username_url = "https://sessionserver.mojang.com/session/minecraft/profile/"
uuid_url = "https://api.mojang.com/profiles/minecraft"


def get_handled_requests(seconds=keep_log_for):
    current = time.time()
    max_keep = current - keep_log_for
    min_get = current - seconds
    pipe = redis.pipeline()
    pipe.zremrangebyscore(requests_key, '-inf', '({}'.format(max_keep))
    pipe.zcount(requests_key, '({}'.format(min_get), 'inf')
    deleted, count = pipe.execute()
    return int(count)


def add_request():
    logging.info("Adding request")
    current = time.time()
    max_keep = current - keep_log_for
    pipe = redis.pipeline()
    pipe.zremrangebyscore(requests_key, '-inf', '({}'.format(max_keep))
    pipe.zadd(requests_key, current, current)
    pipe.execute()


class MojangError(Exception):
    def __init__(self, message):
        self.message = "error: {}".format(message)

    def __str__(self):
        return self.message


def get_uuid(name):
    response = requests.post(
        uuid_url,
        json.dumps([name]).encode(),
        headers={"Content-Type": "application/json"}
    )
    try:
        data = response.json()
    except ValueError:
        raise MojangError("session server did not return a result")

    if 'error' in data:
        raise MojangError("{}: {}".format(data['error'], data['errorMessage']))

    for profile in data:
        if profile['name'].lower() == name.lower():
            return profile['id']
    raise MojangError("session server did not return a result")


def get_name(uuid):
    response = requests.get(username_url + uuid.replace('-', ''))
    try:
        data = response.json()
    except ValueError:
        raise MojangError("session server did not return a result")
    if 'error' in data:
        raise MojangError("{}: {}".format(data['error'], data['errorMessage']))

    if 'name' in data:
        return data['name']

    raise MojangError("session server did not return a result")


@app.route("/turt2live-uuid-mirror")
def uuid_api():
    if 'check' in request.args:
        if 'minutes' in request.args:
            try:
                minutes = float(request.args['minutes'])
            except ValueError:
                return 'error: invalid arguments', 400
            handled = get_handled_requests(60 * minutes)
        else:
            handled = get_handled_requests()
        return json.dumps(dict(maximum=maximum_requests, handled=handled))

    try:
        if 'uuid' in request.args:
            result = get_uuid(request.args['uuid'])
        elif 'name' in request.args:
            result = get_name(request.args['name'])
        else:
            return 'error: invalid arguments', 400
    except MojangError as e:
        return e.message, 400

    add_request()
    return json.dumps(dict(result=result))
