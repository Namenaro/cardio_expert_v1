from enum import Enum


class ErrorCode(Enum):
    RUN_PAZZLE_OUT_OF_SIGNAL = "RUN_PAZZLE_OUT_OF_SIGNAL"


class CoreError(Exception):
    def __init__(self, code: str, message: str, **kwargs):
        self.code = code  # уникальный код
        self.message = message  # читаемое сообщение
        self.details = kwargs  # доп. данные
        super().__init__(message)


class RunError(CoreError):
    pass
