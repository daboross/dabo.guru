import logging
import traceback

from flask import render_template, request

from azdweb import app
from azdweb.main import push, device


@app.errorhandler(Exception)
def internal_error(err):
    logging.exception("Exception!")
    try:
        # since we have pushbullet, we can do exception notices :D
        push.push_note(device, "Python Exception", traceback.format_exc())
    except Exception:
        logging.exception("Exception sending exception note.")
    try:
        return render_template("500.html"), 500
    except Exception:
        logging.exception("Exception rendering 500 page.")
        return render_template("simple-500.html"), 500

@app.errorhandler(404)
def page_not_found(err):
    return render_template("404.html", url=request.url), 404


@app.errorhandler(403)
def unauthorized(err):
    return render_template("403.html", url=request.url), 403


@app.route("/403/")
def unauthorized_manual():
    return render_template("403.html", url=request.url), 403
