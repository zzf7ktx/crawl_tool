from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QLabel,
    QComboBox,
)
from PyQt6.QtGui import QIntValidator
from PyQt6 import QtCore
import getopt
import sys
from etsy import crawl as etsyCrawl, isEtsy
from woo import crawl as wooCrawl, isWoo
import os
import json
import generative_ai as ai
import helper as hp


# Define a subclass of QRunnable that wraps the function
class MyRunnable(QtCore.QRunnable):
    def __init__(self, func):
        super().__init__()
        self.func = func

    def run(self):
        self.func()


class ScrapperWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.url = QLineEdit()
        self.expected_total = QLineEdit()
        self.expected_total.setValidator(QIntValidator())
        self.button = QPushButton("Start")

        thread_pool = QtCore.QThreadPool()
        self.button.clicked.connect(lambda: self.create_runnable(thread_pool))

        self.output = QLabel()
        self.output.setText("")

        self.setWindowTitle("Generate")
        self.setFixedWidth(200)
        self.setFixedHeight(200)
        self.combo_box = QComboBox()

        for element in os.listdir("result"):
            if os.path.isdir(os.path.join("result", element)):
                self.combo_box.addItem(element)
        self.layout = QVBoxLayout()
        self.layout.addWidget(QLabel(text="Choose folder"))
        self.layout.addWidget(self.combo_box)
        self.layout.addWidget(self.button)
        self.layout.addWidget(self.output)
        self.setLayout(self.layout)

    def func(self):
        self.output.setText("Starting...")
        path = self.combo_box.currentText()
        try:
            with open(f"result/{path}/products.json") as user_file:
                json_string = user_file.read()
                products = json.loads(json_string)
                self.output.setText("Generating...")
                re_products = ai.generate_title_and_description(products)
                hp.array_to_json(re_products, "re_products")
                self.output.setText("Done")
        except Exception as ex:
            print(ex)
            self.output.setText("Error")

    def create_runnable(self, thread_pool):
        runnable = MyRunnable(self.func)
        thread_pool.start(runnable)


argument_list = sys.argv[1:]
# Options
options = "hp:o:"
# Long options
long_options = ["headless", "path=", "output="]

try:
    # Parsing argument
    arguments, values = getopt.getopt(argument_list, options, long_options)
    headless = False
    path = ""
    output = "re_products"

    # Checking each argument
    print(arguments)
    for currentArgument, currentValue in arguments:
        if currentArgument in ("--headless"):
            headless = True
        elif currentArgument in ("-p", "--path"):
            path = currentValue
        elif currentArgument in ("-o", "--output"):
            output = currentValue

    if headless:
        print("Starting...")
        try:
            with open(f"result/{path}/products.json") as user_file:
                json_string = user_file.read()
                products = json.loads(json_string)
                print("Generating...")
                re_products = ai.generate_title_and_description(products)
                hp.array_to_json(re_products, output)
                print("Done")
        except Exception as ex:
            print(ex)

    else:
        # Create an application instance
        app = QApplication([])
        widget = ScrapperWidget()
        widget.show()
        sys.exit(app.exec())

except getopt.error as err:
    # output error, and return with an error code
    print(str(err))
