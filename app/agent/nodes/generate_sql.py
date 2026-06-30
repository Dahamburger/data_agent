import yaml
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.llm import llm
from app.agent.state import DataAgentState
from app.core.log import logger
from app.prompt.load_prompt import load_prompt


async def generate_sql(state: DataAgentState, runtime: Runtime[DataAgentContext]):
	"""生成SQL节点

	根据用户查询、表信息、指标信息、日期信息和数据库信息，使用LLM生成SQL语句。

	:param state: DataAgentState，包含query、table_infos、metric_infos、date_info、db_info等状态信息
	:param runtime: Runtime[DataAgentContext]，包含llm等上下文
	:return: dict，包含sql键，值为生成的SQL语句
	"""
	writer = runtime.stream_writer
	writer({"type": "progress", "step": "生成SQL", "status": "running"})

	query = state["query"]
	table_infos = state["table_infos"]
	metric_infos = state["metric_infos"]
	date_info = state["date_info"]
	db_info = state["db_info"]

	try:
		prompt = PromptTemplate(template=load_prompt("generate_sql"),
			input_variables=["query", "table_infos", "metric_infos", "date_info", "db_info"])
		output_parser = StrOutputParser()

		chain = prompt | llm | output_parser

		result = await chain.ainvoke(
			{"query": query,
				"table_infos": yaml.dump(table_infos, allow_unicode=True, sort_keys=False),
				"metric_infos": yaml.dump(metric_infos, allow_unicode=True, sort_keys=False),
				"date_info": yaml.dump(date_info, allow_unicode=True, sort_keys=False),
				"db_info": yaml.dump(db_info, allow_unicode=True, sort_keys=False)
			})

		writer({"type": "progress", "step": "生成SQL", "status": "success"})
		logger.info(f"生成的SQL: {result}")
		return {"sql": result}
	except Exception as e:
		writer({"type": "progress", "step": "生成SQL", "status": "error"})
		logger.error(f"生成SQL失败: {str(e)}")
		raise