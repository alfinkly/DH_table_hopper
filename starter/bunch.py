import logging
from datetime import datetime, timedelta

import pytz
from babel.dates import format_timedelta
from pytz import FixedOffset
from sqlalchemy.ext.asyncio import AsyncEngine

from bitrix_.enums import DealCategory, Hopper
from bitrix_.manager import BitrixManager
from database.repo.deal import DealRepo
from sheet.manager import GoogleSheetManager
from starter import config
from starter.config import DotEnv, deal_stages

config = DotEnv()


async def fetch_data(list_name):
    logging.info("Подключаемся к Bitrix...")
    bitrix_manager = BitrixManager(config.BITRIX_REST_API)
    logging.info("Получаем данные сделок из Bitrix24...")
    deals = await bitrix_manager.get_deals_modified_last_days(list_name, days_ago=1)
    logging.info("Получаем стадии сделок из Bitrix24...")
    stages = await bitrix_manager.get_stages_for_category(list_name)
    logging.info("Получаем сотрудников из Bitrix24...")
    users = await bitrix_manager.get_all_users()
    return deals, stages, users


def calculate_working_hours(delta, start_time, working_start=10, working_end=20):
    """
    Рассчитывает количество времени, прошедшего в рамках рабочих часов.
    delta - разница времени между сейчас и временем перехода сделки на стадию.
    start_time - время перехода на стадию.
    working_start - начало рабочего времени (часы).
    working_end - конец рабочего времени (часы).
    """
    total_hours = 0
    current_time = start_time

    # Перебираем каждый день в диапазоне
    for day in range(delta.days + 1):
        day_start = datetime(current_time.year, current_time.month, current_time.day, working_start,
                             tzinfo=FixedOffset(300))
        day_end = datetime(current_time.year, current_time.month, current_time.day, working_end,
                           tzinfo=FixedOffset(300))

        if current_time < day_start:
            # Если время старта раньше рабочего дня, то начнем с рабочего времени
            current_time = day_start
        if current_time > day_end:
            # Если время старта позже конца рабочего дня, то начнем со следующего дня
            continue

        # Считаем количество рабочих часов за день
        if current_time < day_end:
            total_hours += min(delta.total_seconds() / 3600, (day_end - current_time).total_seconds() / 3600)

        # Переход на следующий день
        current_time = day_start + timedelta(days=1)
        delta -= timedelta(days=1)

    return timedelta(hours=total_hours)


# Обновляем функцию generate_row, чтобы учитывать рабочие часы
def generate_row(deal, stages, users, now):
    # Поиск врача
    user = next((u for u in users if u["ID"] == deal["ASSIGNED_BY_ID"]), {})
    fullname = f"{user.get('NAME', '')} {user.get('LAST_NAME', '')}"

    # Обработка времени движения по стадии
    moved_datetime = datetime.fromisoformat(deal["MOVED_TIME"])
    delta = now - moved_datetime  # Время, прошедшее с момента перехода на стадию

    # Перерасчет времени с учетом рабочих часов
    working_delta = calculate_working_hours(delta, moved_datetime)
    delta_str = format_timedelta(working_delta, locale="ru", format="long")

    # Генерация строки
    row = {
        "deal_id": deal["ID"],
        "doc_name": fullname,
        "delay": ""
    }

    # Добавляем стадии
    for stage in stages:
        stage_name = stage["NAME"]
        stage_id = stage["STATUS_ID"]

        # Если это текущая стадия сделки
        if stage_id == deal["STAGE_ID"]:
            # Проверка, просрочена ли стадия с учетом рабочих часов
            if stage_name in deal_stages and deal_stages[stage_name] and working_delta > deal_stages[stage_name]:
                row["delay"] = "Просрочено"

            # Запись времени, проведенного на стадии
            row[stage_name] = delta_str
        else:
            # Для остальных стадий пустое значение
            row[stage_name] = ""

    return row


def generate_matrix(deals, stages, users):
    now = datetime.now(tz=pytz.FixedOffset(300))

    # Генерация словаря, где ключи — это ID сделки
    matrix = {deal["ID"]: generate_row(deal, stages, users, now) for deal in deals}

    return matrix


async def update_data(engine: AsyncEngine, hopper_id, list_name):
    logging.info("Составляю таблицу...")
    deal_repo = DealRepo(engine)
    deals, stages, users = await fetch_data(list_name)
    matrix = generate_matrix(deals, stages, users)

    logging.info("Авторизуюсь в google sheets")

    google_sheet_manager = GoogleSheetManager(
        'service_account.json',
        config.SPREADSHEET_ID
    )

    for id, data in matrix.items():
        await deal_repo.create_update_deal(int(id), data)
    google_sheet_manager.clear_all_data(hopper_id)
    google_sheet_manager.update_range(hopper_id, "A1", matrix)
    logging.info("Данные успешно обновлены в Google Sheets.")
