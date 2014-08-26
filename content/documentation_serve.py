import codecs
import logging
import os
import re

from flask import render_template

from content import app
from content.util import gh_markdown

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

@app.route("/projects/<project>/", defaults={"page": ""})
@app.route("/projects/<project>/<path:page>")
def serve_markdown(project, page):
    project_basedir = os.path.join(root_path, project)
    if not os.path.exists(project_basedir):
        return render_template("markdown-404.html", project=project), 404

    page = os.path.normpath(page)
    if page.startswith("..") or page.startswith("/"):
        return render_template("markdown-404.html", project=project, page=page), 404

    # normpath again to catch the case where page is '.'
    filename = os.path.normpath(os.path.join(project_basedir, page))

    if os.path.isdir(filename):
        filename = os.path.join(filename, "index")

    filename += ".md"
    if not os.path.exists(filename):
        return render_template("markdown-404.html", project=project, page=page), 404

    sidebar = os.path.join(project_basedir, "sidebar.md")
    if os.path.exists(sidebar):
        _, sidebar_content = load_cached(sidebar)
    else:
        sidebar_content = ""
    title, content = load_cached(filename)
    if title is None:
        title = "{} - {}".format(project, page)
    return render_template("markdown.html", title=title, content=content, sidebar=sidebar_content)
