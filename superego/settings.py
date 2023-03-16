import pathlib
import yaml

BASE_DIR = pathlib.Path(__file__).parent.parent
config_path = BASE_DIR / 'config.yaml'

def parse_config(path):
    with open(path) as f:
        config_ = yaml.safe_load(f)
    return config_

config = parse_config(config_path)