import logging
import logging.config
from pathlib import Path

import yaml

path_to_config = Path(__file__).parent / "logging_config.yaml"
with open(path_to_config, "r") as f:
    config = yaml.safe_load(f.read())


def get_logger(name_of_logger: str) -> logging.Logger:
    logging.config.dictConfig(config)
    logger = logging.getLogger(name_of_logger)
    return logger
