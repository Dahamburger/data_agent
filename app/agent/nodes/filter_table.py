import yaml
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.llm import llm
from app.agent.state import DataAgentState, TableInfoState
from app.prompt.load_prompt import load_prompt
from app.core.log import logger


async def filter_table(state: DataAgentState, runtime: Runtime[DataAgentContext]):
	"""过滤表信息节点

	根据用户查询，使用LLM从所有可用的表信息中筛选出相关的表及其列。

	Args:
	    state: DataAgentState - 包含用户查询和所有表信息的状态
	    runtime: Runtime[DataAgentContext] - 运行时上下文，用于流式输出

	Returns:
	    dict: 包含过滤后的表信息，仅保留与查询相关的表和列

	功能说明:
	    1. 从state中获取用户查询和所有表信息
	    2. 使用LLM分析查询与表/列的相关性
	    3. 根据LLM返回的结果，过滤出相关的表和列
	    4. 返回过滤后的表信息列表
	"""
	writer = runtime.stream_writer
	writer({"type": "progress", "step": "过滤表信息", "status": "running"})
	query = state["query"]
	table_infos: list[TableInfoState] = state["table_infos"]
	prompt = PromptTemplate(template=load_prompt("filter_table_info"), input_variables=['query', 'table_infos'])
	output_parser = JsonOutputParser()
	chain = prompt | llm | output_parser

	try:
		result = await chain.ainvoke({"query": query,
							 "table_infos": yaml.dump(table_infos,sort_keys=False,allow_unicode=True)})
		# print(yaml.dump(table_infos,sort_keys=False,allow_unicode=True))

		filtered_table_infos: list[TableInfoState] = []
		for table_info in table_infos:
			if table_info["name"] in result:
				table_info["columns"] = [column_info for column_info in table_info["columns"]
				if column_info["name"] in result[table_info["name"]]]
				filtered_table_infos.append(table_info)
		writer({"type": "progress", "step": "过滤表信息", "status": "success"})
		logger.info(f"过滤后的表信息: {[table_info['name'] for table_info in filtered_table_infos]}")
		return {"table_infos": filtered_table_infos}
	except Exception as e:
		writer({"type": "progress", "step": "过滤表信息", "status": "error"})
		logger.error(f"过滤表信息失败: {str(e)}")
		raise


