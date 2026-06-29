from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.entities.column_info import ColumnInfo
from app.entities.table_info import TableInfo
from app.models import ColumnInfoMySQL, TableInfoMySQL
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

    async def get_column_info_by_id(self, id: str)->ColumnInfo | None:
        column_info_mysql: ColumnInfoMySQL | None =  await self.session.get(ColumnInfoMySQL, id)
        if column_info_mysql:
            return ColumnInfoMapper.to_entity(column_info_mysql)
        return None

    async def get_table_info_by_id(self, id: str)->TableInfo | None:
        table_info_mysql: TableInfoMySQL | None =  await self.session.get(TableInfoMySQL, id)
        if table_info_mysql:
            return TableInfoMapper.to_entity(table_info_mysql)
        return None

    async def get_key_columns_by_table_id(self, table_id):
        result = await self.session.execute(
            text(
                "SELECT * FROM column_info "
                "WHERE table_id = :table_id AND role IN ('primary_key', 'foreign_key')"
            ),
            {"table_id": table_id}
        )
        return [ColumnInfoMapper.to_entity(row) for row in result.fetchall()]
