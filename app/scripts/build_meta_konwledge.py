import argparse
import asyncio
from pathlib import Path

from pydantic import with_config

from app.clients.mysql_client_manager import meta_mysql_client_manager, dw_mysql_client_manager
from app.core.log import logger
from app.repositories.mysql.dw.dw_mysql_repository import DWMySQLRepository
from app.repositories.mysql.meta.meta_mysql_repository import MetaMySQLRepository
from app.services.meta_knowledge_service import MetaKnowledgeService


async def build(config_path: Path):
    """
       构建元知识服务
       Args:
           config_path (Path): 配置文件的路径对象，指向用于构建元知识的配置信息
       Returns:
           None
       Raises:
           Exception: 当元知识构建过程中发生错误时抛出异常
       """
    meta_mysql_client_manager.init()
    dw_mysql_client_manager.init()
    async with meta_mysql_client_manager.session_factor() as meta_session, dw_mysql_client_manager.session_factor() as dw_session:
        try:
            # 创建MySQL仓库实例，用于数据库操作
            meta_mysql_repository = MetaMySQLRepository(meta_session)
            dw_mysql_repository = DWMySQLRepository(dw_session)
            # 创建实例，注入仓库依赖
            meta_knowledge_service = MetaKnowledgeService(meta_mysql_repository, dw_mysql_repository)
            # 异步执行构建流程，读取配置文件并生成元知识数据
            await meta_knowledge_service.build(config_path)
        finally:
            await meta_mysql_client_manager.close()
            await dw_mysql_client_manager.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c','--conf')

    args = parser.parse_args()
    config_path = args.conf
    print(config_path)
    asyncio.run(build(Path(config_path)))