import logging
import sys

from PySide6.QtWidgets import QApplication

from CORE.logger import setup_logging, AppLogger
from DA3.controller import Controller
from DA3.main_form import MainForm
from DA3.model import Model


def main():
    # Настраиваем логирование
    setup_logging(
        level=logging.INFO,
        log_file="app.log"  # Лог будет писаться в app.log
    )
    # Устанавливаем хук для неперехваченных исключений
    AppLogger.install_uncaught_exception_hook(log_name="uncaught")

    logger = logging.getLogger(__name__)

    # Создаем экземпляр приложения Qt
    app = QApplication(sys.argv)

    # Создаем модель
    logger.info("Создание модели...")
    model = Model()

    # Создаем главное окно
    logger.info("Создание главного окна...")
    main_window = MainForm()

    # Создаем контроллер
    logger.info("Создание контроллера...")
    controller = Controller(
        model=model,
        main_window=main_window
    )

    # Инициализируем форму через диалог выбора
    logger.info("Инициализация формы через диалог выбора...")
    success = controller.init_form_from_dialog()

    # Если пользователь отменил выбор или произошла ошибка
    if not success:
        logger.info("Инициализация формы не удалась. Приложение завершено.")
        sys.exit(0)

    # Показываем главное окно
    main_window.show()
    logger.info("Главное окно отображено. Запуск главного цикла приложения...")

    # Запускаем главный цикл приложения
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
