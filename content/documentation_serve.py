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

discus_format = """<div id="disqus_thread"></div>
<script>
    var disqus_config = function () {
        this.page.url = "https://dabo.guru/{url_path}";
        this.page.identifier = "{url_path}";
    };
    (function() {  // DON'T EDIT BELOW THIS LINE
        var d = document, s = d.createElement('script');

        s.src = '//skywars.disqus.com/embed.js';

        s.setAttribute('data-timestamp', +new Date());
        (d.head || d.body).appendChild(s);
    })();
</script>
<noscript>Please enable JavaScript to view the <a href="https://disqus.com/?ref_noscript" rel="nofollow">comments powered by Disqus.</a></noscript>
"""


def parse_discus(contents, url_path):
    if "[discus-thread]" in contents:
        return contents.replace("[discus-thread]", discus_format.replace("{url_path}", url_path))
    else:
        return contents


def load(filename, url_path):
    with codecs.open(filename, encoding="utf-8") as file:
        raw_contents = file.read()

    contents = gh_markdown.markdown(raw_contents)
    match = title_regex.match(raw_contents)
    if match:
        title = match.group(1) or match.group(2)
    else:
        logging.debug("Didn't match title for {}".format(raw_contents))
        title = None
    return title, parse_discus(contents, url_path)


def load_cached(filename, url_path):
    mtime = os.path.getmtime(filename)
    if filename in cache:
        old_mtime, title, contents = cache[filename]
        if mtime != old_mtime:
            title, contents = load(filename, url_path)
            cache[filename] = (mtime, title, contents)
    else:
        title, contents = load(filename, url_path)
        cache[filename] = (mtime, title, contents)

    return title, contents


@app.route("/projects/<project>/", defaults={"page": ""})
@app.route("/projects/<project>/<path:page>")
def serve_markdown(project, page):
    print("{}, {}".format(project, page))
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
        _, sidebar_content = load_cached(sidebar, "projects/{}/sidebar".format(project))
    else:
        sidebar_content = ""
    title, content = load_cached(filename, "projects/{}/{}".format(project, page))
    if title is None:
        title = "{} - {}".format(project, page)
    return render_template("markdown.html", title=title, content=content, sidebar=sidebar_content)
