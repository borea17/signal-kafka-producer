import pickle
from pathlib import Path
from typing import Any

import pytest

from signalation.conf.settings import Config, SignalConfig, get_config

TESTS_DIR = Path(__file__).parents[0]
TEST_ENV_PATH = TESTS_DIR / "data" / "test.env"
DATA_DIR = TESTS_DIR / "data"
SIGNAL_MESSAGE_DIR = DATA_DIR / "signal_message_dicts"


@pytest.fixture()
def test_config() -> Config:
    return get_config(env_file_path=TEST_ENV_PATH)


@pytest.fixture()
def signal_config(test_config) -> SignalConfig:
    return test_config.signal


@pytest.fixture()
def test_attachment_file_dict() -> dict[str, Any]:
    file_name = "test_attachment_img.png"
    with open(DATA_DIR / file_name, "rb") as f:
        attachment_bytes: bytes = f.read()
    return {
        "chat_name": "test",
        "sender": "test",
        "timestamp_epoch": 1000,
        "attachment_dir": DATA_DIR / "attachment",
        "attachment": {
            "contentType": "image/png",
            "filename": file_name,
            "id": "1085610255921309507.png",
            "size": 101369,
        },
        "attachment_bytes_str": attachment_bytes,
    }


@pytest.fixture(
    params=[message_dict_path for message_dict_path in SIGNAL_MESSAGE_DIR.glob("*.pkl")],
)
def original_signal_message_dict(request) -> dict[str, Any]:
    """Original dict from signal API (anonymized)."""
    with open(request.param, "rb") as f:
        loaded_dict = pickle.load(f)
    return loaded_dict


@pytest.fixture()
def result_json_list() -> list[dict]:
    message_dicts = []
    for message_dict_path in SIGNAL_MESSAGE_DIR.glob("*.pkl"):
        with open(message_dict_path, "rb") as f:
            signal_message_dict = pickle.load(f)
        message_dicts.append(signal_message_dict)
    return message_dicts
