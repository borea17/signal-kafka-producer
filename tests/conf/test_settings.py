from pathlib import Path

from signalation.conf.settings import Config, get_config

TEST_ENV_PATH = Path(__file__).parents[1] / "data" / "test.env"


def test_get_config_works_from_env_file():
    test_config = get_config(env_file_path=TEST_ENV_PATH)
    assert type(test_config) == Config
