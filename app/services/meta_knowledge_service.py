from pathlib import Path
from app.core.log import logger

from omegaconf import OmegaConf

from app.conf.meta_config import MetaConfig
from app.entities.table_info import TableInfo
from app.entities.column_info import ColumnInfo
from app.repositories.mysql.dw.dw_mysql_repository import DWMySQLRepository
from app.repositories.mysql.meta.meta_mysql_repository import MetaMySQLRepository


class MetaKnowledgeService:
    def __init__(self,meta_mysql_repository: MetaMySQLRepository,dw_mysql_repository: DWMySQLRepository):
        self.meta_mysql_repository: MetaMySQLRepository = meta_mysql_repository
        self.dw_mysql_repository: DWMySQLRepository = dw_mysql_repository

    async def build(self,config_path: Path):
        # 1.读取配置文件
        context = OmegaConf.load(config_path)
        schema = OmegaConf.structured(MetaConfig)
        meta_config: MetaConfig = OmegaConf.to_object(OmegaConf.merge(schema, context))
        # 2.根据配置文件同步指定的表信息
        if meta_config.tables:
            # 2.1 将表信心的字段信息保存到meta数据库中
            table_infos: list[TableInfo] = []
            column_infos: list[ColumnInfo] = []
            for table in meta_config.tables:
                # table -> table_info
                # 从DW数据库获取表的字段类型信息
                column_types: dict[str, str] = await self.dw_mysql_repository.get_column_types(table.name)
                # logger.info(column_types)
                table_info = TableInfo(
                    id=table.name,
                    name=table.name,
                    role=table.role,
                    description=table.description,
                )
                table_infos.append(table_info)
                for column in table.columns:
                    # colum n -> column_info
                    # 从dw表中查字段取值
                    column_values:list = await self.dw_mysql_repository.get_column_value(table.name, column.name,10)
                    # logger.info(column_values)
                    column_type = column_types.get(column.name, None)
                    column_info = ColumnInfo(
                        id=f"{table.name}.{column.name}",
                        name=column.name,
                        type=column_type,
                        role=column.role,
                        examples=column_values,
                        description=column.description,
                        alias=column.alias,
                        table_id=table.name,
                    )
                    column_infos.append(column_info)
            # 开启事务，批量保存表信息和字段信息到meta数据库
            async with self.meta_mysql_repository.session.begin():
                self.meta_mysql_repository.save_table_info(table_infos)
                self.meta_mysql_repository.save_column_info(column_infos)
             # 2.2 对字段信息建立向量索引

             # 2.3 对指定的维度字段建立全文索引

        # 3.根据配置文件同步指定的指标信息
        if meta_config.metrics:
            # 3.1 将指标信息保存到meta数据库中
            for metric_config in meta_config.metrics:
                pass
            # 3.2 对指标信息建立向量索引

            # 3.3 对指定的指标字段建立全文索引