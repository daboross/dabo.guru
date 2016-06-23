import logging
import logging.config

from flask import request

from content import app, push


@app.route("/notify/", methods=["POST"])
def notify_respond():
    if request.content_length > 512:
        return """Error: too large of a message""", 400
    logging.info("Web notice: " + request.data.decode())
    push.push_note("dabo.guru note", request.data.decode())
    return """Success\n"""
