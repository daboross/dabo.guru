import os

from flask.templating import render_template

files = {
    "/": "index.html",
    "/frc.html": "frc.html",
    "/resources.html": "resources.html",
    "/contact.html": "contact.html",
    "/projects/": "projects.html",
    # error pages
    "/errors/403.html": "403.html",
    "/errors/404.html": "404.html",
    "/errors/500.html": "500.html",
}


def rendering_function(template):
    def render():
        return render_template(template)

    return render


def register(app):
    for url, template in files.items():
        app.add_url_rule(url, os.path.splitext(template)[0], rendering_function(template))
