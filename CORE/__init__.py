from .logger import setup_logging, get_logger
from .signal_1d import Signal

# Версия
__version__ = "1.0.0"

__all__ = [
    'setup_logging',
    'get_logger',
    '__version__',
    'Signal'
]
