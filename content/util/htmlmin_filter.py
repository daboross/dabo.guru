from markupsafe import Markup

import htmlmin


def minify_filter(s):
    return Markup(htmlmin.minify(str(s), remove_comments=True, remove_empty_space=True))


def register(app):
    app.add_template_filter(minify_filter, name="minify")
