import base64
import json
import logging
import logging.config

from flask import request, render_template

from content import app, push, device


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

