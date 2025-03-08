from PyQt5.QtWidgets import QFileDialog
from src.MenuBar.MenuBarGUI import MenuBarGUI
from src.config import WITHGUI
from typing import Callable
import cv2


class MenuBar:

    # Callbacks that have to be provided
    callback_update_image: Callable = lambda image: None


    ####################################

    def __init__(self):

        if WITHGUI:
            self.gui = MenuBarGUI()
            self.connect_signals()

    def connect_signals(self):
        '''
        Connect the signals from the MenuBarGUI
        '''
        self.gui.load_image_signal.connect(self.load_image)
        # self.gui.save_image_signal.connect()
        # self.gui.manage_plugins_signal.connect()

    def load_image(self):
        """
        Opens a file dialog to load an image and updates the zoomable widget.
        """
        # Open a file dialog
        file_path, _ = QFileDialog.getOpenFileName(None, "Open Image", "", 
                                                   "Images (*.png *.jpg *.jpeg *.bmp *.tiff *.webp)")

        if not file_path:
            return # User canceled file selection
        
        # Load the image using OpenCV
        image = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)

        if image is None:
            return
        
        self.callback_update_image(image)