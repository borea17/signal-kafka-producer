from signalation.conf.settings import Config


def test_get_config_works_from_env_file(test_config: Config):
    assert type(test_config) == Config
