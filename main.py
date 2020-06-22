import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QLineEdit
import vk_parser as vk
import time

def set_text(label, text):
    label.setText(text)


def window():
    app = QApplication(sys.argv)
    widget = QWidget()

    button1 = QPushButton(widget)
    button1.setText("Запустить")
    button1.move(64, 32)
    button1.clicked.connect(button1_clicked)

    button2 = QPushButton(widget)
    button2.setText("Выйти")
    button2.move(64, 64)
    button2.clicked.connect(button2_clicked)

    global label1
    label1 = QLabel(widget)
    label1.setText("Программа не запущена")
    label1.move(150,150)

    global label2
    label2 = QLineEdit(widget)
    label2.move(300,100)

    widget.setGeometry(450, 250, 800, 600)
    widget.setWindowTitle("PyQt5 Button Click Example")
    widget.show()
    sys.exit(app.exec_())


def button1_clicked():
    set_text(label2, "aaa")
    print("hello")
    global vk_auto
    vk_parse()

def button2_clicked():
    exit()

def vk_parse():
    vk_auto = vk.autorize()
    sort_cities_list, sort_population_list = vk.sort_cities_dict(vk.cities_list(vk.users_list(vk.create_groups_list())))
    vk.marker_map(vk.create_coors_array(sort_cities_list), sort_population_list, vk.open_map())

if __name__ == '__main__':
    window()