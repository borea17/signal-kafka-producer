import json
from time import sleep
from uuid import UUID

import click
import requests
from confluent_kafka import Producer

from signalation.conf.logger import get_logger
from signalation.conf.settings import SignalConfig, get_config
from signalation.entities.signal import SignalMessage

logger = get_logger(__file__)
KAFKA_TOPIC = "signal"


@click.command()
@click.option(
    "-e",
    "--env_file_path",
    default=".env",
    help="Path to env file used by configuration.",
    type=click.Path(),
)
def run(env_file_path: str) -> None:
    config = get_config(env_file_path=env_file_path)
    signal_producer_config = {"bootstrap.servers": config.kafka.server.bootstrap_servers}
    signal_producer = Producer(signal_producer_config)
    while True:
        logger.info("Start receiving messages...")
        messages = receive_messages(signal_config=config.signal)
        num_message_kafka = sum([1 for message in messages if message.relevant_for_kafka])
        logger.info(
            f"...received {len(messages)} messages from which {num_message_kafka} are now sent to Kafka..."
        )
        produce_messages(messages=messages, signal_producer=signal_producer)
        logger.info(f"Done. Sleeping for {config.signal.receive_in_s} s.")
        sleep(config.signal.receive_in_s)


def produce_messages(messages: list[SignalMessage], signal_producer: Producer) -> None:
    """Send retrived messages (from signal server) to kafka."""
    for message in messages:
        if message.relevant_for_kafka:
            chat_name = message.chat_name
            value = json.dumps(message.dict(), cls=UUIDEncoder)
            signal_producer.produce(topic=KAFKA_TOPIC, key=chat_name, value=value)
    # wait for all messages in the Producer queue to be delivered
    signal_producer.flush()


def receive_messages(signal_config: SignalConfig) -> list[SignalMessage]:
    """Query `signal-cli-rest-api` and parse results into list of `SignalMessage`s."""
    url = f"{signal_config.base_url}/v1/receive/{signal_config.registered_number}"
    try:
        result = requests.get(url=url, timeout=signal_config.timeout_in_s)
        result_json = result.json()
        if "error" in result_json:
            received_error_msg = result_json["error"]
            logger.error(f"Received an error when querying {url}:\n{received_error_msg}")
            exit(1)
    except requests.exceptions.Timeout:
        logger.warning("Timeout occured.")
        result_json = []
    except requests.exceptions.RequestException:
        logger.error(
            f"Make that `bbernhard/signal-cli-rest-api` is running under {signal_config.signal.base_url}"
        )
        exit(1)

    signal_messages = []
    for message_dict in result_json:
        try:
            signal_message = SignalMessage.parse_obj(message_dict)
            signal_messages.append(signal_message)
        except:
            logger.warning(f"The following message could not be parsed: {message_dict}")
    return signal_messages


class UUIDEncoder(json.JSONEncoder):
    """Standard json encoder cannot encode UUIDs, this simple workaround, see
    https://stackoverflow.com/a/48159596/12999800
    """

    def default(self, obj):
        if isinstance(obj, UUID):
            # if the obj is uuid, we simply return the value of uuid
            return obj.hex
        return json.JSONEncoder.default(self, obj)


if __name__ == "__main__":
    run()
