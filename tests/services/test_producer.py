import requests_mock

from signalation.conf.settings import SignalConfig
from signalation.entities.signal_message import SignalMessage
from signalation.services.producer import receive_messages


def test_receive_messages_works_with_mocked_request(signal_config: SignalConfig, result_json_list: list[dict]) -> None:
    url = f"{signal_config.base_url}/v1/receive/{signal_config.registered_number}"

    with requests_mock.Mocker() as mocked_request:
        mocked_request.get(url, json=result_json_list)
        signal_messages = receive_messages(signal_config)
    for signal_message in signal_messages:
        assert type(signal_message) == SignalMessage
