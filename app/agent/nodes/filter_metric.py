import yaml
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.llm import llm
from app.agent.state import DataAgentState, MetricInfoState
from app.prompt.load_prompt import load_prompt
from app.core.log import logger


async def filter_metric(state: DataAgentState, runtime: Runtime[DataAgentContext]):
	"""过滤指标信息节点

	根据用户查询，使用LLM从所有可用的指标信息中筛选出相关的指标。

	Args:
	    state: DataAgentState - 包含用户查询和所有指标信息的状态
	    runtime: Runtime[DataAgentContext] - 运行时上下文，用于流式输出

	Returns:
	    dict: 包含过滤后的指标信息，仅保留与查询相关的指标

	功能说明:
	    1. 从state中获取用户查询和所有指标信息
	    2. 使用LLM分析查询与指标的相关性
	    3. 根据LLM返回的结果，过滤出相关的指标
	    4. 返回过滤后的指标信息列表
	"""
	writer = runtime.stream_writer
	writer({"type": "progress", "step": "过滤指标信息", "status": "running"})
	query = state["query"]
	metric_infos: list[MetricInfoState] = state["metric_infos"]
	prompt = PromptTemplate(template=load_prompt("filter_metric_info"), input_variables=['query', 'metric_infos'])
	output_parser = JsonOutputParser()
	chain = prompt | llm | output_parser

	try:
		result = await chain.ainvoke({"query": query,
									  "metric_infos": yaml.dump(metric_infos, allow_unicode=True, sort_keys=False)})
		filtered_metric_infos = [metric_info for metric_info in metric_infos if metric_info["name"] in result]
		writer({"type": "progress", "step": "过滤指标信息", "status": "success"})
		logger.info(f"过滤后的指标信息: {[filtered_metric_info['name'] for filtered_metric_info in filtered_metric_infos]}")
		return {"metric_infos": filtered_metric_infos}
	except Exception as e:
		writer({"type": "progress", "step": "过滤指标信息", "status": "error"})
		logger.error(f"过滤指标信息失败: {str(e)}")
		raise

