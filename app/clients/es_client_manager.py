import asyncio

from elasticsearch import AsyncElasticsearch

from app.conf.app_config import ESConfig, app_config


class ElasticSearchClientManager:
    def __init__(self, config: ESConfig):
        self.client : AsyncElasticsearch | None = None
        self.config : ESConfig = config

    def _get_url(self):
        return f"http://{self.config.host}:{self.config.port}"

    def init(self):
        self.client = AsyncElasticsearch([self._get_url()])

    async def close(self):
        await self.client.close()

es_client_manager = ElasticSearchClientManager(app_config.es)
