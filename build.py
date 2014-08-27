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

print("Freezing")

app.config['FREEZER_DESTINATION'] = os.path.abspath("static")
app.config['FREEZER_BASE_URL'] = "http://dabo.guru/"
app.config['FREEZER_DESTINATION_IGNORE'] = bundle_files
freezer = Freezer(app=app, with_static_files=False, with_no_argument_rules=True, log_url_for=True)

freezer.freeze()
