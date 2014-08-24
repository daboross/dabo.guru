from flask.templating import render_template

from content import app


@app.route("/2548/")
def get_2548():
    return render_template("2548.html")
