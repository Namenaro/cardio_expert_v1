from CORE.signal_1d import Signal
from CORE.db_dataclasses.classes_to_pazzles_helpers import DATA_TYPES
from CORE.db_dataclasses import *
from copy import deepcopy


class ExampleSMClass:
    """ Этот класс делает такое-то"""

    def __init__(self, some_arg_1: int = 3,
                 some_arg_2: str = "default_str"):  # у всех аргументов ОБЯЗАНЫ быть умолчательные значения
        self.some_arg_1 = some_arg_1
        self.some_arg_2 = some_arg_2

    def run(self, signal: Signal) -> Signal:
        # нельзя менять входной сигнал, поэтому создаем копию входного сигнала
        result_signal = deepcopy(signal)

        # методы типа SM работают только с Signal.signal_mv
        result_signal.signal_mv = [i / self.some_arg_1 for i in
                                   result_signal.signal_mv]  # какая-то логика получения нового сигнала на основе старого

        return result_signal

    @classmethod
    def to_base_class(self):
        # 1.Общая информация о классе (обязательно)
        name = "ExampleSMClass"  # Название класса как оно есть в коде
        comment = "Этот класс делает такое-то"

        # 2. Описание аргументов конструктора
        arg1 = ClassArgument(name="some_arg_1",  # название, как оно есть в коде
                             comment="комментарий к этому аргументу",
                             data_type=DATA_TYPES.INT.value,
                             # в этом списке опций выбрать нужный тип данных, который реально в коде
                             default_value="3"  # умолчательное значение пишем как строку - всегда
                             )
        arg2 = ClassArgument(name="some_arg_2",
                             comment="комментарий к этому аргументу",
                             data_type=DATA_TYPES.STR.value,
                             default_value="default_str"
                             )
        constructor_args = [arg1, arg2]  # либо пустой массив

        # 3. добавляем запись в БД (код ниже вы не меняете)
        base_class = BaseClass(name=name,
                               comment=comment,
                               type=CLASS_TYPES.SM.value,
                               )
        base_class.constructor_arguments = constructor_args
        return base_class
