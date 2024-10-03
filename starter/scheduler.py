import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler


class GoogleSheetTaskScheduler:
    def __init__(self, google_sheet_manager):
        """
        Инициализация планировщика для Google Sheets.

        :param google_sheet_manager: Экземпляр класса, который управляет взаимодействием с Google Sheets.
        """
        self.scheduler = AsyncIOScheduler()
        self.google_sheet_manager = google_sheet_manager

    def start(self):
        """Запуск планировщика с асинхронной задачей."""
        self.scheduler.start()

        # Запуск asyncio event loop
        try:
            asyncio.get_event_loop().run_forever()
        except (KeyboardInterrupt, SystemExit):
            print("Планировщик остановлен.")
            self.scheduler.shutdown()