from pathlib import Path, PurePath
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QLabel,
    QFileDialog,
)
from PyQt6.QtGui import QIntValidator
import getopt
import sys
import json
from helper import to_shopify_template


class ScrapperWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.selected_file = ""
        self.url = QLineEdit()
        self.expected_total = QLineEdit()
        self.expected_total.setValidator(QIntValidator())
        self.button = QPushButton("Start")
        self.file_button = QPushButton("Choose file")

        self.file_button.clicked.connect(self.open_file_dialog)
        self.button.clicked.connect(lambda: self.func())

        self.output = QLabel()
        self.output.setText("")

        self.setWindowTitle("Generate")
        self.setFixedWidth(200)
        self.setFixedHeight(200)

        dialog = QFileDialog(self, "Select a File")
        dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        dialog.setNameFilter("*.json")

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.file_button)
        self.layout.addWidget(self.output)
        self.layout.addWidget(self.button)
        self.setLayout(self.layout)

    def func(self):
        self.output.setText("Processing...")
        path = Path(self.selected_file)
        folder_name = path.parent

        try:
            with open(self.selected_file) as user_file:
                json_string = user_file.read()
            products = json.loads(json_string)
            print(products)
            to_shopify_template(products, True, f"{folder_name}/shopify_products")
            self.output.setText("Done")
        except Exception as ex:
            print(ex)
            self.output.setText("Error")

    def open_file_dialog(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, "Select a File", "result", "*.json"
        )
        if filename:
            path = Path(filename)
            self.selected_file = str(path)
            self.output.setText(f"File: {self.selected_file}")


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
    output = "shopify_products"

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
        print("Processing...")
        path_ = Path(path)
        folder_name = path.parent

        try:
            with open(path) as user_file:
                json_string = user_file.read()
            products = json.loads(json_string)
            print(products)
            to_shopify_template(products, True, f"{folder_name}/shopify_products")
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
