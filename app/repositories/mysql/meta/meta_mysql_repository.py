from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.entities.column_info import ColumnInfo
from app.entities.table_info import TableInfo
from app.repositories.mysql.meta.mappers.column_info_mapper import ColumnInfoMapper
from app.repositories.mysql.meta.mappers.column_metric_mapper import ColumnMetricMapper
from app.repositories.mysql.meta.mappers.metric_info_mapper import MetricInfoMapper
from app.repositories.mysql.meta.mappers.table_info_mapper import TableInfoMapper


class MetaMySQLRepository:
    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session

    # def save_table_info(self, table_infos: list[TableInfo]):
    #     self.session.add_all([TableInfoMapper.to_model(table_info) for table_info in table_infos])
    #
    # def save_column_info(self, column_infos: list[ColumnInfo]):
    #     self.session.add_all([ColumnInfoMapper.to_model(column_info) for column_info in column_infos])
    async def save_table_info(self, table_infos: list[TableInfo]):
        for table_info in table_infos:
            await self.session.merge(TableInfoMapper.to_model(table_info))

    async def save_column_info(self, column_infos: list[ColumnInfo]):
        for column_info in column_infos:
            await self.session.merge(ColumnInfoMapper.to_model(column_info))

    async def save_metric_infos(self, metric_info):
        for metric in metric_info:
            await self.session.merge(MetricInfoMapper.to_model(metric))

    async def save_column_metrics(self, column_metrics):
        for column_metric in column_metrics:
            await self.session.merge(ColumnMetricMapper.to_model(column_metric))