import logging
import re

import gspread
from google.oauth2.service_account import Credentials


class GoogleSheetManager:
    def __init__(self, service_account_file: str, spreadsheet_id: str):
        """
        Инициализация менеджера для работы с Google Sheets.

        :param service_account_file: Путь к JSON-файлу с ключом сервисного аккаунта.
        :param spreadsheet_id: ID Google Sheets документа.
        """
        self.service_account_file = service_account_file
        self.spreadsheet_id = spreadsheet_id
        self.client = None
        self.sheet = None
        self._authenticate()

    def _authenticate(self):
        """Авторизация с использованием сервисного аккаунта."""
        scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        creds = Credentials.from_service_account_file(self.service_account_file, scopes=scopes)
        self.client = gspread.authorize(creds)
        self.sheet = self.client.open_by_key(self.spreadsheet_id)

    def update_range(self, worksheet_name: str, start_cell: str, data: dict):
        """
        Обновление данных в диапазоне ячеек Google Sheets с заголовками и значениями из словаря.

        :param worksheet_name: Имя листа (Sheet).
        :param start_cell: Начальная ячейка диапазона для заголовков (например, 'A1').
        :param data: Данные для обновления в виде словаря.
        """
        worksheet = self.sheet.worksheet(worksheet_name)

        # Определяем заголовки для столбцов
        headers = ["ID", "Ответственный врач", "Просрочка"]

        # Определение всех возможных стадий из данных (включаем уникальные стадии из всех записей)
        stages = set()
        for deal_data in data.values():
            stages.update(deal_data.keys())
        # Исключаем базовые поля из стадий
        stages.difference_update({"deal_id", "doc_name", "delay"})

        # Добавляем стадии в заголовки
        headers.extend(stages)

        # Преобразуем колонки из буквенной формы в числовую
        start_col_letter, start_row_number = re.match(r"([A-Z]+)(\d+)", start_cell).groups()
        start_row_number = int(start_row_number)
        start_col_number = self.column_letter_to_number(start_col_letter)

        # Логируем заголовки для проверки
        logging.debug(f"Заголовки для вставки: {headers}")

        # Вставляем заголовки в первую строку (например, A2)
        headers_range = f"{start_col_letter}{start_row_number}:{self.column_number_to_letter(start_col_number + len(headers) - 1)}{start_row_number}"
        logging.debug(f"Диапазон заголовков: {headers_range}")
        worksheet.update(headers_range, [headers])

        # Формируем строки данных
        rows = []
        for deal_id, deal_info in data.items():
            row = [
                deal_info.get("deal_id", ""),
                deal_info.get("doc_name", ""),
                deal_info.get("delay", ""),
            ]
            for stage in stages:
                row.append(deal_info.get(stage, ""))  # Вытаскиваем значения стадий, если есть, иначе пустая строка
            rows.append(row)

        # Начинаем вставку данных на строку ниже заголовков
        data_start_row = start_row_number + 1
        data_start_cell = f"{start_col_letter}{data_start_row}"

        # Определяем конечные координаты диапазона вставки данных
        end_row_number = data_start_row + len(rows) - 1
        end_col_letter = self.column_number_to_letter(start_col_number + len(headers) - 1)

        # Диапазон для вставки данных
        data_range = f"{data_start_cell}:{end_col_letter}{end_row_number}"
        logging.debug(f"Диапазон для данных: {data_range}")

        # Вставляем данные в диапазон под заголовками
        worksheet.update(data_range, rows)

    def clear_all_data(self, worksheet_name: str):
        """
        Удаление всех данных с указанного листа Google Sheets.

        :param worksheet_name: Имя листа (Sheet).
        """
        worksheet = self.sheet.worksheet(worksheet_name)
        worksheet.clear()  # Очищаем все данные на листе

    @staticmethod
    def column_number_to_letter(number: int) -> str:
        """Преобразует числовой индекс колонки в буквенное обозначение (например, 1 -> 'A', 2 -> 'B')."""
        result = ''
        while number > 0:
            number, remainder = divmod(number - 1, 26)
            result = chr(remainder + ord('A')) + result
        return result

    @staticmethod
    def column_letter_to_number(letter: str) -> int:
        """Преобразует букву колонки в числовой индекс (например, 'A' -> 1, 'B' -> 2)."""
        num = 0
        for c in letter:
            num = num * 26 + (ord(c.upper()) - ord('A')) + 1
        return num
