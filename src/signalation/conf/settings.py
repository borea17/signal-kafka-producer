from pathlib import Path

from pydantic import BaseModel, BaseSettings, validator


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


class Config(BaseSettings):
    signal: SignalConfig
    kafka: KafkaConfig
    attachment_folder_path: Path

    class Config:
        env_nested_delimiter = "__"

    @validator("attachment_folder_path", always=True)
    def create_folder_if_necessary(cls, attachment_folder_path: Path) -> Path:
        attachment_folder_path.mkdir(parents=True, exist_ok=True)
        return attachment_folder_path


def get_config(env_file_path: Path | str = ".env") -> Config:
    return Config(_env_file=Path(env_file_path))
