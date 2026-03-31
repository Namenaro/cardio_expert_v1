from CORE.db.classes_service.classes_repo_write import add_all_classes_to_db
from CORE.db.db_manager import DBManager
from CORE.db.db_report_html import generate_html_report
from CORE.db.forms_services import *
from CORE.db_dataclasses import *


def create_test_db():
    # Завново создаем саму базу
    db_manager = DBManager()
    if db_manager.db_exists():
        db_manager.delete_database()
    db_manager.create_tables()

    # Заполняем таблицы классов
    add_all_classes_to_db(db_manager)

    # Добавляем одну тестовую форму
    get_test_form(db_manager)


    # Распечатаем содержимое базы в файл
    generate_html_report()


def get_test_form(db_manager:DBManager):
    servise = FormService()

    # Осноная информация о форме
    form = Form(name="test_form",
                     comment="комментарий",
                     path_to_pic="\путь к картинке",
                path_to_dataset="qrs.json")

    # Точки формы
    point1 = Point(name='p1', comment='коммент1')
    point2 = Point(name='p2', comment='коммент2')
    point3 = Point(name='p3', comment='коммент2')
    point4 = Point(name='p4', comment='коммент2')
    point5 = Point(name='p5', comment='коммент2')

    # Параметры формы
    param1 = Parameter(name='param1', comment='комментарий к параметру 1')


    # Добавим все связанные с формой объекты в форму
    form.points = [point1, point2, point3, point4, point5]
    form.parameters = [param1]

    with db_manager.get_connection() as conn:
        servise.add_form(conn=conn, form=form)




if __name__ == "__main__":
    create_test_db()