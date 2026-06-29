from dataclasses import asdict

from elasticsearch import AsyncElasticsearch

from app.entities.value_info import ValueInfo


class ValueESRepository:
    index_name = "value_index"
    index_mappings = {
        "dynamic": False,
        "properties": {
            "id": {"type": "keyword"},
            "value": {"type": "text", "analyzer": "ik_max_word", "search_analyzer": "ik_max_word"},
            "column_id": {"type": "keyword"},
        }
    }

    def __init__(self, es_client: AsyncElasticsearch):
        self.es_client = es_client

    async def ensure_index(self):
        """
        确保 Elasticsearch 索引存在，如果不存在则创建

        该方法会检查名为 value_index 的索引是否已存在，如果不存在则创建该索引
        并应用预定义的映射配置。这是一个幂等操作，可以安全地多次调用。

        索引映射配置：
        - id: keyword 类型，用于精确匹配
        - value: text 类型，使用 ik_max_word 分词器进行中文分词
        - column_id: keyword 类型，用于精确匹配
        - dynamic: False，禁止动态映射

        :return: None
        """
        if not await self.es_client.indices.exists(index=self.index_name):
            await self.es_client.indices.create(
                index=self.index_name,
                mappings=self.index_mappings
            )

    async def index(self, value_infos: list[ValueInfo], batch_size=20):
        for i in range(0, len(value_infos), batch_size):
            batch_value_infos = value_infos[i:i + batch_size]
            batch_options = []
            for batch_value_info in batch_value_infos:
                batch_options.append({"index": {"_index": self.index_name, "_id": batch_value_info.id}})
                batch_options.append(asdict(batch_value_info))
            await self.es_client.bulk(operations=batch_options)

    async def search(self, keyword, min_score: float = 0.6, limit: int = 10) -> list[ValueInfo]:
        """
        在 Elasticsearch 中搜索与给定关键词相关的 ValueInfo 对象

        该方法会在名为 value_index 的索引中执行搜索操作，查找与提供的关键词相关的 ValueInfo 对象。
        搜索结果会根据相关性得分进行排序，并返回得分高于指定阈值的结果。

        :param keyword: str，要搜索的关键词
        :param min_score: float，搜索结果的最小得分阈值
        :param limit: int，返回结果的最大数量，默认为 10
        :return: list[ValueInfo]，包含搜索到的 ValueInfo 对象列表
        """
        query = {
            "query": {
                "multi_match": {
                    "query": keyword,
                    "fields": ["value"]
                }
            }
        }
        response = await self.es_client.search(index=self.index_name, body=query, min_score=min_score, size=limit)
        hits = response['hits']['hits']
        return [ValueInfo(**hit['_source']) for hit in hits]
