from CORE.database.db_manager import DBManager
from CORE.database.forms_servise import FormsService
from CORE.database.repositories.classes_repo_write import add_all_classes_to_db
from CORE.database.repositories import *
from CORE.database.test_utils.db_report_html import generate_html_report
from CORE.db_dataclasses import *

from typing import Optional


def create_test_db():
    # Завново создаем саму базу
    db_manager = DBManager()
    if db_manager.db_exists():
        db_manager.delete_database()
    db_manager.create_tables()

    # Заполняем таблицы классов
    add_all_classes_to_db(db_manager)

    # Добавляем одну тестовую форму
    form = get_test_form(db_manager)


    # Распечатаем содержимое базы в файл
    generate_html_report(output_file='database_report.html')


def get_test_form(db_manager:DBManager)->Optional[Form]:
    servise = FormsService(db_manager)

    # Осноная информация о форме
    form = Form(name="test_form",
                     comment="комментарий",
                     path_to_pic="\путь к картинке",
                     path_to_dataset="\путь к датасету")

    # Точки формы
    point1 = Point(name='p1', comment='коммент1')
    point2 = Point(name='p2', comment='коммент2')

    # Параметры формы
    param1 = Parameter(name='param1', comment='комментарий к параметру 1')
    param2 = Parameter(name='param2', comment='комментарий к параметру 2 это длинный... очень длинный... комментарий о параметре номер два этой формы')


    # Наложим жесткое условие на параметр 1
    hc1 = BasePazzle(name="hard_condion1", comment="это жесткое условие на параметр 1: он должен быть меньше порога")
    classes_repo_read = ClassesRepoRead(db_manager)
    class_id = classes_repo_read.get_class_id_by_name(class_name="LessThanThreshold")
    base_class = classes_repo_read.get_class_by_id(class_id=class_id)
    hc1.class_ref = base_class
    hc1.argument_values = [ObjectArgumentValue(argument_id=base_class.constructor_arguments[0].id, argument_value="5")]



    # Добавим все связанные с формой объекты в форму
    form.points = [point1, point2]
    form.parameters = [param1, param2]
    form.HC_PC_objects.append(hc1)


    form_id = servise.add_form(form=form)



if __name__ == "__main__":
    create_test_db()