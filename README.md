# signal-kafka-producer

This project allows to produce messages from your [signal](https://signal.org/) account to [kafka](https://kafka.apache.org/)
using the [dockerized signal messenger](https://github.com/bbernhard/signal-cli-rest-api) and a dockerized kafka platform.

## Motivation

## Installation

1. Clone Repository and Go to Folder

```bash
git clone git@github.com:borea17/signal-kafka-producer.git
cd signal-kafka-producer
```

2. Install Python Package

```bash
# create virtual environment
python -m venv venv
# activate virtual enviroment
source /venv/bin/activate
# install package
pip install -e .
```

3. Create Configuration File

In order to run the service, you need to create a `.env` file at the root level of the repository with the
following content

```bash
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

Note: You'll need to replace `SIGNAL__REGISTERED_NUMBER` with your phone number.

4. Run Dockerized Services

In order to run the [dockerized signal messenger](https://github.com/bbernhard/signal-cli-rest-api) and a dockerized kafka
you'll need to run

```bash
docker-compose -f dockerized_services/signal/docker-compose.yml --env-file .env up -d
docker-compose -f dockerized_services/kafka/docker-compose.yml --env-file .env up -d
```

5. Start Producer via CLI

```bash
signal-kafka-producer --env_file_path .env
```

Note: You'll need to register your phone number with for the
[dockerized signal messenger](https://github.com/bbernhard/signal-cli-rest-api). Simply follow the instructions
in the terminal.

You should see your produced messages on the kafka ui [https://localhost:8081](https://localhost:8081)
(use port from `.env` file).
