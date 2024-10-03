import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from bitrix_.enums import Hopper, DealCategory
from database.factory import DatabaseFactory
from database.models import Base
from starter.bunch import update_data
from starter.config import DotEnv

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(name)s - %(funcName)s - %(message)s')


async def main():
    """
    Запуск планировщика с задачей обновления данных из Bitrix24 и внесения в Google Sheets.
    """
    scheduler = AsyncIOScheduler()
    config = DotEnv()
    factory = DatabaseFactory(config)
    engine = await factory.get_async_engine()
    sync_engine = factory.get_engine()
    Base.metadata.create_all(sync_engine)

    scheduler.add_job(update_data, 'interval', seconds=60, max_instances=1,
                      kwargs={"engine": engine, "hopper_id": Hopper.OVK, "list_name": DealCategory.OVK})
    scheduler.add_job(update_data, 'interval', seconds=60, max_instances=1,
                      kwargs={"engine": engine, "hopper_id": Hopper.OK, "list_name": DealCategory.OK})
    # await update_data(engine, Hopper.OVK, DealCategory.OVK)
    # await update_data(engine, Hopper.OK, DealCategory.OK)
    scheduler.start()

    # Ожидаем, чтобы цикл событий работал бесконечно
    try:
        while True:
            await asyncio.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        print("Остановка планировщика...")
        scheduler.shutdown()


if __name__ == '__main__':
    asyncio.run(main())
