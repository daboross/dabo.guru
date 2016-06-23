import json
import logging.config
import sys

import os

from pushbullet import PushBullet

logger_configured = False

config = None

pushbullet = None


def set_working_directory():
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def configure_logger(debug_file):
    global logger_configured
    if logger_configured:
        return
    else:
        logger_configured = True
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
                "filename": debug_file
            }
        },
        "root": {
            "level": "DEBUG",
            "handlers": ["console", "file"]
        }
    })


def get_config():
    global config
    if config is None:
        config_path = os.path.abspath("config.json")
        if os.path.isfile(config_path):
            with open(config_path) as config_file:
                config = json.load(config_file)
        else:
            logging.warning("Config not found! Please copy config.default.json to config.json")
            sys.exit()
    return config


def get_pushbullet():
    global pushbullet
    if pushbullet is None:
        config = get_config()

        pushbullet = PushBullet(config["pushbullet"]["api-key"])

    return pushbullet
