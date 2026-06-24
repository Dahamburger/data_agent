from typing import TypedDict

from langchain_huggingface import HuggingFaceEndpointEmbeddings

from app.repositories.qdrant.column_qdrant_repository import ColumnQdrantRepository
from app.repositories.qdrant.metrics_qdrant_repository import MetricsQdrantRepository


class DataAgentContext(TypedDict):
    column_qdrant_repository: ColumnQdrantRepository  # Qdrant列信息仓储，用于存储和检索数据库表的列/字段信息
    metric_qdrant_repository: MetricsQdrantRepository  # Qdrant指标信息仓储，用于存储和检索业务指标信息
    embedding_client: HuggingFaceEndpointEmbeddings  # 向量化客户端，用于将文本转换为向量以便进行语义检索