from enum import Enum
from typing import List, Optional


class ErrorCode(Enum):
    RUN_PAZZLE_OUT_OF_SIGNAL = "RUN_PAZZLE_OUT_OF_SIGNAL"

    PAZZLE_CLASS_CREATION_FAILED = "PAZZLE_CLASS_CREATION_FAILED"
    PAZZLE_POINTS_MAPPING_FAILED = "PAZZLE_POINTS_MAPPING_FAILED"
    PAZZLE_PARAMS_MAPPING_FAILED = "PAZZLE_PARAMS_MAPPING_FAILED"

    MISSING_INPUT_POINTS = "MISSING_INPUT_POINTS"
    MISSING_INPUT_PARAMS = "MISSING_INPUT_PARAMS"

    PAZZLE_EXECUTION_ERROR = "PAZZLE_EXECUTION_ERROR"


class CoreError(Exception):
    def __init__(self, message: str):
        self.message = message  # читаемое сообщение
        super().__init__(message)


class PazzleOutOfSignal(CoreError):
    """Исключение, выбрасываемое пазлом при выходе за пределы сигнала"""

    def __init__(self, message: str = "", class_name: Optional[str] = None):
        super().__init__(message)
        self.class_name = class_name
        self.message = message


class RunPazzleError(CoreError):
    """Исключение для ошибок выполнения PC-пазлов"""

    def __init__(self, code: str, message: str, pazzle_id: int,
                 absent_points: Optional[List[str]] = None,
                 absent_params: Optional[List[str]] = None,
                 class_name: Optional[str] = None,
                 error: Optional[str] = None):
        super().__init__(message)
        self.code = code  # уникальный код ошибки
        self.pazzle_id = pazzle_id
        self.absent_points = absent_points or []
        self.absent_params = absent_params or []
        self.class_name = class_name
        self.error = error

    @classmethod
    def class_creation_failed(cls, pazzle_id: int, error: str) -> 'RunPazzleError':
        """Ошибка создания экземпляра класса пазла"""
        return cls(
            code=ErrorCode.PAZZLE_CLASS_CREATION_FAILED.value,
            message=f"Не удалось создать экземпляр класса пазла {pazzle_id}: {error}",
            pazzle_id=pazzle_id,
            error=error
        )

    @classmethod
    def points_mapping_failed(cls, pazzle_id: int, error: str) -> 'RunPazzleError':
        """Ошибка получения соответствия имен точек"""
        return cls(
            code=ErrorCode.PAZZLE_POINTS_MAPPING_FAILED.value,
            message=f"Не удалось получить список имён необходимых PC-пазлу {pazzle_id} входных точек: {error}",
            pazzle_id=pazzle_id,
            error=error
        )

    @classmethod
    def params_mapping_failed(cls, pazzle_id: int, error: str) -> 'RunPazzleError':
        """Ошибка получения соответствия имен параметров"""
        return cls(
            code=ErrorCode.PAZZLE_PARAMS_MAPPING_FAILED.value,
            message=f"Не удалось получить список имён необходимых PC-пазлу {pazzle_id} входных параметров: {error}",
            pazzle_id=pazzle_id,
            error=error
        )

    @classmethod
    def missing_input_points(cls, pazzle_id: int, absent_points: List[str]) -> 'RunPazzleError':
        """Отсутствуют необходимые точки"""
        return cls(
            code=ErrorCode.MISSING_INPUT_POINTS.value,
            message=f"Отсутствуют необходимые точки для пазла {pazzle_id}: {absent_points}",
            pazzle_id=pazzle_id,
            absent_points=absent_points
        )

    @classmethod
    def missing_input_params(cls, pazzle_id: int, absent_params: List[str]) -> 'RunPazzleError':
        """Отсутствуют необходимые параметры"""
        return cls(
            code=ErrorCode.MISSING_INPUT_PARAMS.value,
            message=f"Отсутствуют необходимые параметры для пазла {pazzle_id}: {absent_params}",
            pazzle_id=pazzle_id,
            absent_params=absent_params
        )

    @classmethod
    def execution_error(cls, pazzle_id: int, class_name: str, error: str) -> 'RunPazzleError':
        """Ошибка выполнения пазла"""
        return cls(
            code=ErrorCode.PAZZLE_EXECUTION_ERROR.value,
            message=f"Ошибка выполнения пазла {pazzle_id} (класс {class_name}): {error}",
            pazzle_id=pazzle_id,
            class_name=class_name,
            error=error
        )
