from typing import TypedDict

from langchain_huggingface import HuggingFaceEndpointEmbeddings

from app.repositories.es.value_es_repository import ValueESRepository
from app.repositories.mysql.dw.dw_mysql_repository import DWMySQLRepository
from app.repositories.mysql.meta.meta_mysql_repository import MetaMySQLRepository
from app.repositories.qdrant.column_qdrant_repository import ColumnQdrantRepository
from app.repositories.qdrant.metric_qdrant_repository import MetricQdrantRepository


class DataAgentContext(TypedDict):
    column_qdrant_repository: ColumnQdrantRepository  # Qdrant列信息仓储，用于存储和检索数据库表的列/字段信息
    metric_qdrant_repository: MetricQdrantRepository  # Qdrant指标信息仓储，用于存储和检索业务指标信息
    embedding_client: HuggingFaceEndpointEmbeddings  # 向量化客户端，用于将文本转换为向量以便进行语义检索
    value_es_repository: ValueESRepository  # ES值信息仓储，用于存储和检索业务指标的值
    meta_mysql_repository: MetaMySQLRepository  # MySQL元数据仓储，用于存储和检索数据库的元数据
    dw_mysql_repository: DWMySQLRepository  # MySQL元数据仓储，用于存储和检索数据库的元数据
