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
    while True:
        api_key = uwsgi.mule_get_msg()
        repo_config = config["github"][api_key]
        documentation.update_repo(repo_config, True)


if __name__ == "__main__":
    main()
