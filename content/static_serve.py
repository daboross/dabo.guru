from flask.templating import render_template

files = {
    "/": "index.html",
    "/frc.html": "frc.html",
    "/irc.html": "irc.html",
}


def rendering_function(template):
    def render():
        return render_template(template)

    return render


def register(app):
    for url, template in files.items():
        app.add_url_rule(url, "static-serve-{}".format(template), rendering_function(template))
