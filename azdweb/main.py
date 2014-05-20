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
import logging
import traceback
import logging.config

from flask import request, render_template

from pushbullet import PushBullet
from azdweb import app, config

api_key = config["pushbullet"]["api-key"]
device = config["pushbullet"]["device"]

# create app
push = PushBullet(api_key)


@app.route("/notify", methods=["POST"])
def notify_respond():
    logging.info("Web notice: " + request.data.decode())
    push.push_note(device, "Web Notice", request.data.decode())
    return """Success\n"""


@app.route("/oauth", methods=["GET"])
def oauth_respond():
    if "oauth_token" in request.args and "oauth_verifier" in request.args:
        data = base64.b64encode(json.dumps(request.args).encode()).decode()
        return render_template("oauth-response.html", data=data)
    else:
        data = json.dumps(request.args, indent=4)
        rows = data.count("\n") + 1
        return render_template("oauth-error.html", data=data, rows=rows)

