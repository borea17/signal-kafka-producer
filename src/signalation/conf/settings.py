from pathlib import Path

from pydantic import BaseModel, BaseSettings


class PortConfig(BaseModel):
    port: int


class SignalConfig(PortConfig):
    registered_number: str
    ip_adress: str
    timeout_in_s: float
    receive_in_s: float

    @property
    def base_url(self) -> str:
        return f"http://{self.ip_adress}:{self.port}"


class KafkaServerConfig(PortConfig):
    @property
    def bootstrap_servers(self) -> str:
        return f"localhost:{self.port}"


class KafkaConfig(BaseModel):
    ui: PortConfig
    server: KafkaServerConfig
    zookeeper: PortConfig

    @property
    def brokers(self) -> dict:
        return {
            "localhost": {
                "url": "localhost",
                "description": "local development kafka broker",
                "port": self.server.port,
            },
        }


class Config(BaseSettings):
    signal: SignalConfig
    kafka: KafkaConfig

    class Config:
        env_nested_delimiter = "__"


def get_config(env_file_path: Path | str = ".env") -> Config:
    return Config(_env_file=Path(env_file_path))
