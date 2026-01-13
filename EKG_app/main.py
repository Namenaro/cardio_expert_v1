import sys
from PySide6.QtWidgets import QApplication

from ui.main_window import MainWindow
from data_adapter import LUDBAdapter

if __name__ == "__main__":
    adapter = LUDBAdapter()
    entries = adapter.get_all_entries()

    if not entries:
        print("Не удалось загрузить записи. Проверьте пути в dataset_utils/paths.py")
        sys.exit(1)

    app = QApplication(sys.argv)
    window = MainWindow(adapter=adapter, entries=entries)
    window.show()
    sys.exit(app.exec())