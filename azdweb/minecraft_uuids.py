import json
from builtins import list
import logging

from flask.globals import request
import requests

from azdweb import app

user_api_url = "https://sessionserver.mojang.com/session/minecraft/profile/"
uuid_api_url = "https://api.mojang.com/profiles/minecraft/"


class MojangError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


@app.route("/name-uuid/", methods=["POST"])
def name_to_uuid_page():
    data = request.get_json()
    if data is None:
        return "Invalid request", 406
    if len(data) >= 100:
        return "Too many usernames", 406
    if not isinstance(data, list):
        return "Not a list", 406
    data = [str(user) for user in data]
    try:
        return json.dumps(retrieve_uuids(data))
    except MojangError as e:
        return e.message, 500


@app.route("/uuid-name/", methods=["POST"])
def uuid_to_name_page():
    data = request.get_json()
    if data is None:
        return "Invalid request", 406
    if len(data) >= 100:
        return "Too many uuids", 406
    if not isinstance(data, list):
        return "Not a list", 406
    return json.dumps(retrieve_usernames(data))


def id_to_uuid(uuid):
    return uuid[0:8] + "-" + uuid[8:12] + "-" + uuid[12:16] + "-" + uuid[16:20] + "-" + uuid[20:32]


def retrieve_uuids(names):
    logging.info("Names: {}".format(names))
    response = requests.post(
        uuid_api_url,
        json.dumps(names).encode(),
        headers={"Content-Type": "application/json"}
    )
    data = response.json()
    logging.info("Data: {}".format(data))
    if "error" in data:
        raise MojangError(data["error"])
    uuids = {}
    for profile in data:
        uuids[profile["name"]] = id_to_uuid(profile["id"])

    return uuids


def retrieve_usernames(uuids):
    names = {}
    for uuid in uuids:
        response = requests.get(user_api_url + uuid.replace("-", ""))
        data = response.json()
        if "name" in data:
            names[uuid] = data["name"]
    return names