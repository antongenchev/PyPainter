from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog
from PyQt5.QtCore import pyqtSignal
from src.ZoomableWidget import ZoomableWidget
from src.ImageProcessor import ImageProcessor
from src.ImageProcessingToolSetting import ImageProcessingToolSetting
from src.Screenshooter.mediator import ScreenshooterMediator
from src.MenuBar.mediator import MenuBarMediator
from mss import mss
import cv2
import numpy as np
from src.config import *

class PyPainter(QWidget):

    # Signals
    close_application_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.zoomable_widget = ZoomableWidget(self)
        self.tool_settings_widget = ImageProcessingToolSetting()
        self.image_processor = ImageProcessor(self.zoomable_widget, self.tool_settings_widget)
        self.screenshooter = ScreenshooterMediator(self)
        self.menu_bar = MenuBarMediator(self)

        self.zoomable_widget.zoomable_label.draw_signal.connect(self.image_processor.on_mouse_move)
        self.zoomable_widget.zoomable_label.start_draw_signal.connect(self.image_processor.on_mouse_down)
        self.zoomable_widget.zoomable_label.stop_draw_signal.connect(self.image_processor.on_mouse_up)
        self.zoomable_widget.zoomable_label.new_image_signal.connect(self.image_processor.on_new_image)

        self.initGUI()

    def initGUI(self):
        '''
        Initialise the GUI
        '''
        self.layout = QVBoxLayout()
        self.setWindowTitle('Screenshot Taker')
        self.setGeometry(config['start_position']['left'],
                         config['start_position']['top'],
                         config['start_position']['width'],
                         config['start_position']['height'])


        # The MenuBar / Navbar on top of the app
        self.layout.setMenuBar(self.menu_bar.gui)

        # Label to display the image
        self.layout.addWidget(self.zoomable_widget)

        # Image Processor sublayout
        self.layout.addWidget(self.image_processor)

        self.layout.addWidget(self.tool_settings_widget)

        # Layer list GUI
        # self.layout.addWidget(self.image_processor.layer_list.gui)

        # Screenshooter GUI
        self.layout.addWidget(self.screenshooter.gui)

        h_layout2 = QHBoxLayout()
        self.button_save = QPushButton('Save', self)
        self.button_save.clicked.connect(self.on_save)
        h_layout2.addWidget(self.button_save)
        self.layout.addLayout(h_layout2)

        self.setLayout(self.layout)

    def on_save(self):
        try:
            with mss() as sct:
                screenshot = sct.grab({'left':self.transparent_window.draggable_widget.selection.left,
                                       'top':self.transparent_window.draggable_widget.selection.top,
                                       'width':self.transparent_window.draggable_widget.selection.width,
                                       'height':self.transparent_window.draggable_widget.selection.height})
                screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
                cv2.imwrite(config['paths']['screenshot_background'], screenshot)
        except Exception as e:
            print(e)

    def closeEvent(self, event):
        self.close_application_signal.emit()
        event.accept()

    def update_image(self, image: np.ndarray):
        '''
        Update the image in the zoomable_widget
        '''
        self.zoomable_widget.zoomable_label.setImage(image)