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

    # 3. Агрегируем это для записи в БД (код ниже вы не меняете)
    base_class = BaseClass(name=name,
                           comment=comment,
                           type=CLASS_TYPES.SM.value,
                           )
    base_class.constructor_arguments = constructor_args
    return base_class