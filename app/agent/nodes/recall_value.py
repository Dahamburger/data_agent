from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.llm import llm
from app.agent.state import DataAgentState
from app.entities.value_info import ValueInfo
from app.prompt.load_prompt import load_prompt
from app.core.log import logger


async def recall_value(state: DataAgentState, runtime: Runtime[DataAgentContext]):
	"""召回字段取值节点

	使用LLM扩展关键词，然后通过Elasticsearch检索相关的字段取值信息。

	:param state: DataAgentState，包含query和keywords等状态信息
	:param runtime: Runtime[DataAgentContext]，包含value_es_repository等上下文
	:return: dict，包含retrieved_value_infos键，值为检索到的字段取值信息列表
	"""
	writer = runtime.stream_writer
	writer({"type": "progress", "step": "召回字段取值", "status": "running"})

	keywords = state["keywords"]
	query = state["query"]
	value_es_repository = runtime.context["value_es_repository"]

	try:
		# 借助LLM扩展关键词
		# prompt | llm |output_parser
		prompt = PromptTemplate(template=load_prompt("extend_keywords_for_value_recall"), input_variables=['query'])
		output_parser = JsonOutputParser()
		chain = prompt | llm | output_parser
		result = await chain.ainvoke({"query": query})
		logger.info(f"LLM扩展的关键词: {result}")
		keywords = list(set(result + keywords))
		logger.info(f"扩展后的关键词: {keywords}")

		# 从es中检索字段信息
		value_infos_map: dict[str, ValueInfo] = {}
		for keyword in keywords:
			current_value_infos: list[ValueInfo] = await value_es_repository.search(keyword)
			# 遍历去重
			for value_info in current_value_infos:
				if value_info.id not in value_infos_map:
					value_infos_map[value_info.id] = value_info
		retrieved_value_infos: list[ValueInfo] = list(value_infos_map.values())
		writer({"type": "progress", "step": "召回字段取值", "status": "success"})
		logger.info(f"检索到的字段取值: {list(value_infos_map.keys())}")
		return {"retrieved_value_infos": retrieved_value_infos}
	except Exception as e:
		writer({"type": "progress", "step": "召回字段取值", "status": "error"})
		logger.error(f"召回字段取值失败: {str(e)}")
		raise
