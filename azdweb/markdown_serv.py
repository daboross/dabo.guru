import codecs
import logging
import os
import re

from flask import render_template

from azdweb import app
from azdweb.util import gh_markdown

root_path = os.path.abspath("markdown")

# {filename: (mtime, title, contents)}
cache = {}

title_regex = re.compile("^([^\n]+)\n[=-]+|!\\[([^\\]]+)\\]")


def load(filename):
    with codecs.open(filename, encoding="utf-8") as file:
        raw_contents = file.read()

    contents = gh_markdown.markdown(raw_contents)
    match = title_regex.match(raw_contents)
    if match:
        title = match.group(1) or match.group(2)
    else:
        logging.debug("Didn't match title for {}".format(raw_contents))
        title = None
    return title, contents


def load_cached(filename):
    mtime = os.path.getmtime(filename)
    if filename in cache:
        old_mtime, title, contents = cache[filename]
        if mtime != old_mtime:
            title, contents = load(filename)
            cache[filename] = (mtime, title, contents)
    else:
        title, contents = load(filename)
        cache[filename] = (mtime, title, contents)

    return title, contents


@app.route("/md/", defaults={"page": "index"})
@app.route("/md/<path:page>")
def serve_markdown(page):
    if "." in page:
        return render_template("markdown-404.html", page=page), 404
    if not page:
        page = "index"
    if page.endswith("/"):
        page += "index"

    filename = os.path.join(root_path, "{}.md".format(page))
    if not os.path.exists(filename):
        return render_template("markdown-404.html", page=page), 404
    sidebar = os.path.join(os.path.dirname(filename), "sidebar.md")
    if os.path.exists(sidebar):
        ignored_title, sidebar_content = load_cached(sidebar)
    else:
        sidebar_content = ""
    title, content = load_cached(filename)
    if title is None:
        title = page
    return render_template("markdown.html", title=title, content=content, sidebar=sidebar_content)


@app.route("/sw/", defaults={"page": "index"})
@app.route("/sw/<path:page>")
def skywars_alias(page):
    if not page:
        page = "index"
    return serve_markdown("skywars/{}".format(page))


@app.route("/rt/", defaults={"page": "index"})
@app.route("/rt/<path:page>")
def robot_tables_alias(page):
    if not page:
        page = "index"
    return serve_markdown("robot-tables/{}".format(page))
