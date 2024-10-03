import logging

from bitrix24 import Bitrix24
import datetime


class BitrixManager:
    def __init__(self, api_url: str):
        """
        Инициализация менеджера для работы с API Bitrix24.

        :param api_url: URL для доступа к Bitrix24 REST API.
        """
        self.bitrix = Bitrix24(api_url)

    async def get_deal_list(self):
        """
        Получение списка всех сделок (crm.deal.list).

        :return: Список сделок.
        """
        try:
            deals = await self.bitrix.callMethod(method='crm.deal.list')
            return deals
        except Exception as e:
            logging.error(f"Ошибка при получении списка сделок: {e}")
            return None

    async def get_lead_list(self, days_ago: int = 1):
        """
        Получение списка лидов, измененных за последние несколько дней (crm.lead.list).

        :param days_ago: Количество дней назад для фильтрации по дате изменения.
        :return: Список лидов.
        """
        try:
            now = datetime.datetime.now() - datetime.timedelta(days=days_ago)
            filter_data = {
                ">DATE_MODIFY": now.strftime("%Y-%m-%d %H:%M:%S"),
            }
            result = await self.bitrix.callMethod(
                method='crm.lead.list',
                filter=filter_data,
                select=["*", "UF_*"]
            )
            return result
        except Exception as e:
            logging.error(f"Ошибка при получении списка лидов: {e}")
            return None

    async def get_deals_modified_last_days(self, category_id: int, days_ago: int = 1):
        """
        Получение списка сделок, измененных за последние несколько дней (crm.deal.list).

        :param category_id: ID Воронки
        :param days_ago: Количество дней назад для фильтрации по дате изменения.
        :return: Список сделок.
        """
        try:
            now = datetime.datetime.now() - datetime.timedelta(days=days_ago)
            filter_data = {
                ">DATE_MODIFY": now.strftime("%Y-%m-%d %H:%M:%S"),
                "CATEGORY_ID": category_id
            }
            result = await self.bitrix.callMethod(
                method='crm.deal.list',
                filter=filter_data,
                select=["*"]
            )
            return result
        except Exception as e:
            logging.error(f"Ошибка при получении списка сделок: {e}")
            return None

    async def get_deal_categories(self):
        """
        Получение списка воронок (категорий сделок).

        :return: Список воронок.
        """
        try:
            categories = await self.bitrix.callMethod(method='crm.dealcategory.list')
            return categories
        except Exception as e:
            logging.error(f"Ошибка при получении воронок: {e}")
            return None

    async def get_stages_for_category(self, category_id):
        """
        Получение стадий для указанной воронки.

        :param category_id: ID воронки.
        :return: Список стадий воронки.
        """
        try:
            stages = await self.bitrix.callMethod(
                method='crm.dealcategory.stage.list',
                id=category_id
            )
            return stages
        except Exception as e:
            logging.error(f"Ошибка при получении стадий для воронки {category_id}: {e}")
            return None

    async def get_all_users(self):
        """
        Получение списка всех сотрудников (user.get).

        :return: Список пользователей.
        """
        try:
            users = await self.bitrix.callMethod(
                method='user.get',
                start=0,
                order={"ID": "ASC"},
                select=["ID", "NAME", "LAST_NAME", "SECOND_NAME", "EMAIL", "ACTIVE", "WORK_POSITION"]
            )

            logging.info(f'Всего получено пользователей: {len(users)}.')
            return users
        except Exception as e:
            logging.error(f"Ошибка при получении списка пользователей: {e}")
            return None