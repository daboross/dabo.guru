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
import os
import traceback
import sys

from flask import Flask, request, render_template

from pushbullet import PushBullet


def setup_logging():
    """
    Initializes the root logger
    :rtype: logging.Logger
    """
    # create logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # create file handler
    file_handler = logging.FileHandler("debug.log")
    file_handler.setLevel(logging.DEBUG)

    # create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)

    # set formatting
    file_handler.setFormatter(logging.Formatter("{asctime}[{levelname}] {message}", "[%Y-%m-%d][%H:%M:%S]", style="{"))
    console_handler.setFormatter(logging.Formatter("[{asctime}] {message}", "%H:%M:%S", style="{"))

    # add the Handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


def get_config():
    if os.path.isfile("config.json"):
        with open("config.json") as config_file:
            return json.load(config_file)
    else:
        print("Config not found! Please copy config.default.json to config.json")
        sys.exit()


setup_logging()
config = get_config()

# get api_key and device
api_key = config["pushbullet"]["api-key"]
device = config["pushbullet"]["device"]

# create app
push = PushBullet(api_key)
app = Flask(__name__, template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'))


@app.route("/notify", methods=["POST"])
def notify_respond():
    print("Web notice: " + request.data.decode())
    push.push_note(device, "Web Notice", request.data.decode())
    return """Success\n"""


@app.route("/oauth/", methods=["GET"])
def oauth_respond():
    if "oauth_token" in request.args and "oauth_verifier" in request.args:
        data = base64.b64encode(json.dumps(request.args).encode()).decode()
        return render_template("oauth-response.html", data=data)
    else:
        data = json.dumps(request.args, indent=4)
        rows = data.count("\n") + 1
        return render_template("oauth-error.html", data=data, rows=rows)


@app.errorhandler(Exception)
def internal_error(err):
    logging.exception("Exception!")
    try:
        # since we have pushbullet, we can do exception notices :D
        push.push_note(device, "Python Exception", traceback.format_exc())
    except Exception:
        logging.exception("Exception sending exception note!")
    return render_template("500.html"), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5445)
