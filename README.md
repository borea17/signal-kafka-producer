# signal-kafka-producer a.k.a. signalation

**[Motivation](https://github.com/borea17/signal-kafka-producer#motivation)** | **[Installation](https://github.com/borea17/signal-kafka-producer#installation)**

This python package allows to produce messages from your [signal](https://signal.org/) account to [kafka](https://kafka.apache.org/)
by querying the [dockerized signal messenger](https://github.com/bbernhard/signal-cli-rest-api).

## Motivation

### Kafka Consumers

### Maintain Messages in Message Queue

## Installation

For running the `signal-kafka-producer`, you'll need to have a access to a running instance of [kafka](https://kafka.apache.org/)
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

You should see your produced messages on the kafka ui [https://localhost:8081](https://localhost:8081)
(use port from `.env` file).
