import json

from sqlalchemy import update, delete
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker
from sqlalchemy.future import select

from database.models import Deal


class DealRepo:
    def __init__(self, engine: AsyncEngine):
        self.session = async_sessionmaker(engine)

    async def get_all(self):
        async with self.session() as session:
            result = await session.scalars(select(Deal))
            return result.all()

    async def get_data_by_deal_id(self, id: int):
        async with self.session() as session:
            deal = await session.scalar(select(Deal).filter_by(deal_id=id))
            return json.loads(deal.data) if deal else None

    async def create(self, **data):
        async with self.session() as session:
            deal = Deal(**data)
            session.add(deal)
            await session.commit()
            await session.refresh(deal)
            return deal

    async def update_by_deal_id(self, id: int, data: str):
        async with self.session() as session:
            stmt = update(Deal).filter_by(deal_id=id).values(data=data).execution_options(
                synchronize_session="fetch")
            await session.execute(stmt)
            await session.commit()

            # Получаем обновленный объект после обновления
            deal = await session.scalar(select(Deal).filter_by(deal_id=id))
            if deal:
                await session.refresh(deal)
            return deal

    async def delete(self, id: int):
        async with self.session() as session:
            stmt = delete(Deal).filter_by(deal_id=id)
            await session.execute(stmt)
            await session.commit()

    async def create_update_deal(self, id: int, data):
        async with self.session() as session:
            # Ищем сделку с указанным id
            deal = await session.scalar(select(Deal).filter_by(deal_id=id))

            # Фильтруем пустые значения из входных данных
            filtered_data = {k: v for k, v in data.items() if v}

            if deal:
                # Преобразуем существующие данные из JSON-строки в словарь
                existing_data = json.loads(deal.data)
                # Обновляем словарь новыми данными, исключив пустые значения
                existing_data.update(filtered_data)
                # Преобразуем обновленный словарь обратно в JSON-строку и сохраняем
                deal.data = json.dumps(existing_data, ensure_ascii=False)
            else:
                # Если сделки с таким id нет, создаем новую с фильтрованными данными
                new_data = json.dumps(filtered_data, ensure_ascii=False)  # Преобразуем входные данные в JSON
                deal = Deal(deal_id=id, data=new_data)
                session.add(deal)

            # Сохраняем изменения в базе данных
            await session.commit()
            # Обновляем объект сделки после сохранения
            await session.refresh(deal)
            return deal