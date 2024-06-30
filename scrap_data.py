from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QLabel,
)
from PyQt6.QtGui import QIntValidator
from PyQt6 import QtCore
import getopt
import sys
from etsy import crawl as etsyCrawl, isEtsy


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

        self.layout = QVBoxLayout()
        self.layout.addWidget(QLabel(text="URL"))
        self.layout.addWidget(self.url)
        self.layout.addWidget(QLabel(text="Minimum"))
        self.layout.addWidget(self.expected_total)
        self.layout.addWidget(self.button)
        self.layout.addWidget(self.output)
        # self.layout.addWidget(self.selection)
        # Set the layout for the widget
        self.setLayout(self.layout)

    def func(self):
        self.output.setText("Determining engine...")
        # Get the text from the url input
        url_value = self.url.text().strip()
        expected_total = 2
        if self.expected_total.text().isnumeric():
            expected_total = int(self.expected_total.text())
        if isEtsy(url_value):
            self.output.setText("Done determination. Starting Etsy")
            etsyCrawl(url_value, expected_total)
        else:
            self.output.setText("Done determination. Not support.")

        self.output.setText("Scrapping Done.")

    def create_runnable(self, thread_pool):
        runnable = MyRunnable(self.func)
        thread_pool.start(runnable)


argument_list = sys.argv[1:]
# Options
options = "hu:f:o:m:"
# Long options
long_options = ["headless", "urls=" "input-file=", "minimum-total=", "output="]

try:
    # Parsing argument
    arguments, values = getopt.getopt(argument_list, options, long_options)
    headless = False
    urls = []
    file_url = ""
    output = ""
    minimum_total = 2

    # Checking each argument
    print(arguments)
    for currentArgument, currentValue in arguments:
        if currentArgument in ("--headless"):
            headless = True
        elif currentArgument in ("-f", "--input-file"):
            file_url = currentValue
        elif currentArgument in ("-o", "--output"):
            output = currentValue
        elif currentArgument in ("--urls"):
            urls = currentValue.split(";")
        elif currentArgument in ("--minimum-total"):
            minimum_total = int(currentValue)

    if headless:
        if file_url != "":
            with open(file_url, "r") as file:
                content = file.read()
            urls = content.split("\n")

        for url in urls:
            print(f"Scrapping: {url}")
            print("Determining engine...")
            if isEtsy(url):
                print("Done determination. Starting Etsy")
                etsyCrawl(url, minimum_total)
            else:
                print("Not support")

    else:
        # Create an application instance
        app = QApplication([])
        widget = ScrapperWidget()
        widget.show()
        sys.exit(app.exec())


except getopt.error as err:
    # output error, and return with an error code
    print(str(err))
