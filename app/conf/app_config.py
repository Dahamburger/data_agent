from dataclasses import dataclass
from pathlib import Path

from omegaconf import OmegaConf

@dataclass
class FileConfig:
    enable: bool
    level: str
    path: str
    rotation: str
    retention: str

@dataclass
class ConsoleConfig:
    enable: bool
    level: str

@dataclass
class LoggingConfig:
    file: FileConfig
    console: ConsoleConfig

@dataclass
class DBConfig:
    host: str
    port: int
    user: str
    password: str
    database: str

@dataclass
class QdrantConfig:
    host: str
    port: int
    embedding_size: int

@dataclass
class EmbeddingConfig:
    host: str
    port: int
    model: str

@dataclass
class ESConfig:
    host: str
    port: int
    index_name: str

@dataclass
class LLMConfig:
    model_name: str
    api_key: str
    base_url: str

@dataclass
class AppConfig:
    logging: LoggingConfig
    db_meta: DBConfig
    db_dw: DBConfig
    qdrant: QdrantConfig
    embedding: EmbeddingConfig
    es: ESConfig
    llm: LLMConfig


APP_CONFIG_PATH = Path(__file__).parents[2] / "conf" / "app_config.yml"
context = OmegaConf.load(APP_CONFIG_PATH)
schema = OmegaConf.structured(AppConfig)
app_config : AppConfig = OmegaConf.to_object(OmegaConf.merge(schema, context))

