import os
import sys

from flask.ext.frozen import Freezer
import webassets

from content import app, assets


def build_assets():
    for bundle in assets:
        assert isinstance(bundle, webassets.Bundle)
        print("Building bundle {}".format(bundle.output))
        bundle.build(force=True, disable_cache=True)


# This is a copy of Freezer.no_argument_rules() modified to ignore certain paths
def no_argument_rules_urls_with_ignore():
    """URL generator for URL rules that take no arguments."""
    ignored = app.config.get('FREEZER_IGNORE_ENDPOINTS', [])
    for rule in app.url_map.iter_rules():
        if rule.endpoint not in ignored and not rule.arguments and 'GET' in rule.methods:
            yield rule.endpoint, {}


def build_pages():
    ignored = [bundle.output for bundle in assets]
    app.config['FREEZER_DESTINATION'] = os.path.abspath("static")
    app.config['FREEZER_BASE_URL'] = "http://dabo.guru/"
    app.config['FREEZER_DESTINATION_IGNORE'] = ignored
    app.config['FREEZER_IGNORE_ENDPOINTS'] = ['oauth_respond', 'mc_api_name', 'mc_api_uuid', 'serve_markdown']
    freezer = Freezer(app=app, with_static_files=False, with_no_argument_rules=False, log_url_for=True)
    freezer.register_generator(no_argument_rules_urls_with_ignore)

    print("Freezing")
    freezer.freeze()


def main():
    args = sys.argv[1:]
    if args:
        is_assets = False
        is_pages = False
        for arg in args:
            if arg == '--assets' or arg == '-a':
                is_assets = True
            elif arg == "--pages" or arg == "-p":
                is_pages = True
            else:
                print("Unknown argument '{}'".format(arg))
                print("Valid arguments: --assets -a --pages -p")
                return
    else:
        is_assets = True
        is_pages = True

    if is_assets:
        build_assets()
    if is_pages:
        build_pages()


main()
