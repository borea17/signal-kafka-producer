from typing import Any

from signalation.entities.signal_message import SignalMessage


def test_original_signal_message_dicts_can_be_parsed(original_signal_message_dict: dict[str, Any]):
    # pydantic ensures validation
    SignalMessage.parse_obj(original_signal_message_dict)
