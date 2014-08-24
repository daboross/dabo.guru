# Github-flavored markdown parsing
# Thanks to http://blog.freedomsponsors.org/markdown_formatting/
import misaka

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
        except:
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
