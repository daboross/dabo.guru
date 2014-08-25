import json
import logging.config
import os
import sys

from flask import Flask

from content.util import htmlmin_filter
from pushbullet import PushBullet

__all__ = ["app", "config"]

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
logging.config.dictConfig({
    "version": 1,
    "formatters": {
        "brief": {
            "format": "[%(asctime)s][%(levelname)s] %(message)s",
            "datefmt": "%H:%M:%S"
        },
        "full": {
            "format": "[%(asctime)s][%(levelname)s] %(message)s",
            "datefmt": "%Y-%m-%d][%H:%M:%S"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "brief",
            "level": "WARNING",
            "stream": "ext://sys.stderr"
        },
        "file": {
            "class": "logging.FileHandler",
            "formatter": "full",
            "level": "DEBUG",
            "filename": "debug.log"
        }
    },
    "root": {
        "level": "DEBUG",
        "handlers": ["console", "file"]
    }
})


def get_config():
    config_path = os.path.abspath("config.json")
    if os.path.isfile(config_path):
        with open(config_path) as config_file:
            return json.load(config_file)
    else:
        logging.warning("Config not found! Please copy config.default.json to config.json")
        sys.exit()


config = get_config()

app = Flask(__name__)

htmlmin_filter.register(app)

# create app
push = PushBullet(config["pushbullet"]["api-key"])

from content import web_api_pages, markdown_serv, github_pull, error_handlers, minecraft_api, game
