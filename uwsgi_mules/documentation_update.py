import logging
from pathlib import Path

# Not an actual python module, but produced by uwsgi
# documentation: http://uwsgi-docs.readthedocs.io/en/latest/PythonModule.html
import uwsgi

from resources_lib import configuration_resources, documentation

repo_path = Path("github").resolve()
markdown_root = Path("markdown").resolve()

configuration_resources.set_working_directory()
configuration_resources.configure_logger("documentation_update-debug.log")
config = configuration_resources.get_config()
push = configuration_resources.get_pushbullet()


def main():
    root_repo_config = config["github"]
    python_executable = config["subprocess_python_interpreter"]
    while True:
        api_key = uwsgi.mule_get_msg().decode()
        repo_config = root_repo_config.get(api_key)
        if repo_config is None:
            logging.warning("Failed to find api_key {} in {}", api_key, config)
            continue
        documentation.update_repo(repo_config, static_rebuild_python_executable=python_executable)


if __name__ == "__main__":
    main()
