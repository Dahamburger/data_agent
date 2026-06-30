from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState
from app.core.log import logger

async def validate_sql(state: DataAgentState, runtime: Runtime[DataAgentContext]):
	"""验证SQL节点

	验证SQL语句的语法正确性。

	:param state: DataAgentState，包含sql等状态信息
	:param runtime: Runtime[DataAgentContext]，包含dw_mysql_repository等上下文
	:return: dict，包含error键，验证成功时为None，失败时为错误信息
	"""
	writer = runtime.stream_writer
	writer({"type": "progress", "step": "验证SQL", "status": "running"})

	dw_mysql_repository = runtime.context["dw_mysql_repository"]

	sql = state["sql"]

	try:
		await dw_mysql_repository.validate_sql(sql)
		writer({"type": "progress", "step": "验证SQL", "status": "success"})
		logger.info(f"SQL验证成功: {sql}")
		return {"error": None}
	except Exception as e:
		writer({"type": "progress", "step": "验证SQL", "status": "error"})
		logger.error(f"SQL验证失败: {sql}")
		return {"error": str(e)}