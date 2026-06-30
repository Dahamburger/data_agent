from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.llm import llm
from app.agent.state import DataAgentState
from app.entities.metric_info import MetricInfo
from app.prompt.load_prompt import load_prompt
from app.core.log import logger


async def recall_metric(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    """召回指标节点

    使用LLM扩展关键词，然后通过向量检索从Qdrant中召回相关的指标信息。

    :param state: DataAgentState，包含query和keywords等状态信息
    :param runtime: Runtime[DataAgentContext]，包含metric_qdrant_repository和embedding_client等上下文
    :return: dict，包含retrieved_metric_infos键，值为检索到的指标信息列表
    """
    writer = runtime.stream_writer
    writer({"type": "progress", "step": "召回指标", "status": "running"})
    keywords = state["keywords"]
    metric_qdrant_repository = runtime.context["metric_qdrant_repository"]
    query = state["query"]

    try:
        # 借助LLM扩展关键词
        # prompt | llm |output_parser
        prompt = PromptTemplate(template=load_prompt("extend_keywords_for_metric_recall"), input_variables=['query'])
        output_parser = JsonOutputParser()
        chain = prompt | llm | output_parser
        result = await chain.ainvoke({"query": query})
        logger.info(f"LLM扩展的关键词: {result}")
        keywords = list(set(result + keywords))
        logger.info(f"扩展后的关键词: {keywords}")

        embedding_client = runtime.context["embedding_client"]
        # 从Qdrant中检索字段信息
        metric_infos_map: dict[str, MetricInfo] = {}
        for keyword in keywords:
            # 对keyword进行向量化
            embedding = await embedding_client.aembed_query(keyword)
            current_metric_infos: list[MetricInfo] = await metric_qdrant_repository.search(embedding)
            # 遍历去重
            for metric_info in current_metric_infos:
                if metric_info.id not in metric_infos_map:
                    metric_infos_map[metric_info.id] = metric_info
        retrieved_metric_infos: list[MetricInfo] = list(metric_infos_map.values())
        writer({"type": "progress", "step": "召回指标", "status": "success"})
        logger.info(f"检索到的指标信息: {list(metric_infos_map.keys())}")
        return {"retrieved_metric_infos": retrieved_metric_infos}
    except Exception as e:
        writer({"type": "progress", "step": "召回指标", "status": "error"})
        logger.error(f"召回指标失败: {str(e)}")
        raise
