import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


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
            logger.warning(f"Папка со стилями не найдена: {self.styles_dir}")
            self.styles_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Создаем папку для стилей: {self.styles_dir}")

    def load_style(self, filename: str) -> str:
        """Загружает стиль из файла"""
        if filename in self._styles_cache:
            return self._styles_cache[filename]

        filepath = self.styles_dir / filename

        if not filepath.exists():
            logger.warning(f" Файл стиля {filepath} не найден")
            return ""

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                self._styles_cache[filename] = content
                return content
        except Exception as e:
            logger.warning(f"Ошибка загрузки стиля {filename}: {e}")
            return ""

    def load_combined_styles(self, *filenames: str) -> str:
        """Загружает и объединяет несколько файлов стилей"""
        combined = []
        for filename in filenames:
            style = self.load_style(filename)
            if style:
                combined.append(style)
            else:
                logger.warning(f"Ошибка загрузки стиля {filename}")

        result = "\n".join(combined)
        return result

    def apply_style(self, widget, *filenames: str) -> None:
        """Применяет стили к виджету"""
        combined_style = self.load_combined_styles(*filenames)
        if combined_style:
            widget.setStyleSheet(combined_style)


# Глобальный экземпляр
_style_loader = None


def get_style_loader() -> StyleLoader:
    """Получить глобальный загрузчик стилей"""
    global _style_loader
    if _style_loader is None:
        _style_loader = StyleLoader()
    return _style_loader
