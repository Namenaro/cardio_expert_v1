import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QTableWidget,
    QTableWidgetItem, QLabel, QPushButton, QHeaderView, QAbstractItemView
)
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtCore import Qt


OPERATIONS_DATA = {
    "Derivative1_central": {
        "display_name": "Derivative1_central",
        "class_name": "Derivative1_central",
        "description": "Вычисляет первую производную методом центральной разности.",
        "params": [
            {"name": "dx", "type": "float", "comment": "шаг по оси x", "value": 1.0}
        ]
    },
    "Derivative1_splines": {
        "display_name": "Derivative1_splines",
        "class_name": "Derivative1_splines",
        "description": "Вычисляет производную с использованием сплайнов.",
        "params": [
            {"name": "order", "type": "int", "comment": "порядок сплайна", "value": 3}
        ]
    },
    "GaussianSmooth": {
        "display_name": "GaussianSmooth",
        "class_name": "GaussianSmooth",
        "description": "Сглаживает сигнал гауссовым ядром.",
        "params": [
            {"name": "sigma", "type": "float", "comment": "стандартное отклонение", "value": 4.0},
            {"name": "win_len", "type": "float", "comment": "окно (по оси времени)", "value": 12.5}
        ]
    },
    "GlobalMax": {
        "display_name": "GlobalMax",
        "class_name": "GlobalMax",
        "description": "Находит глобальный максимум сигнала.",
        "params": []
    },
    "GlobalMin": {
        "display_name": "GlobalMin",
        "class_name": "GlobalMin",
        "description": "Находит глобальный минимум сигнала.",
        "params": []
    },
    "SmoothPreserveBorders": {
        "display_name": "SmoothPreserveBorders",
        "class_name": "SmoothPreserveBorders",
        "description": "Сглаживает сигнал, сохраняя значения на границах.",
        "params": [
            {"name": "sigma", "type": "float", "comment": "стандартное отклонение", "value": 5.0}
        ]
    },
    "SmoothSavitzkyGolay": {
        "display_name": "SmoothSavitzkyGolay",
        "class_name": "SmoothSavitzkyGolay",
        "description": "Сглаживает сигнал с помощью фильтра Савицкого-Голея.",
        "params": [
            {"name": "window_length", "type": "int", "comment": "длина окна (нечетное)", "value": 11},
            {"name": "polyorder", "type": "int", "comment": "порядок полинома", "value": 2}
        ]
    }
}


class SignalEditorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.item_to_key_map = {}
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Добавление объекта типа "изменение сигнала"')
        self.setGeometry(200, 200, 900, 450)

        main_layout = QHBoxLayout(self)

        #левое окно
        self.operations_list = QListWidget()
        self.operations_list.setFont(QFont('Arial', 11))
        for key, data in OPERATIONS_DATA.items():
            display_name = data["display_name"]
            self.operations_list.addItem(display_name)
            self.item_to_key_map[display_name] = key


        #правое окно
        right_panel_layout = QVBoxLayout()
        
        title_label = QLabel('Добавление объекта типа "изменение сигнала"')
        title_label.setFont(QFont('Arial', 12))
        
        self.class_name_label = QLabel("имя класса: ")
        self.description_label = QLabel(" ")
        self.description_label.setWordWrap(True)
        
        self.params_table = QTableWidget()
        self.params_table.setColumnCount(4)
        self.params_table.setHorizontalHeaderLabels(["имя аргумента", "тип", "коммент", "ваше значение"])
        self.params_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.params_table.setSelectionMode(QAbstractItemView.NoSelection)

        self.save_button = QPushButton("Сохранить")
        
        footer_label = QLabel(
            "Шаги этого типа принимают на вход 1d сигнал ЭКГ и на выходе возвращают сигнал такой-же длины, но "
            "модифицированный одним из способов библиотеки"
        )
        footer_label.setWordWrap(True)

        right_panel_layout.addWidget(title_label, alignment=Qt.AlignCenter)
        right_panel_layout.addWidget(self.class_name_label)
        right_panel_layout.addWidget(self.description_label)
        right_panel_layout.addWidget(self.params_table)
        right_panel_layout.addWidget(self.save_button, alignment=Qt.AlignRight)
        right_panel_layout.addWidget(footer_label)

        main_layout.addWidget(self.operations_list, 1)
        right_widget = QWidget()
        right_widget.setLayout(right_panel_layout)
        main_layout.addWidget(right_widget, 2)

        self.operations_list.currentItemChanged.connect(self.update_details_panel)
        self.save_button.clicked.connect(self.save_data)

        self.operations_list.setCurrentRow(3)

    def update_details_panel(self, current_item):
        if not current_item:
            return

        selected_text = current_item.text()
        operation_key = self.item_to_key_map[selected_text]
        
        data = OPERATIONS_DATA[operation_key]

        self.class_name_label.setText(f"имя класса:    {data['class_name']}")
        self.description_label.setText(data['description'])
        
        self.params_table.setRowCount(0) 
        self.params_table.setRowCount(len(data['params']))
        
        for row, param in enumerate(data['params']):
            name_item = QTableWidgetItem(param["name"])
            type_item = QTableWidgetItem(param["type"])
            comment_item = QTableWidgetItem(param["comment"])
            value_item = QTableWidgetItem(str(param["value"]))

            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            type_item.setFlags(type_item.flags() & ~Qt.ItemIsEditable)
            comment_item.setFlags(comment_item.flags() & ~Qt.ItemIsEditable)
            
            value_item.setBackground(QColor('#FDFDDC'))

            self.params_table.setItem(row, 0, name_item)
            self.params_table.setItem(row, 1, type_item)
            self.params_table.setItem(row, 2, comment_item)
            self.params_table.setItem(row, 3, value_item)
        
        if len(data['params']) == 0:
            self.params_table.setRowCount(1)
            no_params_item = QTableWidgetItem("Для этой операции нет редактируемых параметров")
            no_params_item.setTextAlignment(Qt.AlignCenter)
            no_params_item.setFlags(no_params_item.flags() & ~Qt.ItemIsEditable)
            no_params_item.setBackground(QColor('#F0F0F0'))
            self.params_table.setSpan(0, 0, 1, 4) 
            self.params_table.setItem(0, 0, no_params_item)


    def save_data(self):
        current_item = self.operations_list.currentItem()
        if not current_item:
            print("Операция не выбрана.")
            return

        operation_key = self.item_to_key_map[current_item.text()]
        
        print(f"--- Сохранение данных для '{operation_key}' ---")
        
        for row in range(self.params_table.rowCount()):
            if self.params_table.item(row, 0) is None:
                continue

            param_name = self.params_table.item(row, 0).text()
            new_value_str = self.params_table.item(row, 3).text()
            
            try:
                param_type = OPERATIONS_DATA[operation_key]['params'][row]['type']
                if param_type == 'float':
                    new_value = float(new_value_str)
                elif param_type == 'int':
                    new_value = int(new_value_str)
                else:
                    new_value = new_value_str
                    
                OPERATIONS_DATA[operation_key]['params'][row]['value'] = new_value
                print(f"Параметр '{param_name}' обновлен на значение: {new_value}")
            except (ValueError, IndexError):
                print(f"Ошибка: неверный формат значения '{new_value_str}' для параметра '{param_name}'")

        print("Обновленная модель:", OPERATIONS_DATA[operation_key])
        print("-" * 20)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet("""
        QListWidget::item:selected {
            background-color: #0078D7;
            color: white;
        }
        QWidget {
            font-size: 13px;
        }
    """)
    ex = SignalEditorApp()
    ex.show()
    sys.exit(app.exec_())
