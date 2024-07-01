from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QLabel,
    QCheckBox,
)
from PyQt6.QtGui import QIntValidator
from PyQt6 import QtCore
import sys
from etsy import crawl as etsyCrawl, isEtsy
from helper import to_shopify_template, array_to_json
from generative_ai import generate_title_and_description


# Define a subclass of QRunnable that wraps the function
class MyRunnable(QtCore.QRunnable):
    def __init__(self, func):
        super().__init__()
        self.func = func

    def run(self):
        # Call the function when the runnable is executed
        self.func()


# Define a custom widget class
class MyWidget(QWidget):
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
        self.auto_gen = QCheckBox("Generate title", self)
        self.auto_gen.setChecked(True)
        self.enable_shopify_transform = QCheckBox("To shopify", self)
        self.enable_shopify_transform.setChecked(True)

        self.layout = QVBoxLayout()
        self.layout.addWidget(QLabel(text="URL"))
        self.layout.addWidget(self.url)
        self.layout.addWidget(QLabel(text="Minimum"))
        self.layout.addWidget(self.expected_total)
        self.layout.addWidget(self.auto_gen)
        self.layout.addWidget(self.enable_shopify_transform)
        self.layout.addWidget(self.button)
        self.layout.addWidget(self.output)
        self.setLayout(self.layout)

    def create_runnable(self, thread_pool):
        runnable = MyRunnable(self.func)
        thread_pool.start(runnable)

    # Define the func that will take the value of the url input
    def func(self):
        self.output.setText("Determining engine...")
        # Get the text from the url input
        url_value = self.url.text().strip()
        expected_total = 2

        products = []
        path = ""
        if self.expected_total.text().isnumeric():
            expected_total = int(self.expected_total.text())
        if isEtsy(url_value):
            self.output.setText("Done determination. Starting Etsy.")
            products, path = etsyCrawl(url_value, expected_total)
        else:
            self.output.setText("Done determination. Not support.")
            print("Not support")

        if self.auto_gen.isChecked():
            products = generate_title_and_description(products)
            array_to_json(products, "re_products")

        if self.enable_shopify_transform.isChecked():
            to_shopify_template(products, True, f"{path}/shopify_products")
        self.output.setText("Scrapping Done.")


# Create an application instance
app = QApplication(sys.argv)
# Create and show the widget
widget = MyWidget()
widget.show()
sys.exit(app.exec())
