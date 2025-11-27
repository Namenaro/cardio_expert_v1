Редактор шлёт сигнал save_request (т.е. пользователь нажал в нем сохранить).

Контроллер перехватывает этот сигнал, сохраняет данные в БД.

При успехе контроллер вызывает main_window.show_success() и main_window.refresh.

При ошибке — main_window.show_error().

Форма обновляет интерфейс, не зная, кто её вызвал.

# editor_signals.py
class EditorSignals(QObject):
    # Запросы на открытие редакторов
    request_track_editor = Signal(Track, object)  # (data, parent)
    request_step_editor = Signal(Step, object)
    request_point_editor = Signal(Point, object)
    request_param_editor = Signal(Parameter, object)

    # Запрос на сохранение в БД отправляем контроллеру (мб тоже расписать как группу)
    save_request = Signal(str, object)  # (operation_type, data)


editor_signals = EditorSignals()

# Виджеты инициаторы: посылают форме запросы на открытие конкретных редакторов
from editor_signals import editor_signals
class TrackWidget(QWidget):
    def __init__(self, track: Track, parent=None):
        super().__init__(parent)
        self.track = track

        self._init_ui()

        self.propagate_from_ui(self.track)

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"Трек #{track.id}: {track.name} ({track.length} м)"))

        btn = QPushButton("Редактировать")
        btn.clicked.connect(self._on_edit)
        layout.addWidget(btn)

    def _on_edit(self):
        editor_signals.request_track_editor.emit(self.track, self)

    def propagate_from_ui(self, Track):
        будет дергаться при обновлении формы: заполнение новыми данными полей



# редакторы все от базового класса
class BaseEditor(QDialog):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.setModal(True)
        self.data = data
        self._dirty = False  # Флаг: есть ли несохранённые изменения

        # Основной макет
        layout = QVBoxLayout(self)

        # Здесь должны быть поля ввода (реализация в наследниках)
        self._setup_ui(layout)

        # Кнопки
        button_layout = QHBoxLayout()

        self.save_btn = QPushButton("Сохранить")
        self.save_btn.clicked.connect(self._on_save_clicked)
        button_layout.addWidget(self.save_btn)

        self.cancel_btn = QPushButton("Отмена")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)

        layout.addLayout(button_layout)
        self.refresh(data)

    def _setup_ui(self, layout):
        """
        Абстрактный метод: должен быть реализован в наследниках.
        Добавляет поля ввода в макет.
        """
        raise NotImplementedError("Необходимо реализовать _setup_ui в наследнике")

    def get_data(self):
        """
        Абстрактный метод: должен возвращать актуальные данные.
        Реализуется в наследниках.
        """
        raise NotImplementedError("Необходимо реализовать get_data в наследнике")

    def _mark_dirty(self):
        """Помечает, что есть несохранённые изменения"""
        self._dirty = True

    def _has_unsaved_changes(self) -> bool:
        """Проверяет, есть ли несохранённые изменения"""
        if not self._dirty:
            return False

        current = self.get_data()
        return current != self.data  # Предполагаем, что модели реализуют __ne__

    def _on_save_clicked(self):
        реализовать посылку сигнала к контроллеру с запросом на изменение в данных
        raise NotImplementedError


    def refresh(self, data):
        self._mark_dirty = False
        self._propagate_ui_from_data( data)

    def _propagate_ui_from_data(self, data):
        ... парсим data
        раскидываем по контролам
        raise NotImplementedError("Необходимо реализовать _propagate_ui_from_data в наследнике")

    def closeEvent(self, event):
        """
        Обрабатывает попытку закрытия окна.
        Показывает диалог, если есть несохранённые изменения.
        """
        if self._has_unsaved_changes():
            reply = QMessageBox.question(
                self,
                "Несохранённые изменения",
                "Вы хотите сохранить изменения перед выходом?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )

            if reply == QMessageBox.Save:
                self._on_save_clicked()
                event.ignore()  # Не закрываем, ждём ответа от контроллера
                return
            elif reply == QMessageBox.Cancel:
                event.ignore()  # Отменяем закрытие
                return

        # Если нет изменений или выбран «Не сохранять», закрываем
        super().closeEvent(event)



# тут просто наследуем
class TrackEditor(BaseEditor):
    def _setup_ui(self, layout):

        self.length_input = QDoubleSpinBox()
        self.length_input.setValue(self.data.length)
        self.length_input.valueChanged.connect(self._mark_dirty)



    def get_data(self) -> Track:
        return Track(
            id=self.data.id,
            name=self.name_input.text(),
            length=self.length_input.value(),
            description=self.desc_input.text() or None
        )

    def _propagate_ui_from_data(self, Track):
        заполняем поля данными


    def _on_save_clicked(self):
        ### редактор просто шлет сигнал контроллеру
        # (тут мб один из группы возможных сигналов вместо одоно универсального save_request
        updated_data = self.get_data()
        save_request.emit("save_Step", updated_data, self.editor_id)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()


        # Подключение сигналов на открытие редакторов
        editor_signals.request_track_editor.connect(self._open_track_editor)
        editor_signals.request_step_editor.connect(self._open_step_editor)
        editor_signals.request_point_editor.connect(self._open_point_editor)
        editor_signals.request_param_editor.connect(self._open_param_editor)

        self._setup_ui()

        # надо реализовать список открытых редакторов. ЧТобы
        # в методе рефреш рефреш делать их обход (обесчпечить доабвление, удаление)

    def _setup_ui(self):
        # ... создание виджетов инициаторов
        self.form_list_widget = FormListWidget()
        self.form_detail_widget = FormDetailWidget()

    # --- Методы открытия редакторов ---
    def _open_track_editor(self, track: Track, parent: QWidget):
        dialog = TrackEditor(track, parent=parent)

        dialog.show()

    def _open_step_editor(self, step: Step, parent: QWidget):
        dialog = StepEditor(step, parent=parent)
        dialog.show()


    def _open_point_editor(self, point: Point, parent: QWidget):
        dialog = PointEditor(point, parent=parent)
        dialog.show()

    # Публичные методы для контроллера
    def show_success(self, message: str):
        QMessageBox.information(self, "Успех", message)

    def show_error(self, message: str):
        QMessageBox.critical(self, "Ошибка", message)

    def refresh(self, form):
       самый сложный метод: для инициируюших все легко,
       а вот открытым редакторам надо из этой формы вынуть нужный подобъект по его id
        для этого к датаклассу формы надо написать кучу геттеров!
       делаем обход всех открытых редакторов, берем ид ассоциированных
       с ними объектов, запрашиваем из формы по этому ид нужный подоъект и вызываем
        у того редактора _propagate_ui_from_data. Если такого ид не найдено, закрываем этот редактор
       и его потомков


class Model:
    def __init__(self, db_path:str=DB_PATH):
       pass

    def add_object(self, obj):
        вернуть Труе. либо если выпадет исключение то не ловить его. его будет ловить контроллер

    def update_object(self, obj):
        pass

    def delete_object(self, obj):
        pass

    def get_form_by_id(self, obj):
        pass



# контроллер имеет к главному окну доступ по ссылке.
# Он дергает ее метод "обновить все". А так же управляет
# показом сообщений об успехах и ошибках. Он не отправляет сигналов,
# а только получает и только от редакторов. Получив сигнал от редактора он его парсит
# чтобы выхвать соотв запрос к сервисам базы. Он же и получает резуоттат транзакций
class DBController:
    def __init__(self, inital_form, model: Model, main_window: MainWindow):
        self.model = model
        self.main_window = main_window
        self.main_window.refresh(inital_form)


        save_request.connect(self._on_save_request) # получет это самый сигнал из редактора

    def _on_save_request(self, op_type: str, data: object, editor_id: str):
        # парсим что там за запрос...
        try:
            if op_type == "save_Step":
                # выполняем запрос в базу
                self.model.update_step(step)
                # Успех: перезагружаем содерждимое основного окна
                self._update_ui(editor_id_to_close=editor_id)
            elif op_type =="delete_step":
                ...

        except Exception as e:
            self.main_window.show_error(f"Ошибка сохранения: {str(e)}")

    def _update_ui(self, editor_id_to_close):
        """Перезагружает все данные из БД и передаёт форме"""
        try:
            form = self.model.get_form_by_id()
            self.main_window.refresh(form)
            self.main_window.show_success("Форма сохранена")

        except Exception as e:
            self.main_window.show_error(f"Ошибка обновления: {str(e)}")








