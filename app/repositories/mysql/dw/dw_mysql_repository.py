from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class DWMySQLRepository:
    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session

    async def get_column_types(self, table_name: str) -> dict[str, str]:
        """
        从 information_schema 中查询表的字段类型

        Args:
            table_name: 表名

        Returns:
            字典，键为字段名，值为字段类型（如 'VARCHAR(20)', 'INT' 等）
        """
        sql = f"show columns from {table_name}"
        result = await self.session.execute(text(sql))
        return {row.Field: row.Type for row in result.fetchall()}

    async def get_column_value(self, table_name, column_name, limit=10):
        """
        获取表中指定字段的去重值列表

        Args:
            table_name: 表名
            column_name: 字段名
            limit: 返回结果的最大数量，默认为10

        Returns:
            字段值的列表，已去重
        """
        sql = f"select distinct {column_name} from {table_name} limit {limit}"
        result = await self.session.execute(text(sql))
        # return [row[0] for row in result.fetchall()]
        return result.scalars().fetchall()