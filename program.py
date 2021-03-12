import sqlite3
import sys

from PyQt5 import uic
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QApplication, QTableWidgetItem, QMessageBox, QDialog

categories = []

con = sqlite3.connect("money_db.sqlite")

cur = con.cursor()
res = cur.execute('SELECT product_name FROM categories')
for i in res:
    categories.append(*i)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('designs/expenses.ui', self)

        self.tableWidget.itemChanged.connect(self.item_changed)
        self.update_btn.clicked.connect(self.update_result)
        self.add_btn.clicked.connect(self.add_row)
        self.delete_btn.clicked.connect(self.delete_elem)

        self.tableWidget2.itemChanged.connect(self.item_changed2)
        self.update_btn2.clicked.connect(self.update_result2)
        self.add_btn2.clicked.connect(self.add_row2)
        self.deletebtn.clicked.connect(self.delete_elem2)

        self.max_money_line.textChanged.connect(self.remain_line.setText)

        self.setWindowTitle('Контроль расходов')
        self.setFixedSize(750, 650)

        self.modified = {}
        self.titles = None
        self.modified2 = {}
        self.titles2 = None

        self.spend_money = 0
        self.remains = 0
        self.average = []

        self.category1 = ''
        self.cost1 = ''
        self.que1 = ''
        self.category2 = ''
        self.que2 = ''

        self.spend_money_line.setText(str(self.spend_money))

        if self.remains != 0:
            self.remains = self.max_money_line.text()
        self.remain_line.setText(str(self.remains))

        if len(self.average) > 0:
            self.average_line.setText(str(sum(self.average) // len(self.average)))
        else:
            self.average_line.setText('0')

    def update_result(self):
        cur = con.cursor()
        result = cur.execute("SELECT product, expenditure FROM expenses").fetchall()
        r = cur.execute("SELECT expenditure FROM expenses").fetchall()
        for i in r:
            print(i[0])
            self.spend_money = int(self.spend_money) + i[0]
            self.spend_money_line.setText(str(self.spend_money))

            if self.remains != 0:
                self.remains = int(self.remains) - i[0]
            self.remain_line.setText(str(self.remains))

            self.average.append(i[0])
            if len(self.average) > 0:
                self.average_line.setText(str(sum(self.average) // len(self.average)))
            else:
                self.average_line.setText('0')
        self.tableWidget.setRowCount(len(result))
        if not result:
            self.statusBar().showMessage('Ничего не нашлось')
            return
        else:
            self.statusBar().showMessage(f"Нашлась запись")
        self.tableWidget.setColumnCount(len(result[0]))
        self.titles = [description[0] for description in cur.description]
        for i, elem in enumerate(result):
            for j, val in enumerate(elem):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(val)))
        self.modified = {}

    def item_changed(self, item):
        self.modified[self.titles[item.column()]] = item.text()

    def add_row(self):
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

    def delete_elem(self):
        rows = list(set([i.row() for i in self.tableWidget.selectedItems()]))
        ids = [self.tableWidget.item(i, 0).text() for i in rows]
        ids1 = [self.tableWidget.item(i, 1).text() for i in rows]
        valid = QMessageBox.question(
            self, '', "Действительно удалить элементы?",
            QMessageBox.Yes, QMessageBox.No)
        if valid == QMessageBox.Yes:
            cur = con.cursor()
            id = cur.execute(f"SELECT id FROM expenses WHERE product = '{ids[0]}' "
                             f"and expenditure = {ids1[0]}").fetchall()
            id = id[0][0]
            r = cur.execute(f"DELETE FROM expenses WHERE id = '{id}'")
            if not r:
                self.statusBar().showMessage('Запись не удалена')
                return
            else:
                cur.execute(f"DELETE FROM expenses WHERE id = '{id}'")
                self.statusBar().showMessage('Запись была удалена')
            con.commit()
        for i in r:
            self.spend_money = int(self.spend_money) - i[0]
            self.spend_money_line.setText(str(self.spend_money))

            if self.remains != 0:
                self.remains = self.max_money_line.text()
            self.remains = int(self.remains) + i[0]
            self.remain_line.setText(str(self.remains))

            self.average.remove(i[0])
            if len(self.average) > 0:
                self.average_line.setText(str(sum(self.average) // len(self.average)))
            else:
                self.average_line.setText('0')

    def update_result2(self):
        cur = con.cursor()
        result2 = cur.execute("SELECT product_name FROM categories").fetchall()
        self.tableWidget2.setRowCount(len(result2))
        if not result2:
            self.statusBar().showMessage('Ничего не нашлось')
            return
        else:
            self.statusBar().showMessage(f"Нашлась запись")
        self.tableWidget2.setColumnCount(len(result2[0]))
        self.titles2 = [description[0] for description in cur.description]
        for i, elem in enumerate(result2):
            for j, val in enumerate(elem):
                self.tableWidget2.setItem(i, j, QTableWidgetItem(str(val)))
        self.modified2 = {}

    def item_changed2(self, item):
        self.modified2[self.titles2[item.column()]] = item.text()

    def add_row2(self):
        self.add_dialog2 = AddDialog2()
        if self.add_dialog2.exec() == QDialog.Rejected:
            return
        elif self.add_dialog2.exec() == QDialog.Accepted:
            self.category2 = self.add_dialog2.line.text()
            print(self.category2)
            self.que2 = f'INSERT INTO categories(product_name) VALUES("{self.category2}")'
            cur = con.cursor()
            cur.execute(self.que2)
            con.commit()

    def delete_elem2(self):
        rows2 = list(set([i.row() for i in self.tableWidget.selectedItems()]))
        ids2 = [self.tableWidget.item(i, 0).text() for i in rows2]
        valid = QMessageBox.question(
            self, '', "Действительно удалить элементы?",
            QMessageBox.Yes, QMessageBox.No)
        if valid == QMessageBox.Yes:
            cur = con.cursor()
            id = cur.execute(f"SELECT id FROM categories WHERE product_name = '{ids2[0]}'").fetchall()
            id = id[0][0]
            r = cur.execute(f"DELETE FROM categories WHERE id = '{id}'")
            if not r:
                self.statusBar().showMessage('Запись не удалена')
                return
            else:
                cur.execute(f"DELETE FROM categories WHERE id = '{id}'")
                self.statusBar().showMessage('Запись была удалена')
            con.commit()


class AddDialog(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('designs/add.ui', self)

        self.setWindowTitle('Добавить новый расход')

        self.accepted.connect(self.run)
        self.buttonBox.rejected.connect(self.reject)

        self.comboBox.addItems(categories)

    def run(self):
        pass


class AddDialog2(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('designs/add2.ui', self)

        self.setWindowTitle('Добавить новую категорию')

        self.accepted.connect(self.run2)
        self.buttonBox_2.rejected.connect(self.reject)

    def run2(self):
        pass


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('icon.jpg'))
    ex = MainWindow()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
