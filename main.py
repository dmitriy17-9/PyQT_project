import sqlite3
import sys
from PyQt5 import uic
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QApplication, QTableWidgetItem, QMessageBox, QDialog
from data.database import db_connect, category, db_show_table_expenses, expenses, db_delete_row, db_update_row

con, cur = db_connect()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('data/designs/expenses.ui', self)
        self.setWindowTitle('Контроль расходов')

        self.spend_money = 0
        self.remains = 0
        self.money = []

        self.show_table()
        self.calc()

        self.expenses.itemChanged.connect(self.item_changed)
        self.add_btn.clicked.connect(self.add_row_expenses)
        self.delete_btn.clicked.connect(self.delete_row)

        self.modified = {}
        self.titles = []

    def calc(self):
        self.money = expenses()

        self.spend_money = str(sum(self.money))
        self.spend_money_line.setText(self.spend_money)

        if self.remain_line.text() == '':
            self.remain_line.setText('0')
        self.remains = self.max_money_line.text()

        self.max_money_line.textChanged.connect(self.remain_line.setText)

        if not self.money:
            self.average_line.setText('0')
        else:
            self.average_line.setText(str(sum(self.money) // len(self.money)))

    def show_table(self):
        result1 = db_show_table_expenses()

        self.expenses.setRowCount(len(result1))
        self.expenses.setColumnCount(3)
        self.expenses.setColumnWidth(0, 0)
        self.expenses.setColumnWidth(1, 215)
        self.expenses.setHorizontalHeaderLabels(("", "Категория", "Цена"))
        self.titles = ['id', 'product', 'expenditure']
        for i, elem in enumerate(result1):
            self.expenses.setItem(i, 0, QTableWidgetItem(str(result1[i]['id'])))
            self.expenses.setItem(i, 1, QTableWidgetItem(result1[i]['product']))
            self.expenses.setItem(i, 2, QTableWidgetItem(str(result1[i]['expenditure'])))
        self.modified = {}

    def add_row_expenses(self):
        self.add_dialog = AddDialog()
        if self.add_dialog.exec() == QDialog.Rejected:
            return
        self.category1 = self.add_dialog.comboBox.currentText()
        self.cost1 = self.add_dialog.cost_line.text()
        self.que1 = f'INSERT INTO expenses(product, expenditure) VALUES("{self.category1}", {self.cost1})'
        cur = con.cursor()
        cur.execute(self.que1)
        con.commit()
        r = cur.execute("SELECT expenditure FROM expenses").fetchall()

        self.show_table()
        self.calc()

    def delete_row(self):
        # Получаем список элементов без повторов и их id
        rows = list(set([i.row() for i in self.expenses.selectedItems()]))
        ids = [self.expenses.item(i, 0).text() for i in rows]
        print(rows, ids)
        # Спрашиваем у пользователя подтверждение на удаление элементов
        valid = QMessageBox.question(
            self, '', "Действительно удалить элементы с id " + ",".join(ids),
            QMessageBox.Yes, QMessageBox.No)
        # Если пользователь ответил утвердительно, удаляем элементы.
        if valid == QMessageBox.Yes:
            db_delete_row(ids)

        # обновляем tableWidget
        self.show_table()
        self.calc()

    def item_changed(self, item):
        self.modified["id"] = self.expenses.item(item.row(), 0).text()
        # Если значение в ячейке было изменено,
        # то в словарь записывается пара: название поля, новое значение
        self.modified[self.titles[item.column()]] = item.text()
        self.save_results()
        self.calc()

    def save_results(self):
        if self.modified and any(key for key in self.modified.keys() if key != "id"):
            db_update_row(self.modified)
            self.modified.clear()
        self.calc()


class AddDialog(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('data/designs/add.ui', self)

        self.setWindowTitle('Добавить новый расход')

        self.accepted.connect(self.run)
        self.buttonBox.rejected.connect(self.reject)

        self.comboBox.addItems(category())

    def run(self):
        pass


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('data/icon.jpg'))
    ex = MainWindow()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
