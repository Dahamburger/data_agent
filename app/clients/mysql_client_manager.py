import asyncio

from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.expression import text

from app.conf.app_config import DBConfig, app_config


class MysqlClientManager:

    def __init__(self, config: DBConfig):
        self.engine: AsyncEngine | None = None
        self.session_factory = None
        self.config = config

    def _get_url(self):
        return f"mysql+asyncmy://{self.config.user}:{self.config.password}@{self.config.host}:{self.config.port}/{self.config.database}?charset=utf8mb4"

    def init(self):
        # 创建异步数据库引擎，配置连接池参数：
        # pool_size=10: 连接池最大连接数为10
        # pool_pre_ping=True: 每次从连接池获取连接前先检测连接有效性
        self.engine = create_async_engine(self._get_url(),pool_size=10,pool_pre_ping=True)
        # 创建异步会话工厂，配置会话参数：
        # expire_on_commit=False: 提交后不使对象属性过期，避免后续访问时重新查询
        # class_=AsyncSession: 使用异步会话类
        # autoflush=True: 自动刷新会话中的待处理更改到数据库
        self.session_factory = sessionmaker(self.engine, expire_on_commit=False, class_=AsyncSession,autoflush=True)
    async def close(self):
        await self.engine.dispose()

meta_mysql_client_manager = MysqlClientManager(app_config.db_meta)
dw_mysql_client_manager = MysqlClientManager(app_config.db_dw)

# if __name__ == '__main__':
#     dw_mysql_client_manager.init()
#     engine = dw_mysql_client_manager.engine
#     Session = dw_mysql_client_manager.session_factor()
#     print(type(Session))
#
#     async def test():
#         async with Session as session:
#             sql = "select * from fact_order limit 10"
#             result = await session.execute(text(sql))
#             rows = result.mappings().fetchall()
#             print(type(rows))
#             print(rows)
#
#     asyncio.run(test())
