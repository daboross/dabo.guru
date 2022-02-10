import jinja2
import os
from flask import Flask
from redis import StrictRedis
from webassets.env import Environment

from content import static_serve
from content.util import htmlmin_filter, gh_markdown, webassets_integration
from resources_lib import configuration_resources

__all__ = ["app", "config"]

configuration_resources.set_working_directory()
configuration_resources.configure_logger("debug.log")

config = configuration_resources.get_config()

app = Flask(__name__, static_url_path='')

app.jinja_loader = jinja2.FileSystemLoader([
    os.path.abspath(os.path.join(app.root_path, "templates")),
    os.path.abspath(os.path.abspath("static-templates")),
])

push = configuration_resources.get_pushbullet()
redis = StrictRedis()

assets = Environment(os.path.abspath(os.path.join("static", "assets")), "assets/")
assets.append_path(app.static_folder, "/")
assets.auto_build = False
assets.url_expire = True
assets.cache = False
assets.manifest = "file:{}".format(os.path.abspath(os.path.join("static", ".webassets-manifest")))

# Create assets
assets.register('bootstrap-css', 'css/bootstrap.css',
                filters='cssmin', output='bootstrap.css')

assets.register('sidebar-css', 'css/shared-sidebar.css', 'css/bootstrap.css',
                filters='cssmin', output='shared.css')

assets.register('frc-css', 'css/bootstrap.css', 'css/frc.css',
                filters='cssmin', output='frc.css')

assets.register('markdown-css', 'css/bootstrap.css', 'css/markdown-sidebar.css',
                filters='cssmin', output='documentation.css')

assets.register('shared-js', 'js/jquery.js',
                filters='rjsmin', output='shared.js')

# Individual page javascript

assets.register('contact-js', 'js/send-form.js',
                filters='rjsmin', output='contact.js')

assets.register('2548-js', 'js/2548.js',
                filters='rjsmin', output='2548.js')

assets.register('frc-js', 'js/bootstrap.js', 'js/frc.js', 'js/send-form.js',
                filters='rjsmin', output='frc.js')

# Register filters
htmlmin_filter.register(app)
gh_markdown.register(app)
webassets_integration.Integration(assets).register(app)
# Register webpages
static_serve.register(app)
from content import web_api_pages, documentation_serve, documentation_update, error_handlers
# minecraft_api, mirror, statistics_api
