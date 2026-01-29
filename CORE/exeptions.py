import logging
from enum import Enum
from typing import List, Optional

logger = logging.getLogger(__name__)


class ErrorCode(Enum):
    # ошибки парсинга при создании запускаемого объекта пазла (возможна неконстистентность БД)
    PAZZLE_CLASS_CREATION_FAILED = "PAZZLE_CLASS_CREATION_FAILED"
    PAZZLE_POINTS_MAPPING_FAILED = "PAZZLE_POINTS_MAPPING_FAILED"
    PAZZLE_PARAMS_MAPPING_FAILED = "PAZZLE_PARAMS_MAPPING_FAILED"

    # ошибки сопоставления ожидаемых пазлом
    # точек/параметров и фактически полученными
    MISSING_INPUT_POINTS = "MISSING_INPUT_POINTS"
    MISSING_INPUT_PARAMS = "MISSING_INPUT_PARAMS"

    # Проблемы при запуске уже созданного пазла на конкретном сигнале
    PAZZLE_EXECUTION_ERROR = "PAZZLE_EXECUTION_ERROR"
    SM_CHANGED_LEN = "SM_CHANGED_LEN"
    PS_POINT_OUT_OF_INTERVAL = "PS_POINT_OUT_OF_INTERVAL"

    # Проблемы запуска треков
    EMTY_SIGNAL_FOR_TRACK = "EMTY_SIGNAL_FOR_TRACK"
    TRACK_RESULT_POINTS_OUT_OF_INTERVAL = "TRACK_RESULT_POINTS_OUT_OF_INTERVAL"
    STEP_NO_TRACKS = "STEP_NO_TRACKS"
    INVALID_TARGET_POINT_FOR_STEP = "INVALID_TARGET_POINT_FOR_STEP"

    PAZZLE_PROBLEM_IN_TRACK = "PAZZLE_PROBLEM_IN_TRACK"


class CoreError(Exception):
    def __init__(self, message: str):
        self.message = message  # читаемое сообщение
        super().__init__(message)


class PazzleOutOfSignal(CoreError):
    """Исключение, выбрасываемое пазлом при выходе за пределы сигнала.
      выбрасывается только программистом библиотеки пазлов и не является критической ошбикой.
     Это штатно, например, если пытаемся запустить пазл на крайнем кусочке сигнала и он слишком короткий"""

    def __init__(self, message: str = "", class_name: Optional[str] = None):
        super().__init__(message)
        self.class_name = class_name
        self.message = message

        # Автоматическое логирование при создании исключения
        logger.warning(f"PazzleOutOfSignalr в классе: {class_name}")


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

        # Автоматическое логирование при создании исключения
        logger.exception(f"RunPazzleError: {message}\t код ошибки: {self.code}")

    @classmethod
    def selected_point_out_of_interval(cls, left_t: float, right_t: float,
                                       point: float, class_name: str, pazzle_id: int) -> 'RunPazzleError':
        return cls(
            code=ErrorCode.PS_POINT_OUT_OF_INTERVAL.value,
            message=f" SM-пазл {pazzle_id}  вернул как минимум одну точку вне интервала."
                    f"Интервал [{left_t}, {right_t}], точка {point} ",
            class_name=class_name,
            pazzle_id=pazzle_id
        )

    @classmethod
    def sm_changed_len_of_signal(cls, delta_time: float, class_name: str, pazzle_id) -> 'RunPazzleError':
        """При запуске sm новый сигнал не совпал по длине с оригинальным"""
        return cls(
            code=ErrorCode.SM_CHANGED_LEN.value,
            message=f"SM-объект изменил длину сигнала на {delta_time}",
            pazzle_id=pazzle_id,
            class_name=class_name
        )

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


class RunTrackError(CoreError):
    def __init__(self, message: str, track_id: int, code, error: str):
        super().__init__(message)
        self.code = code  # уникальный код ошибки
        self.track_id = track_id
        self.error: str = ""

        # Автоматическое логирование при создании исключения
        logger.exception(f"RunTrackError: {message}\t код ошибки {self.code}")

    @classmethod
    def emty_signal(cls, track_id: int) -> 'RunTrackError':
        """ Сигнал нулевой длины поступил на вход треку при его запуске"""
        return cls(
            message=f"На вход треку {track_id} поступил пустой сигнал - невозможно выбрать точки",
            code=ErrorCode.EMTY_SIGNAL_FOR_TRACK,
            track_id=track_id
        )

    @classmethod
    def selected_points_out_of_interval(cls, track_id: int, left_t: float, right_t: float) -> 'RunTrackError':
        """ Сигнал нулевой длины поступил на вход треку при его запуске"""
        return cls(
            message=f"Итоговые точки трека {track_id} попали вне допустимого для него интервала (интервал [{left_t}, {right_t}])",
            code=ErrorCode.TRACK_RESULT_POINTS_OUT_OF_INTERVAL,
            track_id=track_id
        )

    @classmethod
    def internal_problem_in_pazzle(cls, track_id: int, error: str):
        return cls(track_id=track_id,
                   error=error,
                   code=ErrorCode.PAZZLE_PROBLEM_IN_TRACK,
                   message=f"При выполнении трека {track_id} возникла внутренняя ошибка пазла\t {error}")



class RunStepError(CoreError):
    def __init__(self, message: str, code, num_in_form: int, error=""):
        self.error = error
        self.num_in_form = num_in_form
        self.code = code
        self.message = message

        # Автоматическое логирование при создании исключения
        logger.exception(f"{self.__class__.__name__}: {message}")

    @classmethod
    def empty_tracks_list(cls, num_in_form: int):
        return cls(
            message=f"В шаге (№{num_in_form} в форме) при запуске обнаружен пустой список треков",
            code=ErrorCode.STEP_NO_TRACKS,
            num_in_form=num_in_form
        )

    @classmethod
    def invalid_target_point(cls, num_in_form: int):
        return cls(
            message=f"В шаге (№{num_in_form} в форме) при запуске обнаружено пустое имя целевой точки",
            code=ErrorCode.INVALID_TARGET_POINT_FOR_STEP,
            num_in_form=num_in_form
        )
