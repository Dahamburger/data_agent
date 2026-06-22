from typing import List

from sqlalchemy import JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class MetricInfoMySQL(Base):
    __tablename__ = "metric_info"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, comment="指标编码")
    name: Mapped[str | None] = mapped_column(String(128), comment="指标名称")
    description: Mapped[str | None] = mapped_column(Text, comment="指标描述")
    relevant_columns: Mapped[list | None] = mapped_column(JSON, comment="关联的列")
    alias: Mapped[list | None] = mapped_column(JSON, comment="指标别名")

    columns: Mapped[List["ColumnMetricMySQL"]] = relationship(
        back_populates="metric",
        cascade="all, delete-orphan",
    )
