import sys

import os
import webassets
from flask_frozen import Freezer

from content import app, assets, config
from resources_lib import documentation


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


def markdown_url_generator():
    return documentation.get_all_possible_pages_for_frozen_flask()


def build_pages():
    ignored = [bundle.output for bundle in assets] + ["rust"]
    app.config['FREEZER_DESTINATION'] = os.path.abspath("static")
    app.config['FREEZER_BASE_URL'] = "https://dabo.guru/"
    app.config['FREEZER_DESTINATION_IGNORE'] = ignored
    app.config['FREEZER_IGNORE_ENDPOINTS'] = ['oauth_respond', 'mc_api_name', 'mc_api_uuid', 'serve_markdown',
                                              'uuid_api']
    freezer = Freezer(app=app, with_static_files=False, with_no_argument_rules=False, log_url_for=True)
    freezer.register_generator(no_argument_rules_urls_with_ignore)
    freezer.register_generator(markdown_url_generator)
    freezer.register_generator(lambda: ("/favicon.ico",))
    print("Updating documentation")
    documentation.update_all_repositories(config, False)
    print("Freezing")
    freezer.freeze()


def build_individual_repositories(repository_list):
    app.config['FREEZER_DESTINATION'] = os.path.abspath("static")
    app.config['FREEZER_BASE_URL'] = "https://dabo.guru/"
    app.config['FREEZER_REMOVE_EXTRA_FILES'] = False
    freezer = Freezer(app=app, with_static_files=False, with_no_argument_rules=False, log_url_for=True)
    for repository in repository_list:
        def url_generator():
            return documentation.get_possible_pages_for_frozen_flask(repository)

        freezer.register_generator(url_generator)
    freezer.freeze()


def main():
    args = sys.argv[1:]
    if args:
        is_assets = False
        is_pages = False
        repositories = []
        next_is_repo = False
        for arg in args:
            if next_is_repo:
                repositories.append(arg)
                next_is_repo = False
            elif arg == "--assets" or arg == "-a":
                is_assets = True
            elif arg == "--pages" or arg == "-p":
                is_pages = True
            elif arg == "--repo" or arg == "-r":
                next_is_repo = True
            else:
                print("Unknown argument '{}'".format(arg))
                print("Valid arguments: --assets -a --pages -p")
                return
    else:
        is_assets = True
        is_pages = True
        repositories = []

    if is_assets:
        build_assets()
    if is_pages:
        build_pages()
    elif repositories:
        # All repositories will have already been built if pages is set.
        build_individual_repositories(repositories)


main()
