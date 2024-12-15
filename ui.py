from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QComboBox, QLineEdit, QPushButton, QAbstractItemView, QInputDialog, QFormLayout,
    QTableWidget, QTableWidgetItem, QHBoxLayout, QVBoxLayout, QWidget, QMessageBox, QHeaderView, QDialog,
    QDialogButtonBox, QDateTimeEdit, QLabel, QSpinBox
)
from PyQt6.QtGui import QFont, QIntValidator, QRegularExpressionValidator
from PyQt6.QtCore import QRegularExpression, QDateTime
import psycopg2
import json

from fpdf import FPDF
import os

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Database Manager")
        self.setGeometry(100, 100, 1200, 600)

        with open("table_metadata.json", "r", encoding="utf-8") as file:
            self.metadata = json.load(file)

        # Установка шрифта для приложения
        app_font = QFont("Arial", 12)
        QApplication.setFont(app_font)

        self.db_connection = None
        self.cursor = None
        self.current_table = None
        self.sort_order = {}

        self.setup_ui()
        self.connect_to_database()

    def setup_ui(self):
        # Основной виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Выбор таблицы
        self.table_selector = QComboBox()
        self.table_selector.currentIndexChanged.connect(self.load_table_data)

        # Кнопка добавления записи
        add_record_button = QPushButton("Добавить запись в таблицу")
        add_record_button.clicked.connect(self.open_add_record_form)

        # Поле поиска
        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Введите запрос для поиска...")

        # Кнопка поиска
        search_button = QPushButton("Найти")
        search_button.clicked.connect(self.search_records)

        # Таблица для отображения данных
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(0)
        self.table_widget.setRowCount(0)
        self.table_widget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        # Кнопка "Сформировать отчет"
        generate_report_button = QPushButton("Сформировать отчет")
        generate_report_button.setStyleSheet("position: absolute; bottom: 20px; right: 20px;")
        generate_report_button.clicked.connect(self.open_report_dialog)

        # Layout
        top_layout = QHBoxLayout()
        top_layout.addWidget(self.table_selector)
        top_layout.addStretch(1)
        top_layout.addWidget(add_record_button)
        top_layout.addStretch(1)
        top_layout.addWidget(self.search_field)
        top_layout.addWidget(search_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.table_widget)
        main_layout.addWidget(generate_report_button)

        central_widget.setLayout(main_layout)

    def connect_to_database(self):
        try:
            self.db_connection = psycopg2.connect(
                dbname="vokzal",
                user="postgres",
                password="pass",
                host="localhost",
                port=5432
            )
            self.cursor = self.db_connection.cursor()
            self.load_table_names()
        except psycopg2.Error as e:
            QMessageBox.critical(self, "Ошибка подключения", f"Не удалось подключиться к базе данных:\n{e}")
            self.close()

    def load_table_names(self):
        try:
            # Получаем список таблиц из мета-данных
            table_names = self.metadata.keys()

            # Очищаем список выбора таблиц
            self.table_selector.clear()

            # Добавляем таблицы из мета-данных в виджет выбора
            for table_name in table_names:
                self.table_selector.addItem(table_name)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка загрузки таблиц", f"Не удалось загрузить список таблиц:\n{e}")

    def load_rows(self, rows, column_names):
        # Очистка таблицы перед добавлением новых данных
        self.table_widget.clearContents()
        self.table_widget.setRowCount(0)
        self.table_widget.setColumnCount(0)  # Обнуляем количество столбцов

        # Настройка таблицы
        self.table_widget.setColumnCount(len(column_names) + 1)  # Добавляем одну колонку для кнопок
        self.table_widget.setHorizontalHeaderLabels(column_names + ['Действия'])

        # Устанавливаем фиксированную ширину последнего столбца для кнопок
        self.table_widget.setColumnWidth(len(column_names), 80)

        # Устанавливаем растягивание для всех остальных столбцов
        for col_idx in range(len(column_names)):
            self.table_widget.horizontalHeader().setSectionResizeMode(col_idx, QHeaderView.ResizeMode.Stretch)

        # Включаем сортировку таблицы
        self.table_widget.setSortingEnabled(True)

        # Добавляем данные в таблицу и кнопки
        for row_idx, row_data in enumerate(rows):
            self.table_widget.insertRow(row_idx)  # Вставка новой строки
            for col_idx, cell_data in enumerate(row_data):
                self.table_widget.setItem(row_idx, col_idx, QTableWidgetItem(str(cell_data)))

            # Создаем контейнер для кнопок (кнопки в одной ячейке)
            action_widget = QWidget()

            # Кнопки в виде смайликов
            edit_button = QPushButton("✏️")  # Смайлик для "Редактировать"
            delete_button = QPushButton("🗑️")  # Смайлик для "Удалить"

            # Устанавливаем фиксированные размеры кнопок
            edit_button.setFixedSize(30, 30)
            delete_button.setFixedSize(30, 30)

            # Располагаем кнопки горизонтально
            action_layout = QHBoxLayout(action_widget)
            action_layout.addWidget(edit_button)
            action_layout.addWidget(delete_button)

            # Устанавливаем контейнер в ячейку таблицы
            self.table_widget.setCellWidget(row_idx, len(column_names), action_widget)

            # Связываем действия с кнопками
            edit_button.clicked.connect(lambda _, row=dict(zip(column_names, row_data)): self.edit_record(row))
            delete_button.clicked.connect(lambda _, row=dict(zip(column_names, row_data)): self.delete_record(row))

            # Устанавливаем фиксированную высоту строки
            self.table_widget.setRowHeight(row_idx, 40)

        # Подключаем обработчик для клика по заголовку таблицы
        self.table_widget.horizontalHeader().sectionClicked.connect(self.sort_table)

    def load_table_data(self):
        self.current_table = self.table_selector.currentText()
        if not self.current_table:
            return

        try:
            query = f"SELECT * FROM {self.current_table}"
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            column_names = [desc[0] for desc in self.cursor.description]

            self.load_rows(rows, column_names)

        except psycopg2.Error as e:
            QMessageBox.critical(self, "Ошибка загрузки данных", f"Не удалось загрузить данные из таблицы:\n{e}")

    def sort_table(self, index):
        if index in self.sort_order:
            # Если сортировка уже была включена для этого столбца, меняем направление
            self.sort_order[index] = not self.sort_order[index]
        else:
            # Если сортировка еще не была включена для этого столбца, сортируем по убыванию
            self.sort_order = {key: False for key in self.sort_order}  # Сброс сортировки всех других столбцов
            self.sort_order[index] = True  # Устанавливаем сортировку по убыванию для текущего столбца

    def open_add_record_form(self):
        try:
            meta = self.metadata[self.current_table]
            fields = meta["fields"]
        except KeyError:
            QMessageBox.critical(self, "Ошибка", f"Нет метаданных для таблицы '{self.current_table}'!")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle(f"Добавить запись в {self.current_table}")
        layout = QFormLayout(dialog)

        input_fields = {}
        input_types = {}
        for field, details in fields.items():
            input_type = details.get("input_type", "text")
            input_types[field] = input_type

            if input_type == "dropdown":
                combo_box = QComboBox()
                source_table = details["source_table"]
                source_column = details["source_column"]
                # Получение данных для выпадающего списка
                query = f"SELECT {source_column} FROM {source_table}"
                self.cursor.execute(query)
                values = [str(row[0]) for row in self.cursor.fetchall()]
                combo_box.addItems(values)
                layout.addRow(f"{details['description']} ({field}):", combo_box)
                input_fields[field] = combo_box
            elif input_type == "datetime":
                date_edit = QDateTimeEdit()
                date_edit.setCalendarPopup(True)
                layout.addRow(f"{details['description']} ({field}):", date_edit)
                input_fields[field] = date_edit
            elif input_type == "number":
                line_edit = QLineEdit()
                line_edit.setValidator(QIntValidator())
                layout.addRow(f"{details['description']} ({field}):", line_edit)
                input_fields[field] = line_edit
            elif input_type == "staff_inn":
                line_edit = QLineEdit()
                line_edit.setValidator(QRegularExpressionValidator(QRegularExpression("\\d{12}")))
                layout.addRow(f"{details['description']} ({field}):", line_edit)
                input_fields[field] = line_edit
            elif input_type == "station_inn":
                line_edit = QLineEdit()
                line_edit.setValidator(QRegularExpressionValidator(QRegularExpression("\\d{10}")))
                layout.addRow(f"{details['description']} ({field}):", line_edit)
                input_fields[field] = line_edit
            elif input_type == "gender_dropdown":
                combo_box = QComboBox()
                combo_box.addItems(["M", "F"])
                layout.addRow(f"{details['description']} ({field}):", combo_box)
                input_fields[field] = combo_box
            elif input_type == "text":
                line_edit = QLineEdit()
                layout.addRow(f"{details['description']} ({field}):", line_edit)
                input_fields[field] = line_edit

        # Дополнительное поле для добавления сотрудников, если таблица brigade_routes
        if self.current_table == "brigade_routes":
            staff_count_input = QLineEdit("0")
            staff_count_input.setValidator(QIntValidator(0, 100))
            layout.addRow("Добавить сотрудников (в таблицу staff):", staff_count_input)
            input_fields["staff_count"] = staff_count_input

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(lambda: self.submit_add_record(dialog, input_fields, input_types))
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        dialog.exec()

    def submit_add_record(self, dialog, input_fields, input_types):
        data = {}
        staff_count = 0

        for field, widget in input_fields.items():
            input_type = input_types.get(field, "text")  # Получаем тип поля
            if isinstance(widget, QComboBox):
                value = widget.currentText().strip()
            elif isinstance(widget, QDateTimeEdit):
                value = widget.dateTime().toString("yyyy-MM-dd HH:mm:ss")
            else:
                value = widget.text().strip()

            if not value:
                QMessageBox.warning(dialog, "Ошибка", f"Поле '{field}' не заполнено!")
                return

            if input_type == "staff_inn" and (len(value) != 12 or not value.isdigit()):
                QMessageBox.warning(dialog, "Ошибка", "ИНН сотрудника должен содержать ровно 12 цифр!")
                return
            elif input_type == "station_inn" and (len(value) != 10 or not value.isdigit()):
                QMessageBox.warning(dialog, "Ошибка", "ИНН станции должен содержать ровно 10 цифр!")
                return

            data[field] = value

        if "staff_count" in data:
            staff_count = int(data["staff_count"])
            del data["staff_count"]

        try:
            self.add_record(data)

            brigade_name = data.get("brigade_name", "")
            for i in range(1, staff_count + 1):
                self.open_add_staff_form(i, [brigade_name])

            self.load_table_data()
            QMessageBox.information(self, "Успех", "Запись успешно добавлена!")
            dialog.accept()
        except Exception as e:
            QMessageBox.critical(dialog, "Ошибка", f"Не удалось добавить запись:\n{e}")

    def add_record(self, data):
        try:
            # Получение метаданных из JSON
            meta = self.metadata[self.current_table]

            # Формируем запрос на добавление записи в основную таблицу
            table_name = meta.get("main_table", self.current_table)
            fields_str = ", ".join(data.keys())
            placeholders = ", ".join(["%s"] * len(data))
            insert_query = f"INSERT INTO {table_name} ({fields_str}) VALUES ({placeholders})"

            # Выполняем запрос
            self.cursor.execute(insert_query, tuple(data.values()))
            self.db_connection.commit()

        except psycopg2.Error as e:
            self.db_connection.rollback()
            QMessageBox.critical(self, "Ошибка", f"Ошибка добавления записи:\n{e}")

    def open_add_staff_form(self, staff_index, brigade_name):
        try:
            meta = self.metadata["staff_details"]
            fields = meta["fields"]
        except KeyError:
            QMessageBox.critical(self, "Ошибка", "Нет метаданных для таблицы 'staff_details'!")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle(f"Добавить сотрудника {staff_index}")
        layout = QFormLayout(dialog)

        input_fields = {}
        for field, details in fields.items():
            input_type = details.get("input_type", "text")

            if input_type == "dropdown":
                combo_box = QComboBox()
                if field == "brigade_name":
                    combo_box.addItems(brigade_name)
                else:
                    source_table = details["source_table"]
                    source_column = details["source_column"]
                    query = f"SELECT {source_column} FROM {source_table}"
                    self.cursor.execute(query)
                    values = [str(row[0]) for row in self.cursor.fetchall()]
                    combo_box.addItems(values)
                layout.addRow(f"{details['description']} ({field}):", combo_box)
                input_fields[field] = combo_box
            elif input_type == "datetime":
                date_edit = QDateTimeEdit()
                date_edit.setCalendarPopup(True)
                layout.addRow(f"{details['description']} ({field}):", date_edit)
                input_fields[field] = date_edit
            elif input_type == "number":
                line_edit = QLineEdit()
                line_edit.setValidator(QIntValidator())
                layout.addRow(f"{details['description']} ({field}):", line_edit)
                input_fields[field] = line_edit
            elif input_type == "staff_inn":
                line_edit = QLineEdit()
                line_edit.setValidator(QRegularExpressionValidator(QRegularExpression("\\d{12}")))
                layout.addRow(f"{details['description']} ({field}):", line_edit)
                input_fields[field] = line_edit
            elif input_type == "gender_dropdown":
                combo_box = QComboBox()
                combo_box.addItems(["M", "F"])
                layout.addRow(f"{details['description']} ({field}):", combo_box)
                input_fields[field] = combo_box
            elif input_type == "text":
                line_edit = QLineEdit()
                layout.addRow(f"{details['description']} ({field}):", line_edit)
                input_fields[field] = line_edit

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(lambda: self.submit_add_staff(dialog, input_fields, staff_index))
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        dialog.exec()

    def submit_add_staff(self, dialog, input_fields, staff_index):
        data = {}
        for field, widget in input_fields.items():
            if isinstance(widget, QComboBox):
                value = widget.currentText().strip()
            elif isinstance(widget, QDateTimeEdit):
                value = widget.dateTime().toString("yyyy-MM-dd HH:mm:ss")
            else:
                value = widget.text().strip()

            if not value:
                QMessageBox.warning(dialog, "Ошибка", f"Поле '{field}' не заполнено!")
                return

            if field == "inn" and len(value) != 12:
                QMessageBox.warning(dialog, "Ошибка", "ИНН должен содержать ровно 12 цифр!")
                return

            data[field] = value

        try:
            self.add_staff(data)
            QMessageBox.information(dialog, "Успех", f"Сотрудник {staff_index} успешно добавлен!")
            dialog.accept()
        except Exception as e:
            QMessageBox.critical(dialog, "Ошибка", f"Не удалось добавить сотрудника {staff_index}: {e}")

    def add_staff(self, data):
        try:
            # Получение метаданных из JSON
            meta = self.metadata["staff_details"]

            # Формируем запрос на добавление записи в основную таблицу
            table_name = meta.get("main_table", "staff_details")
            fields_str = ", ".join(data.keys())
            placeholders = ", ".join(["%s"] * len(data))
            insert_query = f"INSERT INTO {table_name} ({fields_str}) VALUES ({placeholders})"

            # Выполняем запрос
            self.cursor.execute(insert_query, tuple(data.values()))
            self.db_connection.commit()

        except psycopg2.Error as e:
            self.db_connection.rollback()
            QMessageBox.critical(self, "Ошибка", f"Ошибка добавления записи:\n{e}")

    def edit_record(self, row_data):
        try:
            # Получение метаданных для текущей таблицы
            meta = self.metadata[self.current_table]
            fields = meta["fields"]

            dialog = QDialog(self)
            dialog.setWindowTitle(f"Редактировать запись в {self.current_table}")
            layout = QFormLayout(dialog)

            input_fields = {}

            # Заполнение полей данными из строки
            for field, details in fields.items():
                input_type = details.get("input_type", "text")
                current_value = row_data.get(field, "")

                if input_type == "dropdown":
                    combo_box = QComboBox()
                    source_table = details["source_table"]
                    source_column = details["source_column"]
                    query = f"SELECT {source_column} FROM {source_table}"
                    self.cursor.execute(query)
                    values = [str(row[0]) for row in self.cursor.fetchall()]
                    combo_box.addItems(values)
                    combo_box.setCurrentText(str(current_value))
                    layout.addRow(f"{details['description']} ({field}):", combo_box)
                    input_fields[field] = combo_box
                elif input_type == "datetime":
                    date_edit = QDateTimeEdit()
                    date_edit.setCalendarPopup(True)
                    if current_value:
                        date_edit.setDateTime(QDateTime.fromString(current_value, "yyyy-MM-dd HH:mm:ss"))
                    layout.addRow(f"{details['description']} ({field}):", date_edit)
                    input_fields[field] = date_edit
                elif input_type == "number":
                    line_edit = QLineEdit()
                    line_edit.setValidator(QIntValidator())
                    line_edit.setText(str(current_value))
                    layout.addRow(f"{details['description']} ({field}):", line_edit)
                    input_fields[field] = line_edit
                elif input_type == "staff_inn":
                    line_edit = QLineEdit()
                    line_edit.setValidator(QRegularExpressionValidator(QRegularExpression("\\d{12}")))
                    line_edit.setText(str(current_value))
                    layout.addRow(f"{details['description']} ({field}):", line_edit)
                    input_fields[field] = line_edit
                elif input_type == "station_inn":
                    line_edit = QLineEdit()
                    line_edit.setValidator(QRegularExpressionValidator(QRegularExpression("\\d{10}")))
                    line_edit.setText(str(current_value))
                    layout.addRow(f"{details['description']} ({field}):", line_edit)
                    input_fields[field] = line_edit
                elif input_type == "gender_dropdown":
                    combo_box = QComboBox()
                    combo_box.addItems(["M", "F"])
                    combo_box.setCurrentText(str(current_value))
                    layout.addRow(f"{details['description']} ({field}):", combo_box)
                    input_fields[field] = combo_box
                elif input_type == "text":
                    line_edit = QLineEdit()
                    line_edit.setText(str(current_value))
                    layout.addRow(f"{details['description']} ({field}):", line_edit)
                    input_fields[field] = line_edit

            button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
            button_box.accepted.connect(lambda: self.submit_edit_record(dialog, row_data, input_fields))
            button_box.rejected.connect(dialog.reject)
            layout.addWidget(button_box)

            dialog.exec()

        except KeyError:
            QMessageBox.critical(self, "Ошибка", f"Нет метаданных для таблицы '{self.current_table}'!")

    def submit_edit_record(self, dialog, row_data, input_fields):
        try:
            new_data = {}

            # Сбор новых данных из формы
            for field, widget in input_fields.items():
                if isinstance(widget, QComboBox):
                    value = widget.currentText().strip()
                elif isinstance(widget, QDateTimeEdit):
                    value = widget.dateTime().toString("yyyy-MM-dd HH:mm:ss")
                else:
                    value = widget.text().strip()

                if not value:
                    QMessageBox.warning(dialog, "Ошибка", f"Поле '{field}' не заполнено!")
                    return

                new_data[field] = value

            # Удаление старой записи
            self.delete_record(row_data)

            # Добавление новой записи с обновленными данными
            self.add_record(new_data)

            self.load_table_data()
            QMessageBox.information(self, "Успех", "Запись успешно обновлена!")
            dialog.accept()
        except Exception as e:
            QMessageBox.critical(dialog, "Ошибка", f"Не удалось обновить запись:\n{e}")

    def delete_record(self, row_data):
        try:
            # Получаем имя таблицы и ключевые столбцы из мета-данных
            table_name = self.metadata[self.current_table]["delete_map"]["table"]
            key_columns = self.metadata[self.current_table]["delete_map"]["keys"]  # Список ключей

            # Формируем условие WHERE с учетом всех ключей
            where_clause = " AND ".join([f"{key} = %s" for key in key_columns])
            key_values = [row_data.get(key) for key in key_columns]  # Получаем значения ключей из строки

            # Проверяем, что все ключевые значения присутствуют
            if None in key_values:
                QMessageBox.critical(self, "Ошибка", "Не все ключевые значения найдены в данных строки!")
                return

            # Формируем SQL-запрос на удаление
            query = f"DELETE FROM {table_name} WHERE {where_clause}"
            self.cursor.execute(query, key_values)
            self.db_connection.commit()

            self.load_table_data()
            QMessageBox.information(self, "Успех", "Запись успешно удалена.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось удалить запись: {e}")


    def search_records(self):
        search_query = self.search_field.text()
        if not search_query or not self.current_table:
            self.load_table_data()
            return

        try:
            # Запрос для поиска по всем полям таблицы
            query = f"SELECT * FROM {self.current_table} WHERE " + " OR ".join(
                [f"CAST({col[0]} AS TEXT) ILIKE %s" for col in self.cursor.description]
            )
            search_pattern = f"%{search_query}%"
            self.cursor.execute(query, [search_pattern] * len(self.cursor.description))

            rows = self.cursor.fetchall()

            column_names = [desc[0] for desc in self.cursor.description]

            self.load_rows(rows, column_names)

        except psycopg2.Error as e:
            QMessageBox.critical(self, "Ошибка поиска", f"Не удалось выполнить поиск:\n{e}")

    def get_column_names(self):
        if not self.current_table:
            return []
        self.cursor.execute(f"SELECT * FROM {self.current_table} LIMIT 1")
        return [desc[0] for desc in self.cursor.description]

    def open_report_dialog(self):
        # Окно выбора типа отчета
        dialog = QDialog(self)
        dialog.setWindowTitle("Сформировать отчет")

        report_type_label = QLabel("Выберите отчет:")
        self.report_type_combobox = QComboBox()
        self.report_type_combobox.addItems([
            "Среднее время в пути для маршрутов",
            "Популярные направления маршрутов",
            "Используемость бригад"
        ])

        # Кнопка "OK" для продолжения
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(lambda: self.open_selected_report(dialog))
        button_box.rejected.connect(dialog.reject)

        layout = QFormLayout()
        layout.addRow(report_type_label, self.report_type_combobox)
        layout.addWidget(button_box)
        dialog.setLayout(layout)

        dialog.exec()

    def open_selected_report(self, parent_dialog):
        # Получаем выбранный тип отчета
        selected_report = self.report_type_combobox.currentText()

        # Открываем соответствующее окно настроек отчета
        if selected_report == "Среднее время в пути для маршрутов":
            self.open_route_report_dialog(parent_dialog)
        elif selected_report == "Популярные направления маршрутов":
            self.open_popular_directions_report_dialog(parent_dialog)
        elif selected_report == "Используемость бригад":
            self.open_brigade_usage_report_dialog(parent_dialog)

    def open_route_report_dialog(self, parent_dialog):
        parent_dialog.accept()

        dialog = QDialog(self)
        dialog.setWindowTitle("Настройки отчета: Среднее время в пути")

        # Вокзал отправления
        station_label = QLabel("Вокзал отправления:")
        self.station_combobox = QComboBox()
        self.get_station_names()

        # Диапазон времени отправления
        date_range_label = QLabel("Диапазон времени отправления:")
        self.start_date_edit = QDateTimeEdit(QDateTime.currentDateTime())
        self.start_date_edit.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.end_date_edit = QDateTimeEdit(QDateTime.currentDateTime())
        self.end_date_edit.setDisplayFormat("yyyy-MM-dd HH:mm:ss")

        # Сортировка
        sort_label = QLabel("Сортировка:")
        self.sort_combobox = QComboBox()
        self.sort_combobox.addItems(["ASC", "DESC"])

        # Кнопки
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(lambda: self.generate_route_report(dialog))
        button_box.rejected.connect(dialog.reject)

        # Layout
        layout = QFormLayout()
        layout.addRow(station_label, self.station_combobox)
        layout.addRow(date_range_label, self.start_date_edit)
        layout.addRow("", self.end_date_edit)
        layout.addRow(sort_label, self.sort_combobox)
        layout.addWidget(button_box)
        dialog.setLayout(layout)

        dialog.exec()

    def get_station_names(self):
        try:
            query = "SELECT name FROM stations"
            self.cursor.execute(query)
            stations = self.cursor.fetchall()
            for station in stations:
                self.station_combobox.addItem(station[0])  # Добавляем вокзал в список
        except psycopg2.Error as e:
            QMessageBox.critical(self, "Ошибка загрузки вокзалов", f"Не удалось загрузить вокзалы:\n{e}")

    def generate_route_report(self, dialog):
        departure_station = self.station_combobox.currentText()
        start_date = self.start_date_edit.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        end_date = self.end_date_edit.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        sort_order = self.sort_combobox.currentText()

        # Формируем SQL запрос
        query = f"""
        SELECT 
            s1.name AS departure_station,
            s2.name AS arrival_station,
            ROUND(AVG(EXTRACT(EPOCH FROM (r.arrival_time - r.departure_time)) / 3600), 2) AS avg_travel_time_hours,
            COUNT(*) AS route_count
        FROM 
            routes r
        JOIN stations s1 ON r.departure_station_code = s1.station_code
        JOIN stations s2 ON r.arrival_station_code = s2.station_code
        WHERE 
            r.departure_time BETWEEN %s AND %s
            AND s1.name = %s
        GROUP BY 
            s1.name, s2.name
        ORDER BY 
            avg_travel_time_hours {sort_order};
        """

        try:
            # Выполняем SQL запрос с переданными параметрами
            self.cursor.execute(query, (start_date, end_date, departure_station))
            report_data = self.cursor.fetchall()

            if not report_data:
                QMessageBox.warning(self, "Нет данных", "Для заданного периода и фильтров данные отсутствуют.")
                return

            # Создаем PDF файл
            pdf_file_path = os.path.join(os.path.expanduser("~"), "Desktop", "route_report.pdf")
            self.create_route_pdf(report_data, pdf_file_path)

            # Показываем сообщение об успешном сохранении
            QMessageBox.information(self, "Отчет сформирован", f"Отчет сохранен на рабочем столе:\n{pdf_file_path}")
            dialog.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка генерации отчета", f"Не удалось сгенерировать отчет:\n{e}")

    def create_route_pdf(self, data, file_path):
        pdf = FPDF()
        pdf.add_page()

        # Пути к файлам шрифтов
        font_dir = os.path.join(os.path.dirname(__file__), "fonts")
        regular_font_path = os.path.join(font_dir, "timesnrcyrmt.ttf")
        bold_font_path = os.path.join(font_dir, "timesnrcyrmt_bold.ttf")

        # Подключение пользовательских шрифтов
        pdf.add_font("TimesNewRoman", style="", fname=regular_font_path, uni=True)
        pdf.add_font("TimesNewRoman", style="B", fname=bold_font_path, uni=True)

        # Устанавливаем шрифт
        pdf.set_font("TimesNewRoman", size=12)

        # Заголовок
        pdf.set_font("TimesNewRoman", style="B", size=16)
        pdf.cell(0, 10, "Отчет по маршрутам", ln=True, align="C")
        pdf.ln(10)  # Отступ

        # Заголовки таблицы
        pdf.set_font("TimesNewRoman", style="B", size=12)
        column_headers = ["Вокзал отправления", "Вокзал прибытия", "Сред. время (ч)", "Кол-во маршрутов"]
        column_widths = [50, 50, 40, 40]

        for i, header in enumerate(column_headers):
            pdf.cell(column_widths[i], 10, header, border=1, align="C")
        pdf.ln()

        # Данные таблицы
        pdf.set_font("TimesNewRoman", size=12)
        for row in data:
            for i, cell in enumerate(row):
                pdf.cell(column_widths[i], 10, str(cell), border=1, align="C")
            pdf.ln()

        # Сохраняем файл
        try:
            pdf.output(file_path)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить файл:\n{e}")

    def open_popular_directions_report_dialog(self, parent_dialog):
        parent_dialog.accept()

        dialog = QDialog(self)
        dialog.setWindowTitle("Настройки отчета: Популярные направления маршрутов")

        # Диапазон времени отправления
        date_range_label = QLabel("Диапазон времени отправления:")
        self.start_date_edit = QDateTimeEdit(QDateTime.currentDateTime())
        self.start_date_edit.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.end_date_edit = QDateTimeEdit(QDateTime.currentDateTime())
        self.end_date_edit.setDisplayFormat("yyyy-MM-dd HH:mm:ss")

        # Сортировка
        sort_label = QLabel("Сортировка:")
        self.sort_combobox = QComboBox()
        self.sort_combobox.addItems(["По количеству маршрутов", "По общему времени в пути"])

        # Кнопки
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(lambda: self.generate_popular_directions_report(dialog))
        button_box.rejected.connect(dialog.reject)

        # Layout
        layout = QFormLayout()
        layout.addRow(date_range_label, self.start_date_edit)
        layout.addRow("", self.end_date_edit)
        layout.addRow(sort_label, self.sort_combobox)
        layout.addWidget(button_box)
        dialog.setLayout(layout)

        dialog.exec()

    def generate_popular_directions_report(self, dialog):
        start_date = self.start_date_edit.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        end_date = self.end_date_edit.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        sort_order = "route_count DESC, total_travel_time_hours DESC" if self.sort_combobox.currentText() == "По количеству маршрутов" else "total_travel_time_hours DESC, route_count DESC"

        # Формируем SQL запрос
        query = f"""
        SELECT 
            s1.name AS departure_station,
            s2.name AS arrival_station,
            COUNT(r.route_code) AS route_count,
            ROUND(SUM(EXTRACT(EPOCH FROM (r.arrival_time - r.departure_time))) / 3600, 2) AS total_travel_time_hours
        FROM 
            routes r
        JOIN stations s1 ON r.departure_station_code = s1.station_code
        JOIN stations s2 ON r.arrival_station_code = s2.station_code
        WHERE 
            r.departure_time BETWEEN %s AND %s
        GROUP BY 
            s1.name, s2.name
        ORDER BY 
            {sort_order};
        """

        try:
            # Выполняем SQL запрос с переданными параметрами
            self.cursor.execute(query, (start_date, end_date))
            report_data = self.cursor.fetchall()

            if not report_data:
                QMessageBox.warning(self, "Нет данных", "Для заданного периода данные отсутствуют.")
                return

            # Создаем PDF файл
            pdf_file_path = os.path.join(os.path.expanduser("~"), "Desktop", "popular_directions_report.pdf")
            self.create_popular_routes_pdf(report_data, pdf_file_path)

            # Показываем сообщение об успешном сохранении
            QMessageBox.information(self, "Отчет сформирован", f"Отчет сохранен на рабочем столе:\n{pdf_file_path}")
            dialog.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка генерации отчета", f"Не удалось сгенерировать отчет:\n{e}")

    def create_popular_routes_pdf(self, data, file_path):
        pdf = FPDF()
        pdf.add_page()

        # Пути к файлам шрифтов
        font_dir = os.path.join(os.path.dirname(__file__), "fonts")
        regular_font_path = os.path.join(font_dir, "timesnrcyrmt.ttf")
        bold_font_path = os.path.join(font_dir, "timesnrcyrmt_bold.ttf")

        # Подключение пользовательских шрифтов
        pdf.add_font("TimesNewRoman", style="", fname=regular_font_path, uni=True)
        pdf.add_font("TimesNewRoman", style="B", fname=bold_font_path, uni=True)

        # Устанавливаем шрифт
        pdf.set_font("TimesNewRoman", size=12)

        # Заголовок
        pdf.set_font("TimesNewRoman", style="B", size=16)
        pdf.cell(0, 10, "Популярные направления маршрутов", ln=True, align="C")
        pdf.ln(10)  # Отступ

        # Заголовки таблицы
        pdf.set_font("TimesNewRoman", style="B", size=12)
        column_headers = ["Вокзал отправления", "Вокзал прибытия", "Кол-во маршрутов", "Общее время (ч)"]
        column_widths = [50, 50, 40, 50]

        for i, header in enumerate(column_headers):
            pdf.cell(column_widths[i], 10, header, border=1, align="C")
        pdf.ln()

        # Данные таблицы
        pdf.set_font("TimesNewRoman", size=12)
        for row in data:
            for i, cell in enumerate(row):
                pdf.cell(column_widths[i], 10, str(cell), border=1, align="C")
            pdf.ln()

        # Сохраняем файл
        try:
            pdf.output(file_path)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить файл:\n{e}")

    def open_brigade_usage_report_dialog(self, parent_dialog):
        parent_dialog.accept()

        dialog = QDialog(self)
        dialog.setWindowTitle("Настройки отчета: Используемость бригад")

        # Диапазон времени отправления
        date_range_label = QLabel("Диапазон времени отправления:")
        self.start_date_edit = QDateTimeEdit(QDateTime.currentDateTime())
        self.start_date_edit.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.end_date_edit = QDateTimeEdit(QDateTime.currentDateTime())
        self.end_date_edit.setDisplayFormat("yyyy-MM-dd HH:mm:ss")

        # Минимальный стаж сотрудников
        min_experience_label = QLabel("Минимальный стаж сотрудников:")
        self.min_experience_edit = QSpinBox()
        self.min_experience_edit.setMinimum(0)
        self.min_experience_edit.setMaximum(100)
        self.min_experience_edit.setValue(0)

        # Сортировка
        sort_label = QLabel("Сортировка:")
        self.sort_combobox = QComboBox()
        self.sort_combobox.addItems(["По количеству маршрутов", "По среднему стажу"])

        # Кнопки
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(lambda: self.generate_brigade_usage_report(dialog))
        button_box.rejected.connect(dialog.reject)

        # Layout
        layout = QFormLayout()
        layout.addRow(date_range_label, self.start_date_edit)
        layout.addRow("", self.end_date_edit)
        layout.addRow(min_experience_label, self.min_experience_edit)
        layout.addRow(sort_label, self.sort_combobox)
        layout.addWidget(button_box)
        dialog.setLayout(layout)

        dialog.exec()

    def generate_brigade_usage_report(self, dialog):
        start_date = self.start_date_edit.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        end_date = self.end_date_edit.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        min_experience = self.min_experience_edit.value()
        sort_order = "route_count DESC, avg_experience_years DESC" if self.sort_combobox.currentText() == "По количеству маршрутов" else "avg_experience_years DESC, route_count DESC"

        # Формируем SQL запрос
        query = f"""
        SELECT 
            b.name AS brigade_name,
            COUNT(rb.route_code) AS route_count,
            ROUND(AVG(s.experience_years), 2) AS avg_experience_years
        FROM 
            route_brigades rb
        JOIN brigades b ON rb.brigade_code = b.brigade_code
        JOIN staff s ON s.brigade_code = b.brigade_code
        WHERE 
            s.experience_years >= %s
            AND rb.route_code IN (
                SELECT route_code 
                FROM routes 
                WHERE departure_time BETWEEN %s AND %s
            )
        GROUP BY 
            b.name
        ORDER BY 
            {sort_order};
        """

        try:
            # Выполняем SQL запрос с переданными параметрами
            self.cursor.execute(query, (min_experience, start_date, end_date))
            report_data = self.cursor.fetchall()

            if not report_data:
                QMessageBox.warning(self, "Нет данных", "Для заданного периода и фильтров данные отсутствуют.")
                return

            # Создаем PDF файл
            pdf_file_path = os.path.join(os.path.expanduser("~"), "Desktop", "brigade_usage_report.pdf")
            self.create_brigade_usage_pdf(report_data, pdf_file_path)

            # Показываем сообщение об успешном сохранении
            QMessageBox.information(self, "Отчет сформирован", f"Отчет сохранен на рабочем столе:\n{pdf_file_path}")
            dialog.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка генерации отчета", f"Не удалось сгенерировать отчет:\n{e}")

    def create_brigade_usage_pdf(self, data, file_path):
        pdf = FPDF()
        pdf.add_page()

        # Пути к файлам шрифтов
        font_dir = os.path.join(os.path.dirname(__file__), "fonts")
        regular_font_path = os.path.join(font_dir, "timesnrcyrmt.ttf")
        bold_font_path = os.path.join(font_dir, "timesnrcyrmt_bold.ttf")

        # Подключение пользовательских шрифтов
        pdf.add_font("TimesNewRoman", style="", fname=regular_font_path, uni=True)
        pdf.add_font("TimesNewRoman", style="B", fname=bold_font_path, uni=True)

        # Устанавливаем шрифт
        pdf.set_font("TimesNewRoman", size=12)

        # Заголовок
        pdf.set_font("TimesNewRoman", style="B", size=16)
        pdf.cell(0, 10, "Используемость бригад", ln=True, align="C")
        pdf.ln(10)  # Отступ

        # Заголовки таблицы
        pdf.set_font("TimesNewRoman", style="B", size=12)
        column_headers = ["Название бригады", "Количество маршрутов", "Средний стаж (годы)"]
        column_widths = [70, 50, 60]

        for i, header in enumerate(column_headers):
            pdf.cell(column_widths[i], 10, header, border=1, align="C")
        pdf.ln()

        # Данные таблицы
        pdf.set_font("TimesNewRoman", size=12)
        for row in data:
            for i, cell in enumerate(row):
                pdf.cell(column_widths[i], 10, str(cell), border=1, align="C")
            pdf.ln()

        # Сохраняем файл
        try:
            pdf.output(file_path)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить файл:\n{e}")

    def closeEvent(self, event):
        if self.cursor:
            self.cursor.close()
        if self.db_connection:
            self.db_connection.close()
        event.accept()
