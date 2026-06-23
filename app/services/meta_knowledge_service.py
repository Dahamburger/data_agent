import uuid
from dataclasses import asdict
from pathlib import Path

from langchain_huggingface import HuggingFaceEndpointEmbeddings
from omegaconf import OmegaConf

from app.conf.meta_config import MetaConfig
from app.entities.column_info import ColumnInfo
from app.entities.table_info import TableInfo
from app.entities.value_info import ValueInfo
from app.repositories.es.value_es_repository import ValueESRepository
from app.repositories.mysql.dw.dw_mysql_repository import DWMySQLRepository
from app.repositories.mysql.meta.meta_mysql_repository import MetaMySQLRepository
from app.repositories.qdrant.column_qdrant_repository import ColumnQdrantRepository


class MetaKnowledgeService:
    def __init__(self,
                 meta_mysql_repository: MetaMySQLRepository,
                 dw_mysql_repository: DWMySQLRepository,
                 column_qdrant_repository: ColumnQdrantRepository,
                 embedding_client: HuggingFaceEndpointEmbeddings,
                 value_es_repository: ValueESRepository):
        self.meta_mysql_repository: MetaMySQLRepository = meta_mysql_repository
        self.dw_mysql_repository: DWMySQLRepository = dw_mysql_repository
        self.column_qdrant_repository: ColumnQdrantRepository = column_qdrant_repository
        self.embedding_client: HuggingFaceEndpointEmbeddings = embedding_client
        self.value_es_repository: ValueESRepository = value_es_repository

    async def build(self, config_path: Path):
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
                    column_values: list = await self.dw_mysql_repository.get_column_value(table.name, column.name, 10)
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
                await self.meta_mysql_repository.save_table_info(table_infos)
                await self.meta_mysql_repository.save_column_info(column_infos)
            # 2.2 对字段信息建立向量索引
            await self.column_qdrant_repository.ensure_collection()

            points: list[dict] = []
            for column_info in column_infos:
                points.append({
                    'id': uuid.uuid4(),
                    'embedding_text': column_info.name,
                    'payload': asdict(column_info)
                })

                points.append({
                    'id': uuid.uuid4(),
                    'embedding_text': column_info.description,
                    'payload': asdict(column_info)
                })

                for alia in column_info.alias:
                    points.append({
                        'id': uuid.uuid4(),
                        'embedding_text': alia,
                        'payload': asdict(column_info)
                    })
            # 向量化
            embeddings: list[list[float]] = []
            embedding_texts = [point['embedding_text'] for point in points]
            batch_embedding_size = 10
            for i in range(0, len(embedding_texts), batch_embedding_size):
                batch_embedding_texts = embedding_texts[i:i + batch_embedding_size]
                batch_embeddings = await self.embedding_client.aembed_documents(batch_embedding_texts)
                embeddings.extend(batch_embeddings)

            ids = [point['id'] for point in points]

            payloads = [point['payload'] for point in points]

            await self.column_qdrant_repository.upsert(embeddings, ids, payloads)

            # 2.3 对指定的维度字段建立全文索引
            await self.value_es_repository.ensure_index()

            value_infos: list[ValueInfo] = []
            for table in meta_config.tables:
                for column in table.columns:
                    if column.sync:
                        # 查询字段取值
                        column_values: list = await self.dw_mysql_repository.get_column_value(table.name, column.name,
                                                                                              100000)
                        [value_infos.append(ValueInfo(id=f"{table.name}.{column.name}.{value}", value=value,
                                                 column_id=f"{table.name}.{column.name}")) for value in column_values]
            await self.value_es_repository.index(value_infos)

        # 3.根据配置文件同步指定的指标信息
        if meta_config.metrics:
            # 3.1 将指标信息保存到meta数据库中
            for metric_config in meta_config.metrics:
                pass
            # 3.2 对指标信息建立向量索引

            # 3.3 对指定的指标字段建立全文索引
