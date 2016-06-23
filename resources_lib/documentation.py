import logging
import subprocess
from pathlib import Path

import os
import shutil

from resources_lib import configuration_resources

repo_path = Path("github").resolve()
markdown_root = Path("markdown").resolve()


def update_repo(repo_config, rebuild_static=True):
    """
    :param repo_config: A configuration with a "name", "url" and "markdown_dir"
    :param rebuild_static: If true, run Frozen-Flask in a subprocess before returning
    """
    name = repo_config["name"]
    url = repo_config["url"]
    logging.info("Updating repository {} from {}".format(name, url))
    git_directory = repo_path.joinpath(name)
    if not git_directory.exists():
        if not repo_path.exists():
            repo_path.mkdir(mode=0o755, parents=True)
        subprocess.call(["git", "clone", url, name], cwd=str(repo_path))
    else:
        subprocess.call(["git", "pull"], cwd=str(git_directory))

    if not markdown_root.exists():
        markdown_root.mkdir(mode=0o755, parents=True)

    markdown_source = git_directory.joinpath(repo_config["markdown_dir"])
    markdown_destination = markdown_root.joinpath(name)

    logging.debug("Copying: {} -> {}".format(markdown_source, markdown_destination))
    try:
        try:
            shutil.rmtree(str(markdown_destination))
        except FileNotFoundError:
            pass  # no need to delete a file that doesn't exist
        shutil.copytree(str(markdown_source), str(markdown_destination))
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
                    push = configuration_resources.get_pushbullet()
                    push.push_note("Couldn't update documentation", err.output)
                except Exception:
                    logging.exception("Exception sending exception note.")


def update_all_repositories(config, rebuild_static):
    for repo_config in config["github"].values():
        update_repo(repo_config, rebuild_static=rebuild_static)


def get_possible_pages_for_frozen_flask(repo):
    return get_frozen_flask_markdown_urls(markdown_root.joinpath(repo), project_prefix=repo)


def get_all_possible_pages_for_frozen_flask():
    return get_frozen_flask_markdown_urls(markdown_root)


def get_frozen_flask_markdown_urls(dir_path, project_prefix=None):
    """
    :param project_prefix: If specified, the project name. If not specified each subdirectory of dir_path will be
        assumed to be a separate project named with the directory name
    :type dir_path: pathlib.Path | str
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
