from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QGridLayout, QLabel,
                             QSpinBox)
from PyQt5.QtCore import pyqtSignal
from enum import IntEnum, auto
from src.config import config
from src.utils.Box import Box

class ScreenshooterGUI(QWidget):

    # Signals
    take_screenshot = pyqtSignal()
    close_screenshot = pyqtSignal()
    selection_changed = pyqtSignal(Box)

    def __init__(self):
        super().__init__()
        self.initGUI()

    def initGUI(self):
        '''
        Initialise the gui for the screenshooter.
        It consists of buttons for creating and closing screenshots
        as well as changing the selection of the screen.
        '''
        self.layout = QVBoxLayout()

        # Buttons for taking and closing screenshots
        screenshot_layout = QHBoxLayout()
        self.button_screenshot = QPushButton('Capture', self)
        self.button_screenshot.clicked.connect(self.on_take_screenshot)
        self.button_close_screenshot = QPushButton('Close', self)
        self.button_close_screenshot.clicked.connect(self.on_close_screenshot)
        screenshot_layout.addWidget(self.button_screenshot)
        screenshot_layout.addWidget(self.button_close_screenshot)
        self.layout.addLayout(screenshot_layout)

        # Menu for changing the screenshot selection
        grid_layout = QGridLayout()
        self.label_position = QLabel('Position(x,y)')
        self.field_left = QSpinBox(self)
        self.field_top = QSpinBox(self)
        self.label_size = QLabel('Size(w,h)')
        self.field_width = QSpinBox(self)
        self.field_height = QSpinBox(self)
        self.field_left.setRange(0, config['monitor']['width'])
        self.field_top.setRange(0, config['monitor']['height'])
        self.field_width.setRange(0, config['monitor']['width'])
        self.field_height.setRange(0, config['monitor']['height'])
        self.field_left.valueChanged.connect(self.on_change_selection)
        self.field_top.valueChanged.connect(self.on_change_selection)
        self.field_width.valueChanged.connect(self.on_change_selection)
        self.field_height.valueChanged.connect(self.on_change_selection)
        grid_layout.addWidget(self.label_position, 0, 0)
        grid_layout.addWidget(self.field_left, 0, 1)
        grid_layout.addWidget(self.field_top, 0, 2)
        grid_layout.addWidget(self.label_size, 1, 0)
        grid_layout.addWidget(self.field_width, 1, 1)
        grid_layout.addWidget(self.field_height, 1, 2)
        self.layout.addLayout(grid_layout)

        self.setLayout(self.layout)

    def on_change_selection(self):
        '''
        Send a signal to the Screenshooter when the selection is changed through the spin
        boxes in the gui.
        '''
        # Get the selection coordinates from the spin boxes.
        selection = Box(int(self.field_left.text()),
                        int(self.field_top.text()),
                        int(self.field_width.text()),
                        int(self.field_height.text()))

        # Emit a signal to the Screenshooter with the new selection.
        self.selection_changed.emit(selection)

    def on_take_screenshot(self):
        '''
        Capture the screen.
        '''
        self.take_screenshot.emit()


    def on_close_screenshot(self):
        '''
        Close the captured screenshot
        '''
        self.close_screenshot.emit()