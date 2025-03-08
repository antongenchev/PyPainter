from src.PyPainter import PyPainter
from PyQt5.QtWidgets import QApplication
import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

if __name__ == '__main__':
    Qapp = QApplication(sys.argv)
    app = PyPainter()
    app.show()
    sys.exit(Qapp.exec_())
