from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.llm import llm
from app.agent.state import DataAgentState
from app.core.log import logger
from app.entities.column_info import ColumnInfo
from app.prompt.load_prompt import load_prompt


async def recall_column(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    """召回列名节点

    使用LLM扩展关键词，然后通过向量检索从Qdrant中召回相关的列信息。

    :param state: DataAgentState，包含query和keywords等状态信息
    :param runtime: Runtime[DataAgentContext]，包含column_qdrant_repository和embedding_client等上下文
    :return: dict，包含retrieved_column_infos键，值为检索到的列信息列表
    """
    writer = runtime.stream_writer
    writer({"type": "progress", "step": "召回列名", "status": "running"})
    keywords = state["keywords"]
    column_qdrant_repository = runtime.context["column_qdrant_repository"]
    query = state["query"]

    try:
        # 借助LLM扩展关键词
        # prompt | llm |output_parser
        prompt = PromptTemplate(template=load_prompt("extend_keywords_for_column_recall"), input_variables=['query'])
        output_parser = JsonOutputParser()
        chain = prompt | llm | output_parser
        result = await chain.ainvoke({"query": query})
        logger.info(f"LLM扩展的关键词: {result}")
        keywords = list(set(result + keywords))
        logger.info(f"扩展后的关键词: {keywords}")

        embedding_client = runtime.context["embedding_client"]
        # 从Qdrant中检索字段信息
        column_infos_map: dict[str, ColumnInfo] = {}
        for keyword in keywords:
            # 对keyword进行向量化
            embedding = await embedding_client.aembed_query(keyword)
            current_column_infos: list[ColumnInfo] = await column_qdrant_repository.search(embedding)
            # 遍历去重
            for column_info in current_column_infos:
                if column_info.id not in column_infos_map:
                    column_infos_map[column_info.id] = column_info
        retrieved_column_infos: list[ColumnInfo] = list(column_infos_map.values())
        writer({"type": "progress", "step": "召回列名", "status": "success"})
        logger.info(f"检索到的字段信息: {list(column_infos_map.keys())}")
        return {"retrieved_column_infos": retrieved_column_infos}
    except Exception as e:
        writer({"type": "progress", "step": "召回列名", "status": "error"})
        logger.error(f"召回列名失败: {str(e)}")
        raise
