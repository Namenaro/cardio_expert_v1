# utils/style_loader.py
import os
from pathlib import Path
from typing import Optional


class StyleLoader:
    """Класс для загрузки и объединения QSS стилей"""

    _styles_cache = {}

    def __init__(self, styles_dir: Optional[str] = None):
        if styles_dir is None:
            # Путь к папке со стилями относительно этого файла
            self.styles_dir = Path(__file__).parent.parent / "styles"
        else:
            self.styles_dir = Path(styles_dir)

        # Проверяем существование директории
        if not self.styles_dir.exists():
            print(f"Warning: Styles directory not found: {self.styles_dir}")
            self.styles_dir.mkdir(parents=True, exist_ok=True)
            print(f"Created styles directory: {self.styles_dir}")

    def load_style(self, filename: str) -> str:
        """Загружает стиль из файла"""
        if filename in self._styles_cache:
            return self._styles_cache[filename]

        filepath = self.styles_dir / filename
        print(f"Looking for style file: {filepath}")  # Отладка

        if not filepath.exists():
            print(f"Warning: Style file {filepath} not found")
            # Создаем пример файла если его нет
            self._create_example_style(filepath)
            return ""

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                self._styles_cache[filename] = content
                print(f"Loaded style from {filename}: {len(content)} bytes")  # Отладка
                return content
        except Exception as e:
            print(f"Error loading style {filename}: {e}")
            return ""

    def _create_example_style(self, filepath: Path):
        """Создает пример файла стилей если его нет"""
        if filepath.name == "common.qss":
            example_content = """
/* Basic styles - replace with your actual styles */
* {
    font-family: 'Segoe UI', 'Arial', sans-serif;
}

QPushButton {
    background-color: #4a90e2;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px;
}

QPushButton:hover {
    background-color: #357abd;
}
"""
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(example_content)
                print(f"Created example style file: {filepath}")
            except Exception as e:
                print(f"Error creating example style: {e}")

    def load_combined_styles(self, *filenames: str) -> str:
        """Загружает и объединяет несколько файлов стилей"""
        combined = []
        for filename in filenames:
            style = self.load_style(filename)
            if style:
                combined.append(style)
            else:
                print(f"Warning: Could not load style {filename}")

        result = "\n".join(combined)
        print(f"Combined styles length: {len(result)} bytes")  # Отладка
        return result

    def apply_style(self, widget, *filenames: str) -> None:
        """Применяет стили к виджету"""
        combined_style = self.load_combined_styles(*filenames)
        if combined_style:
            widget.setStyleSheet(combined_style)
            print(f"Applied styles to {widget.__class__.__name__}")  # Отладка
        else:
            print(f"No styles applied to {widget.__class__.__name__}")


# Глобальный экземпляр
_style_loader = None


def get_style_loader() -> StyleLoader:
    """Получить глобальный загрузчик стилей"""
    global _style_loader
    if _style_loader is None:
        _style_loader = StyleLoader()
    return _style_loader
