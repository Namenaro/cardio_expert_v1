from .signal_1d import Signal

from .logger import setup_logging, get_logger

# Версия
__version__ = "1.0.0"

__all__ = [
    'setup_logging',
    'get_logger',
    '__version__',
    'Signal'
]
