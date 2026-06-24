from struct import error

from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState


async def validate_sql(state: DataAgentState, runtime: Runtime[DataAgentContext]):
	"""Node stub: validate_sql

	Args:
		state: DataAgentState
		runtime: Runtime[DataAgentContext]

	"""
	return {"error": None}
