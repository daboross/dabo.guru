#!/usr/bin/env python3
#
# Copyright 2014 Dabo Ross <http://www.daboross.net/>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import json
import os
import traceback
import sys

from flask import Flask, request

from pushbullet import PushBullet


def load_config():
    if os.path.isfile("config.json"):
        with open("config.json") as config_file:
            config = json.load(config_file)
    else:
        print("Config not found! Please copy config.default.json to config.json")
        sys.exit()
    return config


def setup():
    config = load_config()
    global api_key, device
    api_key = config["pushbullet"]["api-key"]
    device = config["pushbullet"]["device"]


push = PushBullet(api_key)
app = Flask(__name__)


@app.route("/notify", methods=["POST"])
def hello():
    # noinspection PyBroadException
    try:
        print("Web notice: " + request.data.decode())
        push.push_note(device, "Web Notice", request.data.decode())
        return """Success\n"""
    except Exception:
        traceback.print_exc()
        return """Failure\n"""


if __name__ == "__main__":
    setup()
    app.run(host="127.0.0.1", port=5445)