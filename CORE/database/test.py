from CORE.dataclasses import Point, Parameter, Form
from CORE.database import DBWrapperForDoctor

def test_db_wrapper():
    point1 = Point("q_peak", "нижняя точка пика q")
    point2 = Point("r_peak", "пик r при инфаркте")

    param1 = Parameter("q_height", "высотка пика q")
    param2 = Parameter("q_len", "длина q")

    # Создаем форму с точками и параметрами
    form = Form(
        name="some_test_form",
        comment="Форма с частью данных",
        points=[point1, point2],
        parameters=[param1, param2],
        path_to_pic="/form.jpg",
        path_to_dataset="/dataset.csv"
    )
    db_wrapper_for_doctor = DBWrapperForDoctor()
    # добавим новую форму в базу
    db_wrapper_for_doctor.add_form(form)

    # прочитаем форму из базы
    form_restored = db_wrapper_for_doctor.read_form_by_name("some_test_form")
    print(form_restored)

    # удалим ее из базы: должны удалиться и все ее точки и параметры из соотв.таблиц!
    db_wrapper_for_doctor.delete_form("some_test_form")

    #попробуем ее прочитать - должно теперь вернуть None
    form_restored = db_wrapper_for_doctor.read_form_by_name("some_test_form")
    print(form_restored)



test_db_wrapper()