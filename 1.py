# crop_price_calculator.py
# Приложение для расчёта реализационной цены продукции растениеводства (Вариант 8)

import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit,
                             QVBoxLayout, QPushButton, QComboBox, QMessageBox, QInputDialog)
from PyQt5.QtCore import Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Расчет реализационной цены")
        self.setGeometry(100, 100, 600, 700)

        layout = QVBoxLayout()

        # Заголовок
        self.title_label = QLabel("Определение реализационной цены продукции растениеводства")
        self.title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(self.title_label)

        # 1. Тип культуры (выпадающий список)
        layout.addWidget(QLabel("Тип культуры:"))
        self.culture_combo = QComboBox()
        self.culture_combo.addItems(["Ячмень", "Озимая пшеница", "Подсолнечник"])
        layout.addWidget(self.culture_combo)

        # 2. Производственная себестоимость 1 ц, тыс. руб.
        layout.addWidget(QLabel("Производственная себестоимость 1 ц, тыс. руб.:"))
        self.cost_input = QLineEdit()
        layout.addWidget(self.cost_input)

        # 3. Объем реализации, ц (не используется в формуле, но оставим)
        layout.addWidget(QLabel("Объем реализации, ц:"))
        self.volume_input = QLineEdit()
        layout.addWidget(self.volume_input)

        # 4. Аренда торговой точки, тыс. руб.
        layout.addWidget(QLabel("Аренда торговой точки, тыс. руб.:"))
        self.rent_input = QLineEdit()
        layout.addWidget(self.rent_input)

        # 5. Заработная плата продавцам, тыс. руб.
        layout.addWidget(QLabel("Заработная плата продавцам, тыс. руб.:"))
        self.salary_input = QLineEdit()
        layout.addWidget(self.salary_input)

        # 6. Маркетинговые расходы, тыс. руб.
        layout.addWidget(QLabel("Маркетинговые расходы, тыс. руб.:"))
        self.marketing_input = QLineEdit()
        layout.addWidget(self.marketing_input)

        # Кнопка "Рассчитать страховые взносы"
        self.btn_insurance = QPushButton("Рассчитать страховые взносы")
        self.btn_insurance.clicked.connect(self.calc_insurance)
        layout.addWidget(self.btn_insurance)

        # Поле для вывода страховых взносов
        layout.addWidget(QLabel("Страховые взносы, тыс. руб.:"))
        self.insurance_output = QLineEdit()
        self.insurance_output.setReadOnly(True)
        layout.addWidget(self.insurance_output)

        # Кнопка "Рассчитать цену реализации"
        self.btn_price = QPushButton("Рассчитать цену реализации")
        self.btn_price.clicked.connect(self.calc_price)
        layout.addWidget(self.btn_price)

        # Поле для вывода цены реализации
        layout.addWidget(QLabel("Цена реализации, тыс. руб./ц:"))
        self.price_output = QLineEdit()
        self.price_output.setReadOnly(True)
        layout.addWidget(self.price_output)

        # Кнопка "Сравнить с плановой ценой" (гистограмма)
        self.btn_compare = QPushButton("Сравнить с плановой ценой")
        self.btn_compare.clicked.connect(self.compare_price)
        layout.addWidget(self.btn_compare)

        self.setLayout(layout)

        # Переменная для хранения последней рассчитанной цены
        self.last_price = None

    # Вспомогательная функция для получения числа из поля ввода
    def get_float(self, line_edit, field_name):
        try:
            value = float(line_edit.text())
            return value
        except ValueError:
            QMessageBox.warning(self, "Ошибка ввода", f"Поле '{field_name}' должно содержать число.")
            return None

    # Расчет страховых взносов (30% от зарплаты)
    def calc_insurance(self):
        salary = self.get_float(self.salary_input, "Заработная плата продавцам")
        if salary is None:
            return
        insurance = salary * 0.30
        self.insurance_output.setText(f"{insurance:.2f}")

    # Расчет цены реализации
    def calc_price(self):
        # Получаем все необходимые значения
        cost = self.get_float(self.cost_input, "Производственная себестоимость 1 ц")
        if cost is None:
            return
        rent = self.get_float(self.rent_input, "Аренда торговой точки")
        if rent is None:
            return
        salary = self.get_float(self.salary_input, "Заработная плата продавцам")
        if salary is None:
            return
        marketing = self.get_float(self.marketing_input, "Маркетинговые расходы")
        if marketing is None:
            return

        # Страховые взносы (могут быть ещё не нажаты, но по логике их нужно рассчитать)
        insurance_text = self.insurance_output.text()
        if not insurance_text:
            QMessageBox.warning(self, "Предупреждение", "Сначала рассчитайте страховые взносы!")
            return
        try:
            insurance = float(insurance_text)
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Не удалось получить страховые взносы.")
            return

        # Определяем процент наценки в зависимости от культуры
        culture = self.culture_combo.currentText()
        markup_percent = {
            "Ячмень": 50,
            "Озимая пшеница": 35,
            "Подсолнечник": 45
        }.get(culture, 0)

        # Формула: (себестоимость + (аренда + зарплата + страховые + маркетинг)) * (1 + наценка/100)
        total_costs = cost + (rent + salary + insurance + marketing)
        price = total_costs * (1 + markup_percent / 100.0)

        self.last_price = price
        self.price_output.setText(f"{price:.2f}")

    # Сравнение с плановой ценой (гистограмма)
    def compare_price(self):
        if self.last_price is None:
            QMessageBox.warning(self, "Нет данных", "Сначала рассчитайте цену реализации.")
            return

        # Запрашиваем плановую цену у пользователя
        planned_price, ok = QInputDialog.getDouble(
            self, "Плановая цена", "Введите плановую цену (тыс. руб./ц):", decimals=2
        )
        if not ok:
            return

        # Строим гистограмму в отдельном окне
        self.show_histogram(self.last_price, planned_price)

    def show_histogram(self, actual, planned):
        # Создаём окно с графиком
        dialog = QWidget()
        dialog.setWindowTitle("Сравнение цен")
        dialog.setGeometry(200, 200, 500, 400)
        layout = QVBoxLayout()

        figure = Figure(figsize=(5, 4), dpi=100)
        canvas = FigureCanvas(figure)
        layout.addWidget(canvas)

        ax = figure.add_subplot(111)
        categories = ['Фактическая цена', 'Плановая цена']
        values = [actual, planned]
        colors = ['#2e7d32', '#1976d2']
        bars = ax.bar(categories, values, color=colors)
        ax.set_ylabel('Цена, тыс. руб./ц')
        ax.set_title('Сравнение фактической и плановой цены')

        # Подписи значений на столбцах
        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                    f'{val:.2f}', ha='center', va='bottom')

        canvas.draw()
        dialog.setLayout(layout)
        dialog.show()
        # Сохраняем ссылку, чтобы окно не закрылось сразу
        self.histogram_window = dialog


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
