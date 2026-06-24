from typing import TypedDict

from app.entities.column_info import ColumnInfo
from app.entities.metric_info import MetricInfo


class DataAgentState(TypedDict):
    query: str  # 用户提问
    keywords: str
    retrieved_column_infos: list[ColumnInfo]  # 检索到的字段信息
    retrieved_metric_infos: list[MetricInfo]  # 检索到的指标信息
    error: str | None  # 校验sql出现的错误信息
