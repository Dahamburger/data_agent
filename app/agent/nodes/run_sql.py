from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState
from app.core.log import logger

async def run_sql(state: DataAgentState, runtime: Runtime[DataAgentContext]):
	"""执行SQL节点

	在数据仓库中执行SQL查询并返回结果。

	:param state: DataAgentState，包含sql等状态信息
	:param runtime: Runtime[DataAgentContext]，包含dw_mysql_repository等上下文
	:return: dict，包含执行结果数据
	"""
	writer = runtime.stream_writer
	writer({"type": "progress", "step": "执行SQL", "status": "running"})

	sql = state["sql"]

	dw_mysql_repository = runtime.context["dw_mysql_repository"]

	try:
		result = await dw_mysql_repository.execute_sql(sql)

		writer({"type": "progress", "step": "执行SQL", "status": "success"})
		writer({"type": "result", "data": result})
		logger.info(f"执行SQL结果: {result}")

	except Exception as e:
		writer({"type": "progress", "step": "执行SQL", "status": "error"})
		logger.error(f"执行SQL失败:{str(e)}")
		raise