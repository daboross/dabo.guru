# Github-flavored markdown parsing
# Thanks to http://blog.freedomsponsors.org/markdown_formatting/
import misaka
from markupsafe import Markup
import itertools

from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters.html import HtmlFormatter


class HighlighterRenderer(misaka.HtmlRenderer, misaka.SmartyPants):
    def block_code(self, text, lang):
        s = ''
        if not lang:
            lang = 'text'
        try:
            lexer = get_lexer_by_name(lang, stripall=True)
        except Exception:
            s += '<div class="highlight"><span class="err">Error: language "{}" is not supported</span></div>'.format(
                lang)
            lexer = get_lexer_by_name('text', stripall=True)
        formatter = HtmlFormatter()
        s += highlight(text, lexer, formatter)
        return s

    def table(self, header, body):
        return '<table class="table">\n' + header + '\n' + body + '\n</table>'

# And use the renderer
renderer = HighlighterRenderer(flags=misaka.HTML_ESCAPE | misaka.HTML_SAFELINK)
md = misaka.Markdown(
    renderer, extensions=
    misaka.EXT_FENCED_CODE | misaka.EXT_NO_INTRA_EMPHASIS | misaka.EXT_TABLES | misaka.EXT_AUTOLINK |
    misaka.EXT_SPACE_HEADERS | misaka.EXT_STRIKETHROUGH | misaka.EXT_SUPERSCRIPT
)


def markdown(text):
    return md.render(text)


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
