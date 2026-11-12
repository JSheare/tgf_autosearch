"""A module containing functions for working with the application's config file."""
import pathlib
import platformdirs
import yaml
from typing import Any, Dict

import tgf_autosearch.config.parameters as params


def make_user_config() -> None:
    """Copies the application's config template to the user config directory."""
    template_file = f'{pathlib.Path(__file__).parent.parent}/config/{params.CONFIG_FILE}'
    with open(template_file, 'r') as f:
        lines = f.readlines()

    directory = platformdirs.user_config_path(params.APPLICATION_NAME, appauthor=False)
    if not directory.is_dir():
        directory.mkdir(parents=True)

    with open(f'{directory}/{params.CONFIG_FILE}', 'w') as f:
        f.writelines(lines)


def read_config() -> Dict[str, Any]:
    """Reads and parses the application's config file and returns it as a dictionary."""
    # Reading the user config file, or making one if it doesn't exist
    directory = platformdirs.user_config_path(params.APPLICATION_NAME, appauthor=False)
    user_file = f'{directory}/{params.CONFIG_FILE}'
    if not pathlib.Path(user_file).is_file():
        make_user_config()

    with open(user_file, 'r') as f:
        config = yaml.safe_load(f)

    return config
