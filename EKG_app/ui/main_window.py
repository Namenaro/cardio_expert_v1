import json
import os
from dataclasses import asdict
from typing import List, Dict

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QGroupBox, QRadioButton, QScrollBar, QFileDialog, QMessageBox, 
    QListWidget
)
from PySide6.QtCore import Qt

from matplotlib.patches import Rectangle

from data_adapter import LUDBAdapter
from models import Entry
from .mpl_canvas import MplCanvas
from core.signal_1d import Signal
from core.drawer import Drawer

class MainWindow(QMainWindow):
    def __init__(self, adapter: LUDBAdapter, entries: List[Entry]):
        super().__init__()
        self.setWindowTitle("Инструмент разметки ЭКГ")
        self.setGeometry(100, 100, 1500, 950)

        self.adapter = adapter
        self.entries = entries
        self.current_index = 0
        self.current_signal: Signal = None
        self.output_json_path: str = None
        
        self.default_window_sec = 2.0
        self.is_custom_zoom = False

        self.saved_annotations: List[Dict] = [] 

        self.zoom_start_x = None
        self.zoom_start_y = None
        self.zoom_rect_patch = None

        self.pan_start_x_px = None 
        self.pan_start_y_px = None
        self.pan_orig_xlim = None
        self.pan_orig_ylim = None

        self.dragging_point_name = None
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        left_panel = QVBoxLayout()
        self.setup_tools_panel(left_panel)
        main_layout.addLayout(left_panel, stretch=1)

        right_panel = QVBoxLayout()
        self.setup_plot_panel(right_panel)
        main_layout.addLayout(right_panel, stretch=5) 
        
        self.load_ecg_by_index(0)

    def setup_tools_panel(self, layout: QVBoxLayout):
        """Панель инструментов."""
        font_style = "font-size: 14px;"
        
        # 1. выбор файла
        save_box = QGroupBox("Файл разметки")
        save_box.setStyleSheet(f"QGroupBox {{ font-weight: bold; {font_style} }}")
        save_layout = QVBoxLayout()
        self.select_file_btn = QPushButton("Выбрать файл...")
        self.select_file_btn.setStyleSheet(f"padding: 8px; {font_style}")
        self.file_label = QLabel("Файл не выбран")
        self.file_label.setWordWrap(True)
        self.file_label.setStyleSheet("font-size: 12px; color: #555;")
        save_layout.addWidget(self.select_file_btn)
        save_layout.addWidget(self.file_label)
        save_box.setLayout(save_layout)
        self.select_file_btn.clicked.connect(self.select_output_file)

        # 2. выбор точки
        point_box = QGroupBox("Тип точки")
        point_box.setStyleSheet(f"QGroupBox {{ font-weight: bold; {font_style} }}")
        point_layout = QHBoxLayout()
        radio_style = f"QRadioButton {{ {font_style} }}"
        self.radio_p1 = QRadioButton("p1"); self.radio_p1.setStyleSheet(radio_style)
        self.radio_p2 = QRadioButton("p2"); self.radio_p2.setStyleSheet(radio_style)
        self.radio_p3 = QRadioButton("p3"); self.radio_p3.setStyleSheet(radio_style)
        self.radio_p1.setChecked(True)
        point_layout.addWidget(self.radio_p1); point_layout.addWidget(self.radio_p2); point_layout.addWidget(self.radio_p3)
        point_box.setLayout(point_layout)

        # 3. текущая группа
        info_box = QGroupBox("Текущая (новая) группа")
        info_box.setStyleSheet(f"QGroupBox {{ font-weight: bold; {font_style} }}")
        info_layout = QVBoxLayout()
        lbl_style = f"QLabel {{ {font_style} }}"
        self.lbl_p1 = QLabel("p1: -"); self.lbl_p1.setStyleSheet(lbl_style)
        self.lbl_p2 = QLabel("p2: -"); self.lbl_p2.setStyleSheet(lbl_style)
        self.lbl_p3 = QLabel("p3: -"); self.lbl_p3.setStyleSheet(lbl_style)
        self.btn_clear_points = QPushButton("Сбросить новые точки")
        self.btn_clear_points.setStyleSheet(f"background-color: #FFE4E1; color: #8B0000; padding: 5px; {font_style}")
        self.btn_clear_points.clicked.connect(self.reset_current_points)
        info_layout.addWidget(self.lbl_p1); info_layout.addWidget(self.lbl_p2); info_layout.addWidget(self.lbl_p3)
        info_layout.addSpacing(5)
        info_layout.addWidget(self.btn_clear_points)
        info_box.setLayout(info_layout)
        self.btn_save = QPushButton("СОХРАНИТЬ в файл")
        self.btn_save.setStyleSheet(f"QPushButton {{ background-color: #2E8B57; color: white; font-weight: bold; padding: 10px; {font_style} }} QPushButton:hover {{ background-color: #3CB371; }}")
        self.btn_save.clicked.connect(self.save_current_annotation)
        info_layout.addWidget(self.btn_save)

        # 4. список сохраненных
        saved_box = QGroupBox("Сохраненные группы")
        saved_box.setStyleSheet(f"QGroupBox {{ font-weight: bold; {font_style} }}")
        saved_layout = QVBoxLayout()
        self.saved_list_widget = QListWidget()
        self.saved_list_widget.setStyleSheet("font-size: 12px;")
        self.saved_list_widget.itemClicked.connect(self.on_saved_item_clicked)
        self.btn_delete_saved = QPushButton("Удалить выбранную")
        self.btn_delete_saved.setStyleSheet(f"background-color: #CD5C5C; color: white; font-weight: bold; padding: 5px; {font_style}")
        self.btn_delete_saved.clicked.connect(self.delete_saved_annotation)
        saved_layout.addWidget(self.saved_list_widget)
        saved_layout.addWidget(self.btn_delete_saved)
        saved_box.setLayout(saved_layout)

        self.btn_reset_zoom = QPushButton("Сбросить зум")
        self.btn_reset_zoom.setStyleSheet(f"padding: 8px; {font_style}")
        self.btn_reset_zoom.clicked.connect(self.reset_zoom)

        layout.addWidget(save_box)
        layout.addWidget(point_box)
        layout.addWidget(info_box)
        layout.addWidget(saved_box)
        layout.addWidget(self.btn_reset_zoom)
        layout.addStretch()

    def setup_plot_panel(self, layout: QVBoxLayout):
        self.canvas = MplCanvas(self, width=15, height=8, dpi=100)
        self.drawer = Drawer(self.canvas.axes)
        self.canvas.figure.subplots_adjust(left=0.03, right=0.99, top=0.97, bottom=0.08)
        self.canvas.mpl_connect('button_press_event', self.on_press)
        self.canvas.mpl_connect('motion_notify_event', self.on_drag)
        self.canvas.mpl_connect('button_release_event', self.on_release)

        self.scrollbar = QScrollBar(Qt.Horizontal)
        self.scrollbar.setMinimumHeight(25)
        self.scrollbar.valueChanged.connect(self.on_scrollbar_change)

        nav_layout = QHBoxLayout()
        nav_style = "font-size: 14px; padding: 5px;"
        self.lbl_status = QLabel("Запись -/-")
        self.lbl_status.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.btn_prev = QPushButton("< Пред."); self.btn_prev.setStyleSheet(nav_style)
        self.btn_next = QPushButton("Следующ. >"); self.btn_next.setStyleSheet(nav_style)
        nav_layout.addWidget(self.lbl_status); nav_layout.addStretch()
        nav_layout.addWidget(self.btn_prev); nav_layout.addWidget(self.btn_next)
        self.btn_prev.clicked.connect(self.prev_ecg)
        self.btn_next.clicked.connect(self.next_ecg)

        layout.addWidget(self.canvas)
        layout.addWidget(self.scrollbar)
        layout.addLayout(nav_layout)

    # --- ДАННЫЕ ---

    def load_ecg_by_index(self, index):
        if not (0 <= index < len(self.entries)): return
        self.current_index = index
        self.current_entry = self.entries[self.current_index]
        self.current_signal = self.adapter.get_signal_for_entry(self.current_entry)
        self.current_entry.points.clear()
        
        total_samples = len(self.current_signal.signal_mv)
        visible_samples = int(self.default_window_sec * self.current_signal.frequency)
        self.scrollbar.setMaximum(max(0, total_samples - visible_samples))
        self.scrollbar.setValue(0)
        self.is_custom_zoom = False
        
        self.reload_saved_annotations()
        self.lbl_status.setText(f"Запись {index + 1}/{len(self.entries)}: {self.current_entry.patient_id} ({self.current_entry.lead_name})")
        self.update_labels()
        self.draw_plot()

    def prev_ecg(self): self.load_ecg_by_index(self.current_index - 1)
    def next_ecg(self): self.load_ecg_by_index(self.current_index + 1)

    def select_output_file(self):
        path, _ = QFileDialog.getSaveFileName(self, "Файл разметки", "", "JSON (*.json)")
        if path:
            self.output_json_path = path
            self.file_label.setText(os.path.basename(path))
            self.reload_saved_annotations()
            self.draw_plot()

    def reload_saved_annotations(self):
        self.saved_annotations = []
        self.saved_list_widget.clear()
        if not self.output_json_path or not os.path.exists(self.output_json_path): return
        try:
            with open(self.output_json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if not isinstance(data, list): data = []
                curr_pid = self.current_entry.patient_id
                curr_lead = self.current_entry.lead_name
                group_counter = 1
                for item in data:
                    if item.get('patient_id') == curr_pid and item.get('lead_name') == curr_lead:
                        pts = item.get('points', {})
                        self.saved_annotations.append(pts)
                        p1_val = pts.get('p1', 0)
                        item_text = f"Группа {group_counter} (p1 ≈ {p1_val:.2f}с)"
                        self.saved_list_widget.addItem(item_text)
                        group_counter += 1
        except: pass

    def delete_saved_annotation(self):
        row = self.saved_list_widget.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите группу из списка для удаления.")
            return
        if not self.output_json_path: return
        points_to_remove = self.saved_annotations[row]
        try:
            with open(self.output_json_path, 'r', encoding='utf-8') as f: all_data = json.load(f)
            curr_pid = self.current_entry.patient_id
            curr_lead = self.current_entry.lead_name
            new_data = []
            deleted = False
            for item in all_data:
                if (not deleted and item.get('patient_id') == curr_pid and item.get('lead_name') == curr_lead and item.get('points') == points_to_remove):
                    deleted = True
                    continue 
                new_data.append(item)
            with open(self.output_json_path, 'w', encoding='utf-8') as f: json.dump(new_data, f, indent=2, ensure_ascii=False)
            self.reload_saved_annotations()
            self.draw_plot(preserve_limits=True)
        except Exception as e: QMessageBox.critical(self, "Ошибка удаления", str(e))

    def on_saved_item_clicked(self, item):
        row = self.saved_list_widget.currentRow()
        if row < 0 or row >= len(self.saved_annotations): return
        pts = self.saved_annotations[row]
        times = [v for v in pts.values()]
        if not times: return
        avg_time = sum(times) / len(times)
        fs = self.current_signal.frequency
        target_sample = int((avg_time - (self.default_window_sec / 2)) * fs)
        self.is_custom_zoom = False 
        self.scrollbar.setValue(max(0, target_sample))
        self.scrollbar.setEnabled(True)

    def reset_current_points(self):
        self.current_entry.points.clear()
        self.update_labels()
        self.draw_plot(preserve_limits=True)

    # --- МЫШЬ (ЗУМ, ПАНОРАМИРОВАНИЕ И ПЕРЕТАСКИВАНИЕ ТОЧЕК) ---

    def get_point_under_cursor(self, xdata):
        """Проверяет, находится ли курсор рядом с красной линией."""
        if xdata is None: return None
        
        xlim = self.canvas.axes.get_xlim()
        tolerance = (xlim[1] - xlim[0]) * 0.015 
        
        closest_point = None
        min_dist = float('inf')

        for p_name, p_time in self.current_entry.points.items():
            dist = abs(p_time - xdata)
            if dist < tolerance and dist < min_dist:
                min_dist = dist
                closest_point = p_name
        
        return closest_point

    def on_press(self, event):
        if not event.inaxes: return
        
        if event.button == 1: # ЛКМ
            # проверяем, не кликнули ли мы по точке для перетаскивания
            point_under_cursor = self.get_point_under_cursor(event.xdata)
            
            if point_under_cursor:
                # Если кликнули на точку - начинаем тащить
                self.dragging_point_name = point_under_cursor
                if point_under_cursor == 'p1': self.radio_p1.setChecked(True)
                elif point_under_cursor == 'p2': self.radio_p2.setChecked(True)
                elif point_under_cursor == 'p3': self.radio_p3.setChecked(True)
            else:
                # Если не на точку - готовимся к панорамированию
                self.pan_start_x_px = event.x
                self.pan_start_y_px = event.y
                self.pan_orig_xlim = self.canvas.axes.get_xlim()
                self.pan_orig_ylim = self.canvas.axes.get_ylim()

        elif event.button == 3: # ПКМ (Зум)
            self.zoom_start_x = event.xdata; self.zoom_start_y = event.ydata
            self.zoom_rect_patch = Rectangle((self.zoom_start_x, self.zoom_start_y), 0, 0, fill=True, color='yellow', alpha=0.3, ec='black')
            self.canvas.axes.add_patch(self.zoom_rect_patch); self.canvas.draw()

    def on_drag(self, event):
        if not event.inaxes: return

        if event.button == 1: # ЛКМ
            if self.dragging_point_name:
                # 1. ПЕРЕТАСКИВАНИЕ ТОЧКИ
                self.current_entry.points[self.dragging_point_name] = event.xdata
                self.update_labels()
                self.draw_plot(preserve_limits=True) 
                
            elif self.is_custom_zoom and self.pan_start_x_px is not None:
                # 2. ПАНОРАМИРОВАНИЕ (если не тащим точку)
                dx_px = event.x - self.pan_start_x_px
                dy_px = event.y - self.pan_start_y_px
                bbox = self.canvas.axes.get_window_extent()
                width_data = self.pan_orig_xlim[1] - self.pan_orig_xlim[0]
                height_data = self.pan_orig_ylim[1] - self.pan_orig_ylim[0]
                dx_data = (dx_px / bbox.width) * width_data
                dy_data = (dy_px / bbox.height) * height_data
                self.canvas.axes.set_xlim([self.pan_orig_xlim[0] - dx_data, self.pan_orig_xlim[1] - dx_data])
                self.canvas.axes.set_ylim([self.pan_orig_ylim[0] - dy_data, self.pan_orig_ylim[1] - dy_data])
                self.canvas.draw()

        elif event.button == 3 and self.zoom_rect_patch:
            # 3. РИСОВАНИЕ ЗУМА
            self.zoom_rect_patch.set_width(event.xdata - self.zoom_start_x)
            self.zoom_rect_patch.set_height(event.ydata - self.zoom_start_y)
            self.canvas.draw()

    def on_release(self, event):
        if event.button == 1:
            if self.dragging_point_name:
                # Закончили тащить точку
                self.dragging_point_name = None
            
            elif self.pan_start_x_px is not None:
                # Закончили панорамирование или клик
                total_drag_px = ((event.x - self.pan_start_x_px)**2 + (event.y - self.pan_start_y_px)**2)**0.5
                if total_drag_px < 3 and event.inaxes: 
                    # Это был обычный клик - ставим точку
                    self.place_point(event.xdata)
                self.pan_start_x_px = None

        elif event.button == 3 and self.zoom_rect_patch:
            self.zoom_rect_patch.remove(); self.zoom_rect_patch = None
            if event.inaxes and abs(event.xdata - self.zoom_start_x) > 0.01:
                x_min, x_max = sorted([self.zoom_start_x, event.xdata]); y_min, y_max = sorted([self.zoom_start_y, event.ydata])
                self.canvas.axes.set_xlim(x_min, x_max); self.canvas.axes.set_ylim(y_min, y_max)
                self.is_custom_zoom = True; self.scrollbar.setEnabled(False)
            self.canvas.draw()

    def place_point(self, x_time):
        if self.radio_p1.isChecked(): p_type = 'p1'
        elif self.radio_p2.isChecked(): p_type = 'p2'
        else: p_type = 'p3'
        self.current_entry.points[p_type] = x_time
        self.update_labels(); self.draw_plot(preserve_limits=True)

    def reset_zoom(self):
        self.is_custom_zoom = False; self.scrollbar.setEnabled(True); self.draw_plot()

    def on_scrollbar_change(self):
        if not self.is_custom_zoom: self.draw_plot()

    # --- СОХРАНЕНИЕ ---
    def save_current_annotation(self):
        if not self.output_json_path:
            QMessageBox.warning(self, "Ошибка", "Выберите файл!")
            return
        pts = self.current_entry.points
        if not all(k in pts for k in ('p1', 'p2', 'p3')):
            QMessageBox.warning(self, "Ошибка", "Отметьте 3 точки!")
            return

        new_record = {"patient_id": self.current_entry.patient_id, "lead_name": self.current_entry.lead_name, "points": pts.copy()}
        all_data = []
        if os.path.exists(self.output_json_path):
            try:
                with open(self.output_json_path, 'r', encoding='utf-8') as f: all_data = json.load(f)
            except: pass
        all_data.append(new_record)
        try:
            with open(self.output_json_path, 'w', encoding='utf-8') as f: json.dump(all_data, f, indent=2, ensure_ascii=False)
            self.current_entry.points.clear(); self.reload_saved_annotations(); self.update_labels(); self.draw_plot(preserve_limits=True)
        except Exception as e: QMessageBox.critical(self, "Ошибка", str(e))

    # --- ОТРИСОВКА ---
    def draw_plot(self, preserve_limits=False):
        if not self.current_signal: return
        old_xlim = self.canvas.axes.get_xlim(); old_ylim = self.canvas.axes.get_ylim()
        if self.is_custom_zoom: start_t, end_t = old_xlim
        else:
            start_sample = self.scrollbar.value(); start_t = start_sample / self.current_signal.frequency; end_t = start_t + self.default_window_sec

        try: signal_fragment = self.current_signal.get_fragment(max(0, start_t - 2.0), end_t + 2.0)
        except: signal_fragment = self.current_signal

        self.canvas.axes.clear(); self.drawer.draw_signal(signal_fragment)

        # Зеленые (сохраненные)
        for group in self.saved_annotations:
            for p_n, p_t in group.items():
                self.canvas.axes.axvline(p_t, color='green', linestyle='-', linewidth=1.5, alpha=0.8)
                y_pos = self.canvas.axes.get_ylim()[1]
                self.canvas.axes.text(p_t, y_pos, p_n, color='green', fontsize=8, ha='center', va='bottom')
        
        # Красные (текущие)
        for p_n, p_t in self.current_entry.points.items():
            self.canvas.axes.axvline(p_t, color='red', linestyle='--', linewidth=2)
            y_pos = self.canvas.axes.get_ylim()[1]
            self.canvas.axes.text(p_t, y_pos, p_n, color='red', fontsize=12, fontweight='bold', ha='center', va='bottom')

        if preserve_limits or self.is_custom_zoom:
            self.canvas.axes.set_xlim(old_xlim); self.canvas.axes.set_ylim(old_ylim)
        else: self.canvas.axes.set_xlim(start_t, end_t)
        self.canvas.draw()

    def update_labels(self):
        pts = self.current_entry.points
        self.lbl_p1.setText(f"p1: {pts.get('p1', '-')}")
        self.lbl_p2.setText(f"p2: {pts.get('p2', '-')}")
        self.lbl_p3.setText(f"p3: {pts.get('p3', '-')}")