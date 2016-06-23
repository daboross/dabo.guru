import logging

import uwsgi
from flask import request
from flask.templating import render_template
from flask.wrappers import Response

from content import app, config


@app.route("/webhook", methods=["POST"])
def webhook():
    if not "token" in request.args:
        return render_template("403.html"), 403
    api_key = request.args["token"]

    if api_key in config["github"]:
        logging.debug("Submitting repo update for {}".format(config["github"][api_key]))
        uwsgi.mule_msg(api_key)
        return Response("Update successful", 200, mimetype="text/plain")

    return render_template("403.html"), 403
