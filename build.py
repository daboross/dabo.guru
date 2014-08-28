import os

from flask.ext.frozen import Freezer
import webassets

from content import app, assets

bundle_files = []
for bundle in assets:
    assert isinstance(bundle, webassets.Bundle)
    print("Building bundle {}".format(bundle.output))
    bundle.build(force=True, disable_cache=True)
    bundle_files.append(bundle.output)


# This is a copy of Freezer.no_argument_rules() modified to ignore certain paths
def no_argument_rules_urls_with_ignore():
    """URL generator for URL rules that take no arguments."""
    ignored = app.config.get('FREEZER_IGNORE_ENDPOINTS', [])
    for rule in app.url_map.iter_rules():
        if rule.endpoint not in ignored and not rule.arguments and 'GET' in rule.methods:
            yield rule.endpoint, {}


app.config['FREEZER_DESTINATION'] = os.path.abspath("static")
app.config['FREEZER_BASE_URL'] = "http://dabo.guru/"
app.config['FREEZER_DESTINATION_IGNORE'] = bundle_files
app.config['FREEZER_IGNORE_ENDPOINTS'] = ['oauth_respond', 'mc_api_name', 'mc_api_uuid', 'serve_markdown']
freezer = Freezer(app=app, with_static_files=False, with_no_argument_rules=False, log_url_for=True)
freezer.register_generator(no_argument_rules_urls_with_ignore)

print("Freezing")
freezer.freeze()
