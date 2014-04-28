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
import base64
import json
import os
import traceback
import sys

from flask import Flask, request

from pushbullet import PushBullet

if os.path.isfile("config.json"):
    with open("config.json") as config_file:
        config = json.load(config_file)
else:
    print("Config not found! Please copy config.default.json to config.json")
    sys.exit()

# get api_key and device
api_key = config["pushbullet"]["api-key"]
device = config["pushbullet"]["device"]

# create app
push = PushBullet(api_key)
app = Flask(__name__)

with open(os.path.join("templates", "oauth-template.html")) as oauth_template_file:
    oauth_template = oauth_template_file.read()


# noinspection PyBroadException
@app.route("/notify", methods=["POST"])
def notify_respond():
    try:
        print("Web notice: " + request.data.decode())
        push.push_note(device, "Web Notice", request.data.decode())
        return """Success\n"""
    except Exception:
        traceback.print_exc()
        return """Failure\n"""


# noinspection PyBroadException
@app.route("/oauth/", methods=["GET"])
def oauth_respond():
    try:
        data = base64.b64encode(json.dumps(request.args).encode()).decode()
        return oauth_template.replace("<%content%>", data)
    except Exception:
        traceback.print_exc()
        return """Something went wrong. Please contact dabo@dabo.guru about this incident.\n"""


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5445)
