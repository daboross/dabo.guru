import os

from flask import request, render_template

from azdweb import app
from azdweb.util import gh_markdown

root_path = os.path.abspath("markdown")

# {filename: (mtime, contents)}
cache = {}


def load(filename):
    with open(filename) as file:
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


@app.route("/md/<page>")
def serve_markdown(page):
    filename = os.path.join(root_path, "{}.md".format(page))
    if not os.path.exists(filename):
        return render_template("markdown-404.html", page=page)
    return render_template("markdown.html", page=page, content=load_cached(filename))