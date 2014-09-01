import json
from builtins import list

from flask.globals import request
import requests
from werkzeug.contrib.cache import RedisCache

from content import app

uuid_to_username_url = "https://sessionserver.mojang.com/session/minecraft/profile/"
username_to_uuid_url = "https://api.mojang.com/profiles/minecraft"

data_cache = RedisCache(key_prefix='dabo.guru:minecraft-api:')


class MojangError(Exception):
    def __init__(self, data):
        self.message = "{}: {}".format(data['error'], data['errorMessage'])

    def __str__(self):
        return self.message


@app.route("/name-uuid/", methods=["POST"])
def mc_api_uuid():
    data = request.get_json()
    if data is None:
        return "Invalid request: {}".format(request.data), 406
    if len(data) >= 100:
        return "Too many usernames", 406
    if not isinstance(data, list):
        return "Not a list", 406
    data = tuple(str(user) for user in data)
    try:
        return json.dumps(retrieve_uuids(data))
    except MojangError as e:
        return e.message, 500


@app.route("/uuid-name/", methods=["POST"])
def mc_api_name():
    data = request.get_json()
    if data is None:
        return "Invalid request", 406
    if len(data) >= 100:
        return "Too many uuids", 406
    if not isinstance(data, list):
        return "Not a list", 406
    return json.dumps(retrieve_names(data))


def id_to_uuid(uuid):
    return uuid[0:8] + "-" + uuid[8:12] + "-" + uuid[12:16] + "-" + uuid[16:20] + "-" + uuid[20:32]


def retrieve_uuids(names):
    cached = data_cache.get("uuids:{}".format(hash(names)))
    if cached is not None:
        return cached
    response = requests.post(
        username_to_uuid_url,
        json.dumps(names).encode(),
        headers={"Content-Type": "application/json"}
    )
    data = response.json()
    if "error" in data:
        raise MojangError(data)
    uuids = {}
    for profile in data:
        uuids[profile["name"]] = id_to_uuid(profile["id"])
    data_cache.set("uuids:{}".format(hash(names)), uuids, timeout=14400)
    return uuids


def retrieve_names(uuids):
    names = {}
    for uuid in uuids:
        cached = data_cache.get("names:{}".format(uuid))
        if cached is not None:
            names[uuid] = cached
            continue
        response = requests.get(uuid_to_username_url + uuid.replace("-", ""))
        data = response.json()
        if "name" in data:
            names[uuid] = data["name"]
            data_cache.set("names:{}".format(uuid), data["name"], timeout=14400)
    return names
