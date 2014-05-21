from concurrent.futures.thread import ThreadPoolExecutor
import logging
import os
import subprocess
import shutil

from flask import request
from flask.templating import render_template

from azdweb import app, config

repo_path = os.path.abspath("github")
markdown_root = os.path.abspath("markdown")
threadpool = ThreadPoolExecutor(2)


def update_repo(repo_config):
    name = repo_config["name"]
    url = repo_config["url"]
    logging.info("Updating repository {} from {}".format(name, url))
    dirname = os.path.join(repo_path, name)
    if not os.path.exists(dirname):
        if not os.path.exists(repo_path):
            os.makedirs(repo_path)
        subprocess.call(["git", "clone", url, name], cwd=repo_path)
    else:
        subprocess.call(["git", "pull"], cwd=dirname)

    if not os.path.exists(markdown_root):
        os.makedirs(markdown_root)

    markdown_source = os.path.join(dirname, repo_config["markdown_dir"])
    markdown_dest = os.path.join(markdown_root, name)
    logging.debug("Copying: {} -> {}".format(markdown_source, markdown_dest))

    try:
        try:
            shutil.rmtree(markdown_dest)
        except FileNotFoundError:
            pass  # no need to delete a file that doesn't exist
        logging.debug("Result: {}".format(shutil.copytree(markdown_source, markdown_dest)))
    except Exception:
        logging.exception("Ah, exception here.")


@app.route("/webhook", methods=["POST"])
def webhook():
    if not "token" in request.args:
        return render_template("invalid-api-key-403.html"), 403
    api_key = request.args["token"]

    if api_key in config["github"]:
        threadpool.submit(update_repo, config["github"][api_key])
        return render_template("generic-success.html")

    return render_template("invalid-api-key-403.html"), 403
