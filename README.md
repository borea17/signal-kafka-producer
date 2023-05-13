# signal-kafka-producer a.k.a. signalation

[![Python package](https://github.com/borea17/signal-kafka-producer/actions/workflows/python-package.yml/badge.svg?branch=main)](https://github.com/borea17/signal-kafka-producer/actions/workflows/python-package.yml) [![Python Publish](https://github.com/borea17/signal-kafka-producer/actions/workflows/python-package.yml/badge.svg?branch=main)](https://github.com/borea17/signal-kafka-producer/actions/workflows/python-publish.yml) [![PyPI version](https://badge.fury.io/py/signalation.svg)](https://badge.fury.io/py/signalation)

**[Motivation](https://github.com/borea17/signal-kafka-producer#motivation---why-should-i-use-it)** | **[Installation](https://github.com/borea17/signal-kafka-producer#installation---how-can-i-use-it)** | **[Implementation Details](https://github.com/borea17/signal-kafka-producer#implementation-details---how-does-it-work)**

Python package to produce messages from your [signal](https://signal.org/) account to [kafka](https://kafka.apache.org/)
by querying the [dockerized signal messenger API](https://github.com/bbernhard/signal-cli-rest-api).

## Motivation - Why should I use it?

After starting the `signal-kafka-producer` all your signal messages (sent and received) are produced onto a kafka topic.
As a result, there are two main advantages:

1. Messages do not get lost, see [Keep (Ephemeral) Messages in Message Queue](https://github.com/borea17/signal-kafka-producer#keep-ephemeral-messages-in-message-queue)
2. Use [Kafka Connectors](https://docs.confluent.io/kafka-connectors/self-managed/kafka_connectors.html) or consumers for your use case, see [Kafka Consumers/Connectors](https://github.com/borea17/signal-kafka-producer#kafka-consumersconnectors)

### Keep (Ephemeral) Messages in Message Queue

We've all been there: You are searching for some information and cannot find the corresponding message.
Maybe you've switched your phone, phone number or some of your contacts simply love [Signal's ephemeral/self-destructing messages](https://signal.org/blog/disappearing-by-default/) - in any case `signal-kafka-producer` comes to the rescue. Any message is stored
in a kafka topic and YOU are the maintainer of it.

Note: Messages will be deleted in Kafka as well, see [Retention Policy](https://www.conduktor.io/kafka/kafka-topic-configuration-log-retention/).
However, you can either set infinite time or use a Kafka DB Sink Connector to store your messages in a database.

### Kafka Consumers/Connectors

Having your signal message in a Kafka Topic comes with all kafka associated benefits:

- **Real-time processing**:
  Depending on your use-case, you can write consumers that can act on the messages in real-time, e.g.,
  - A service that sends answers from ChatGPT whenever a message starts with `ChatGPT please help:`
  - A service that forwards messages to `Note to Self` whenever a self-destructing message is received.
- **Flexibility**:
  Kafka Topics can be integrated using other tools such as
  [Kafka Connectors](https://docs.confluent.io/kafka-connectors/self-managed/kafka_connectors.html), e.g.,
  you could use a Kafka DB Sink Connector to store your messages in a database.

## Installation - How can I use it?

For running the `signal-kafka-producer`, you'll need to have access to a running instance of [kafka](https://kafka.apache.org/)
and [signal](https://github.com/bbernhard/signal-cli-rest-api). If you do not have that go to
[Complete Installation including Dockerized Services](https://github.com/borea17/signal-kafka-producer#complete-installation-including-dockerized-services),
otherwise you can directly use [Pip Installation](https://github.com/borea17/signal-kafka-producer#pip-installation).

### Pip Installation

```bash
pip install signalation
```

The producer can then be executed via

```bash
signal-kafka-producer --env_file_path .env
```

where the `.env` file should have the following content

```bash
ATTACHMENT_FOLDER_PATH=<folder path in which attachments shall be stored>
# Signal configuration
SIGNAL__REGISTERED_NUMBER=<your phone number>
SIGNAL__IP_ADRESS=<ip address of signal rest api>
SIGNAL__PORT=<port of signal rest api>
SIGNAL__TIMEOUT_IN_S=<signal request timeout in seconds>
SIGNAL__RECEIVE_IN_S=<signal request interval in seconds>
# Kafka configuration
KAFKA__SERVER__PORT=<kafka bootstrap server port>
```

### Complete Installation including Dockerized Services

1. Clone Repository, Install Python Package and Create Configuration

```bash
git clone git@github.com:borea17/signal-kafka-producer.git
cd signal-kafka-producer
pip install .
```

In order to run the dockerized services (signal messenger and kafka) as well as the producer service,
you need to create a `.env` file with the following content

```bash
ATTACHMENT_FOLDER_PATH=./attachments
# Signal configuration
SIGNAL__REGISTERED_NUMBER=+49000000
SIGNAL__IP_ADRESS=127.0.0.1
SIGNAL__PORT=8080
SIGNAL__TIMEOUT_IN_S=90
SIGNAL__RECEIVE_IN_S=1
# Kafka configuration
KAFKA__UI__PORT=8081
KAFKA__SERVER__PORT=9092
KAFKA__ZOOKEEPER__PORT=2181
```

Note: You'll need to replace `SIGNAL__REGISTERED_NUMBER` with your phone number. Of course, you are free to adjust
ports and timeouts / waiting times to your needs.

2. Run Dockerized Services

In order to run the [dockerized signal messenger](https://github.com/bbernhard/signal-cli-rest-api) and a dockerized kafka
(using your previously defined variables), you simply need to run

```bash
docker-compose -f tests/dockerized_services/signal/docker-compose.yml --env-file .env up -d
docker-compose -f tests/dockerized_services/kafka/docker-compose.yml --env-file .env up -d
```

Note: Adjust paths accordingly.

3. Start Producer via CLI

```bash
signal-kafka-producer --env_file_path .env
```

Note: You'll need to register your phone number with for the
[dockerized signal messenger](https://github.com/bbernhard/signal-cli-rest-api). Simply follow the instructions
in the terminal.

You should see your produced messages on the kafka ui [http://localhost:8081/](https://localhost:8081)
(use `KAFKA__UI__PORT` from `.env` file).

## Implementation Details - How does it work?

`signal-kafka-producer` calls [`src/signalation/services/producer.py`](https://github.com/borea17/signal-kafka-producer/blob/main/src/signalation/services/producer.py) which has the following logic:

1. It polls the Signal server and retrieves new Signal messages with their metadata
2. It produces the messages to a Kafka topic.
3. If a message has an attachment, it downloads it and stores the file locally.
   Additionally, corresponding metadata of the attachment is produced to a separate Kafka topic.

Here is a more detailed description given by ChatGPT:

> The `run` function is the main entry point of the code. It retrieves configuration settings from an environment file
> and initializes a Kafka producer object. Then, it repeatedly calls the `run_message_loop_iteration` function,
> which retrieves Signal messages and their attachments, produces them to the relevant Kafka topics, and sleeps for
> a specified duration before it starts the next iteration.
>
> The `receive_messages` function sends a `GET` request to the Signal server to retrieve new messages for a
> given registered number. It returns a list of Signal messages, each represented by a `SignalMessage` object.
> The `receive_attachments` function sends a GET request to the Signal server to retrieve attachments associated
> with a given list of messages. It returns a list of `AttachmentFile` objects, each representing a Signal attachment file.
>
> The `produce_messages` function takes a list of `SignalMessage` objects and a Kafka producer object,
> and produces them to the message topic.
>
> Finally, the `EnhancedEncoder` class is a custom JSON encoder that converts Python objects into JSON strings.
