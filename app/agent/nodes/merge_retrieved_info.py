from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState, TableInfoState, ColumnInfoState, MetricInfoState
from app.entities.column_info import ColumnInfo
from app.entities.metric_info import MetricInfo
from app.entities.value_info import ValueInfo
from app.repositories.mysql.meta.meta_mysql_repository import MetaMySQLRepository
from app.core.log import logger


async def merge_retrieved_info(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    """将各路召回结果（字段、取值、指标）合并为统一的表结构状态，补全缺失的元数据。"""
    writer = runtime.stream_writer
    writer("合并召回信息")

    retrieved_column_infos: list[ColumnInfo] = state["retrieved_column_infos"]
    retrieved_value_infos: list[ValueInfo] = state["retrieved_value_infos"]
    retrieved_metric_infos: list[MetricInfo] = state["retrieved_metric_infos"]

    meta_mysql_repository: MetaMySQLRepository = runtime.context["meta_mysql_repository"]

    # 以字段ID为键构建初始字段映射，方便后续去重与补全
    retrieved_column_infos_map: dict[str, ColumnInfo] = {retrieved_column_info.id: retrieved_column_info for
                                                         retrieved_column_info in retrieved_column_infos}

    async def ensure_column_info(column_id: str) -> ColumnInfo | None:
        if column_id in retrieved_column_infos_map:
            return retrieved_column_infos_map[column_id]

        column_info = await meta_mysql_repository.get_column_info_by_id(column_id)
        if column_info is None:
            logger.warning("字段元数据不存在，跳过合并: column_id={}", column_id)
            return None

        retrieved_column_infos_map[column_id] = column_info
        return column_info

    # 指标可能关联了字段召回结果中未包含的字段，逐一从数据库补全
    for retrieved_metric_info in retrieved_metric_infos:
        for relevant_column in retrieved_metric_info.relevant_columns:
            await ensure_column_info(relevant_column)

    # 将召回的字段取值追加到对应字段的 examples 中，同样补全未收录的字段
    for retrieved_value_info in retrieved_value_infos:
        value = retrieved_value_info.value
        column_id = retrieved_value_info.column_id
        column_info = await ensure_column_info(column_id)
        if column_info is None:
            continue
        if value not in column_info.examples:
            column_info.examples.append(value)


    # 按 table_id 将所有字段归组，再逐表查询表元信息，组装成 TableInfoState
    table_infos: list[TableInfoState] = []
    table_to_columns_map: dict[str, list[ColumnInfo]] = {}
    for column_info in retrieved_column_infos_map.values():
        table_id = column_info.table_id
        if table_id not in table_to_columns_map:
            table_to_columns_map[table_id] = []
        table_to_columns_map[table_id].append(column_info)

    # 强制为每个表添加主外键字段
    for table_id in table_to_columns_map.keys():
        key_columns: list[ColumnInfo] = await meta_mysql_repository.get_key_columns_by_table_id(table_id)
        column_ids = [column_info.id for column_info in table_to_columns_map[table_id]]
        for key_column in key_columns:
            if key_column.id not in column_ids:
                table_to_columns_map[table_id].append(key_column)

    for table_id, column_infos in table_to_columns_map.items():
        table_info = await meta_mysql_repository.get_table_info_by_id(table_id)
        columns = [ColumnInfoState(
            name=column_info.name,
            description=column_info.description,
            role=column_info.role,
            examples=column_info.examples
        ) for column_info in column_infos]
        table_info_state = TableInfoState(
            name=table_info.name,
            description=table_info.description,
            role=table_info.role,
            columns=columns
        )
        table_infos.append(table_info_state)

    # 处理指标信息
    # metric_infos: list[MetricInfoState]
    metric_infos: list[MetricInfoState] = [MetricInfoState(
        name= retrieved_metric_info.name,
        description=retrieved_metric_info.description,
        relevant_columns=retrieved_metric_info.relevant_columns,
        alias=retrieved_metric_info.alias
    ) for retrieved_metric_info in retrieved_metric_infos]

    logger.info("合并召回信息完成，table_infos: %s, metric_infos: %s", table_infos, metric_infos)
    return {
        "table_infos":table_infos,
        "metric_infos":metric_infos
    }
