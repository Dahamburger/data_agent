import uuid

from app.api.lifespan import lifespan
from app.api.routers.query_router import query_router
from app.core.context import request_id_ctx_var
from app.core.log import logger
from fastapi import FastAPI,Request


logger.info("初始化完成")
app = FastAPI(lifespan=lifespan)
app.include_router(query_router)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    request_id = uuid.uuid4()
    # 设置请求ID到上下文变量中
    request_id_ctx_var.set(request_id)
    response = await call_next(request)
    return response