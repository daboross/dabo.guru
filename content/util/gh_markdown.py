# Github-flavored markdown parsing
# Thanks to http://blog.freedomsponsors.org/markdown_formatting/
import itertools

import misaka
from markupsafe import Markup
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments.util import ClassNotFound


class HighlighterRenderer(misaka.HtmlRenderer):
    def blockcode(self, text, lang):
        if not lang:
            get_lexer_by_name("text")

        try:
            lexer = get_lexer_by_name(lang, stripall=True)
        except ClassNotFound:
            lexer = get_lexer_by_name("text")

        formatter = HtmlFormatter()

        return highlight(text, lexer, formatter)

    def table(self, content):
        return '<table class="table">\n' + content + '\n</table>'


# And use the renderer
renderer = HighlighterRenderer(flags=misaka.HTML_ESCAPE)
md = misaka.Markdown(renderer, extensions=(
    'tables', 'fenced-code', 'autolink', 'underline', 'no-intra-emphasis',
    'highlight', 'disable-indented-code', 'space-headers'
))


def markdown(text):
    return md(text)


def markdown_filter(s):
    text_lines = str(s).split('\n')
    if not text_lines:
        return ""  # there aren't any lines, so return nothing

    # this gets the first non-empty string, so we can get indentation from it
    initial_line = next(s for s in text_lines if s)

    # count leading spaces on first line, so we can strip the indentation spaces from all other lines
    leading_spaces = sum(1 for _ in itertools.takewhile(str.isspace, initial_line))
    # strip indentation spaces from lines so they work correctly inlined in html.
    # Note that we are removing an exact number of spaces so that we only strip spaces used for initial indentation in
    # html, not spaces used for marking code sections for instance.
    text_lines = (line[leading_spaces:] for line in text_lines)

    # reconstruct text
    text = '\n'.join(text_lines)

    return Markup(markdown(text))


def register(app):
    app.add_template_filter(markdown_filter, name="markdown")
