import os

from noxsegutils.extractor import load_config, save_config


SAVE_YAML_PATH = os.path.join(
    os.path.dirname(
        os.path.abspath(__file__)),
    'save.yaml')


def save_timestamps(mediab: str, key: object, val: object, config: str = SAVE_YAML_PATH) -> None:
    save = load_config(config, {})
    if not mediab in save:
        save[mediab] = {}
    save[mediab][key] = val
    save_config(config, save)
