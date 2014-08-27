import base64
import json
import logging
import logging.config

from flask import request, render_template

from content import app, push

valid_response_title = "OAuth response"
valid_response_desc = "Please copy the following data:"
invalid_response_title = "Invalid OAuth response"
invalid_response_desc = "The URL provided is invalid. Parameters oauth_token and/or oauth_verifier are missing"


@app.route("/notify", methods=["POST"])
def notify_respond():
    logging.info("Web notice: " + request.data.decode())
    push.push_note("dabo.guru note", request.data.decode())
    return """Success\n"""


@app.route("/oauth", methods=["GET"])
def oauth_respond():
    if "oauth_token" in request.args and "oauth_verifier" in request.args:
        data = base64.b64encode(json.dumps(request.args).encode()).decode()
        return render_template("display-data.html", title=valid_response_title, desc=valid_response_desc,
                               data=data, rows=2)
    else:
        data = json.dumps(request.args, indent=4)
        rows = data.count("\n") + 1
        return render_template("display-data.html", title=invalid_response_title, desc=invalid_response_desc,
                               data=data, rows=rows)

