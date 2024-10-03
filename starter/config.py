import datetime

from environs import Env


class DotEnv:
    def __init__(self):
        env = Env()
        env.read_env(".env")
        self.DB_NAME = env.str('DB_NAME')
        self.DB_HOST = env.str('DB_HOST')
        self.DB_PASSWORD = env.str('DB_PASSWORD')
        self.DB_USER = env.str('DB_USER')
        self.DB_PORT = env.str('DB_PORT')
        self.BITRIX_REST_API = env.str('BITRIX_REST_API')
        self.SHEET_KEY = env.str('SHEET_KEY')
        self.SPREADSHEET_ID = env.str("SPREADSHEET_ID")

    def psycopg_url(self):
        return f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    def asyncpg_url(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


deal_stages = {
    "Новая заявка": datetime.timedelta(hours=3),
    "АНАМНЕЗ В ПРОЦЕССЕ": datetime.timedelta(days=2),
    "1-КОНСУЛЬТАЦИЯ": datetime.timedelta(days=2),
    "ЖДЕМ ДОКУМЕНТЫ": datetime.timedelta(days=2),
    "ОТПРАВИТЬ ЗАПРОС В КЛИНИКУ": datetime.timedelta(hours=1),
    "ЗАПРОСЫ В КЛИНИКИ ОТПРАВЛЕНЫ": datetime.timedelta(days=2),
    "ОТВЕТ С КЛИНИКИ ПОСТУПИЛ": datetime.timedelta(hours=2, minutes=30),
    "ВСЕ ОТВЕТЫ ПОСТУПИЛИ": datetime.timedelta(hours=2),
    "ШАБЛОННЫЕ ОТВЕТЫ": datetime.timedelta(days=1),
    "ПОДГОТОВИТЬ ОТВЕТ": datetime.timedelta(hours=4, minutes=30),
    "ОТВЕТ ГОТОВ": datetime.timedelta(hours=2),
    "2-КОНСУЛЬТАЦИЯ": datetime.timedelta(days=2),
    "В ПРОЦЕССЕ": datetime.timedelta(days=2),
    "Подготовка документов к К-ЕТА,Виза": datetime.timedelta(days=2),
    "Подали документы": datetime.timedelta(days=9),
    "К-ЕТА,Виза одобрена,отказана": datetime.timedelta(hours=4),
    "Перечитка снимков и стеклоблоков": None,  # Не указано точное время
    "Планируют позже": datetime.timedelta(weeks=2),
    "Необходима запись в клинику": datetime.timedelta(hours=2),
    "Запросили запись клинику": datetime.timedelta(days=1, hours=12),
    "дата приема назначена": datetime.timedelta(hours=4),
    "ОПД": None,
    "Успешно реализовано": None,
    "НОВАЯ ЗАЯВКА": datetime.timedelta(hours=1),
    "НЕ ДОЗВОН/ НЕТ ОТВЕТА": datetime.timedelta(days=2),
    "ПРИНИМАЕТ РЕШЕНИЕ": datetime.timedelta(weeks=2),
    "Отложенная заявка": None,
    "СЧЕТ ВЫСТАВЛЕН": datetime.timedelta(days=1),
    "ПОТЕНЦИАЛЬНЫЙ КЛИЕНТ": datetime.timedelta(weeks=1),
}