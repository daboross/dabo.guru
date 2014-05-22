import json
import urllib.error
import urllib.parse

import requests

from azdweb import app

base_name_url = "https://account.minecraft.net/buy/frame/checkName/{}"
paid_url = "http://www.minecraft.net/haspaid.jsp"


class UserNotFound(Exception):
    pass


@app.route("/user-uuid/<username>")
def username_uuid(username):
    try:
        return json.dumps(get_profile(username), indent=1)
    except UserNotFound:
        return "User not found", 500


@app.route("/uuid-user/<uuid>")
def uuid_username(uuid):
    try:
        return json.dumps(get_profile(uuid), indent=1)
    except UserNotFound:
        return "User not found", 500


def is_taken(name):
    quoted_name = urllib.parse.quote_plus(name)
    response = requests.request("GET", base_name_url.format(quoted_name))

    if "OK" in response.text:
        return "free"
    elif "TAKEN" in response.text:
        return "taken"
    else:
        return "invalid"


def get_profile(username):
    data = request_profile(username)
    if len(data["profiles"]) < 1:
        raise UserNotFound
    user = data["profiles"][0]
    profile = {
        "name": user["name"],
        "id": user["id"],
        "legacy": user.get("legacy", False),
        "premium": is_paid(username)
    }
    return profile


def is_paid(username):
    return "true" in requests.get(paid_url, params={"user": username}).text


def request_profile(username):
    request = requests.post(
        "https://api.mojang.com/profiles/page/1",
        json.dumps({"name": username, "agent": "minecraft"}).encode(),
        headers={"Content-Type": "application/json"}
    )
    return request.json()
