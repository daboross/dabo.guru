import codecs
import os

from flask import render_template

from azdweb import app
from azdweb.util import gh_markdown

root_path = os.path.abspath("markdown")

# {filename: (mtime, contents)}
cache = {}


def load(filename):
    with codecs.open(filename, encoding="utf-8") as file:
        return gh_markdown.markdown(file.read())


def load_cached(filename):
    mtime = os.path.getmtime(filename)
    if filename in cache:
        old_mtime, contents = cache[filename]
        if mtime != old_mtime:
            contents = load(filename)
            cache[filename] = (mtime, contents)
    else:
        contents = load(filename)
        cache[filename] = (mtime, contents)
    return contents


@app.route("/md/", defaults={"page": "index"})
@app.route("/md/<path:page>/")
def serve_markdown(page):
    if "." in page:
        return render_template("markdown-404.html", page=page)
    if not page:
        page = "index"
    if page.endswith("/"):
        page += "index"

    filename = os.path.join(root_path, "{}.md".format(page))
    if not os.path.exists(filename):
        return render_template("markdown-404.html", page=page)
    sidebar = os.path.join(os.path.dirname(filename), "sidebar.md")
    if os.path.exists(sidebar):
        sidebar_content = load_cached(sidebar)
    else:
        sidebar_content = ""
    return render_template("markdown.html", title=page, content=load_cached(filename), sidebar=sidebar_content)


@app.route("/sw/", defaults={"page": "index"})
@app.route("/sw/<path:page>/")
def skywars_alias(page):
    if not page:
        page = "index"
    return serve_markdown("skywars/{}".format(page))
