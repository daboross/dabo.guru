import logging
import subprocess
from concurrent.futures.thread import ThreadPoolExecutor
from pathlib import Path

import os
import shutil
from flask import request
from flask.templating import render_template
from flask.wrappers import Response

from content import app, config, push

repo_path = Path("github").resolve()
markdown_root = Path("markdown").resolve()
threadpool = ThreadPoolExecutor(2)


def update_repo(repo_config, rebuild_static: True):
    name = repo_config["name"]
    url = repo_config["url"]
    logging.info("Updating repository {} from {}".format(name, url))
    dirname = repo_path.joinpath(name)
    if not dirname.exists():
        if not repo_path.exists():
            repo_path.mkdir(mode=0o755, parents=True)
        subprocess.call(["git", "clone", url, name], cwd=str(repo_path))
    else:
        subprocess.call(["git", "pull"], cwd=str(dirname))

    if not markdown_root.exists():
        markdown_root.mkdir(mode=0o755, parents=True)

    markdown_source = dirname.joinpath(repo_config["markdown_dir"])
    markdown_dest = markdown_root.joinpath(name)

    logging.debug("Copying: {} -> {}".format(markdown_source, markdown_dest))
    try:
        try:
            shutil.rmtree(str(markdown_dest))
        except FileNotFoundError:
            pass  # no need to delete a file that doesn't exist
        shutil.copytree(str(markdown_source), str(markdown_dest))
    except Exception:
        logging.exception("Exception updating repository")
    else:
        if rebuild_static:
            build_file = str(Path("build.py").resolve())
            try:
                subprocess.check_output(["python3", build_file, "--repo", name])
            except subprocess.CalledProcessError as err:
                logging.warning("Error updating static repository documentation files: Output: {}", err.output)
                try:
                    push.push_note("Couldn't update documentation", err.output)
                except Exception:
                    logging.exception("Exception sending exception note.")


@app.route("/webhook", methods=["POST"])
def webhook():
    if not "token" in request.args:
        return render_template("403.html"), 403
    api_key = request.args["token"]

    if api_key in config["github"]:
        logging.debug("Submitting repo update for {}".format(config["github"][api_key]))
        threadpool.submit(update_repo, config["github"][api_key])
        return Response("Update successful", 200, mimetype="text/plain")

    return render_template("403.html"), 403


def update_all(rebuild_static):
    for repo in config["github"].values():
        update_repo(repo, rebuild_static=rebuild_static)


def get_possible_pages_for_frozen_flask(repo):
    return get_frozen_flask_markdown_urls(markdown_root.joinpath(repo), project_prefix=repo)


def get_all_possible_pages_for_frozen_flask():
    return get_frozen_flask_markdown_urls(markdown_root)


def get_frozen_flask_markdown_urls(dir_path, project_prefix=None):
    """
    :type path: pathlib.Path | str
    :rtype: iterator((str, map))
    """
    for (directory_path, _, filenames) in os.walk(str(dir_path)):
        for filename in filenames:
            path = Path(directory_path).joinpath(filename)
            if path.suffix == ".md":
                url_path = path.relative_to(dir_path).with_suffix("")
                if project_prefix:
                    project = project_prefix
                    page = url_path
                else:
                    project = url_path.parts[0]
                    page = url_path.relative_to(project)

                yield "serve_markdown", {
                    "project": project,
                    "page": "{}/".format(page)
                }

                if url_path.parts[-1] == "index":
                    index_page = page.parent
                    yield "serve_markdown", {
                        "project": project,
                        "page": "{}/".format(index_page)
                    }
