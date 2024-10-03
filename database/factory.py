from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine


class DatabaseFactory:
    def __init__(self, config):
        self.config = config

    async def get_async_engine(self, echo=False):
        async_engine = create_async_engine(
            url=self.config.asyncpg_url(),
            echo=echo
        )
        return async_engine

    def get_engine(self):
        async_engine = create_engine(
            url=self.config.psycopg_url(),
            echo=False
        )
        return async_engine
