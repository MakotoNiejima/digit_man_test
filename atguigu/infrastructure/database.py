from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import text

from atguigu.config.settings import settings

engine: AsyncSession | None = None
session_factory :async_sessionmaker[AsyncSession] | None = None

async def init_db_engine():
    global engine, session_factory
    engine = create_async_engine(settings.database_url,echo=True)
    session_factory = async_sessionmaker(engine,expire_on_commit=False)

async def dispose_engine():
    await engine.close()

async def main():
    await init_db_engine()

    async with session_factory() as session:
        result = await session.execute(text("select 1"))
        print("------------")
        print(result.fetchone())

import asyncio

if __name__ == "__main__":
    asyncio.run(main())