import json
from time import sleep
from uuid import UUID

import click
import requests
from confluent_kafka import Producer

from signalation.conf.logger import get_logger
from signalation.conf.settings import Config, SignalConfig, get_config
from signalation.entities.signal import AttachmentFile, SignalMessage

logger = get_logger(__file__)
KAFKA_MESSAGE_TOPIC = "signal"
KAFKA_ATTACHMENT_TOPIC = "signal_attachments"


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
        run_message_loop(config=config, signal_producer=signal_producer)


def run_message_loop(config: Config, signal_producer: Producer) -> None:
    """Retrieve signal messages and produce them to kafka."""
    logger.info("Start receiving messages...")
    messages = receive_messages(signal_config=config.signal)
    num_message_kafka = sum([1 for message in messages if message.relevant_for_kafka])
    logger.info(f"...received {len(messages)} messages from which {num_message_kafka} are now sent to Kafka...")
    produce_messages(messages=messages, signal_producer=signal_producer)

    has_attachment = sum([message.has_attachment for message in messages]) > 0
    if has_attachment:
        logger.info("Start receiving attachments...")
        attachments = receive_attachments(signal_config=config.signal, messages=messages)
        produce_attachments(attachments=attachments, signal_producer=signal_producer)

    logger.info(f"Done. Sleeping for {config.signal.receive_in_s} s.")
    sleep(config.signal.receive_in_s)


def receive_attachments(signal_config: SignalConfig, messages: list[SignalMessage]) -> list[AttachmentFile]:
    """Query `signal-cli-rest-api` for downloaded attachments, serve them and return list of Attachments."""
    url = f"{signal_config.base_url}/v1/attachments"
    attachments = []
    for message in messages:
        if message.has_attachment:
            for attachment in message.attachments:
                query_url = f"{url}/{attachment.id}"
                try:
                    result = requests.get(url=query_url, timeout=signal_config.timeout_in_s)
                    attachment_file = AttachmentFile(
                        attachment_bytes_str=result.content,  # will be encoded to str through pydantic validator
                        chat_name=message.chat_name,
                        sender=message.msg_sender,
                        timestamp_epoch=message.envelope.timestamp,
                        attachment=attachment,
                    )
                    attachments.append(attachment_file)
                except requests.exceptions.Timeout:
                    logger.warning("Timeout occured.")
                except requests.exceptions.RequestException:
                    logger.error(
                        f"Make sure that `bbernhard/signal-cli-rest-api` is running under {signal_config.base_url}"
                    )
                    exit(1)
    return attachments


def receive_messages(signal_config: SignalConfig) -> list[SignalMessage]:
    """Query `signal-cli-rest-api` and parse results into list of `SignalMessage`s."""
    url = f"{signal_config.base_url}/v1/receive/{signal_config.registered_number}"
    try:
        result = requests.get(url=url, timeout=signal_config.timeout_in_s)
        result_json = result.json()
        if "error" in result_json:
            received_error_msg = result_json["error"]
            not_registered_error = f"User {signal_config.registered_number} is not registered.\n"
            if received_error_msg == not_registered_error:
                link = f"http://{signal_config.ip_adress}:{signal_config.port}/v1/qrcodelink?device_name=signal-api"
                msg = f"""
                    {signal_config.registered_number} is not registered.

                    Open the following link in your browser

                    {link}

                    then open Signal on your phone, go to `Settings > Linked Devices`
                    and scan the QR code using the + button.

                    You should see `signal-api` as a linked device in your list.
                """
                logger.info(msg)
                input("Press Enter once you are done...")

                result_json = []
            else:

                logger.error(f"Received an error when querying {url}:\n{received_error_msg}")
                result_json = []
    except requests.exceptions.Timeout:
        logger.warning("Timeout occured.")
        result_json = []
    except requests.exceptions.RequestException:
        logger.error(f"Make that `bbernhard/signal-cli-rest-api` is running under {signal_config.base_url}")
        exit(1)

    signal_messages = []
    for message_dict in result_json:
        try:
            signal_message = SignalMessage.parse_obj(message_dict)
            signal_messages.append(signal_message)
        except:
            logger.warning(f"The following message could not be parsed: {message_dict}")
    return signal_messages


def produce_messages(messages: list[SignalMessage], signal_producer: Producer) -> None:
    """Send retrived messages (from signal server) to kafka."""
    for message in messages:
        if message.relevant_for_kafka:
            chat_name = message.chat_name
            value = json.dumps(message.dict(), cls=UUIDEncoder)
            signal_producer.produce(topic=KAFKA_MESSAGE_TOPIC, key=chat_name, value=value)
    # wait for all messages in the Producer queue to be delivered
    signal_producer.flush()


def produce_attachments(attachments: list[AttachmentFile], signal_producer: Producer) -> None:
    for attachment in attachments:
        chat_name = attachment.chat_name
        value = json.dumps(attachment.dict(), cls=UUIDEncoder)

        signal_producer.produce(topic=KAFKA_ATTACHMENT_TOPIC, key=chat_name, value=value)
    # wait for all messages in the Producer queue to be delivered
    signal_producer.flush()


class UUIDEncoder(json.JSONEncoder):
    """Standard json encoder cannot encode UUIDs, this is a simple workaround, see
    https://stackoverflow.com/a/48159596/12999800
    """

    def default(self, obj):
        if isinstance(obj, UUID):
            # if the obj is uuid, we simply return the value of uuid
            return obj.hex
        return json.JSONEncoder.default(self, obj)


if __name__ == "__main__":
    run()
