from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class ColumnMetricMySQL(Base):
    __tablename__ = "column_metric"

    column_id: Mapped[str] = mapped_column(
        ForeignKey("column_info.id"),
        primary_key=True,
        comment="列编号",
    )
    metric_id: Mapped[str] = mapped_column(
        ForeignKey("metric_info.id"),
        primary_key=True,
        comment="指标编号",
    )

    column: Mapped["ColumnInfoMySQL"] = relationship(back_populates="metrics")
    metric: Mapped["MetricInfoMySQL"] = relationship(back_populates="columns")
