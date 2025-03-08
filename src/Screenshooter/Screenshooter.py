from PyQt5.QtCore import pyqtSignal
from src.Screenshooter.ScreenshooterGUI import ScreenshooterGUI
from mss import mss
import cv2
import numpy as np
from typing import Callable
from src.utils.Box import Box
from src.Screenshooter.TransparentWindow import TransparentWindow
from src.config import config


class Screenshooter:

    # image_singal is the signal going to be emitted when a new
    # screenshot selection is captured. It sends the image in cv2
    # format.
    image_signal = pyqtSignal(object) # object is np.ndarray

    def __init__(self, callback_capture: Callable = None):
        # The transparent window with a screenshot
        self.transparent_window: TransparentWindow = None

        # Define the callback that will be executed when there is
        # a new capture. The new image/capture will be passed
        # to the callback.
        self.callback_capture = callback_capture

        self.gui = ScreenshooterGUI()
        self.connect_signals()

    def connect_signals(self):
        '''
        Connect the signals from the GUI to methods of this class.
        '''
        self.gui.take_screenshot.connect(self.take_screenshot)
        self.gui.close_screenshot.connect(self.close_screenshot)
        self.gui.selection_changed.connect(self.change_selection)

    def close(self):
        '''
        React to the application being closed by cosing the transparent window
        '''
        if self.transparent_window:
            self.transparent_window.close()

    def take_screenshot(self):
        '''
        Open a transparent window with the screenshot
        '''
        with mss() as sct:
            screenshot = sct.grab({'left': 0, 'top': 0, 'width': 1920, 'height': 1080})
            self.screenshot_image = cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGRA2BGR) # convert to opencv image
            cv2.imwrite(config['paths']['screenshot_background'], self.screenshot_image)

        # Open a window with the background being the screenshot
        self.transparent_window = TransparentWindow()
        self.transparent_window.show()

        # Connect the signal from the DraggableBox for screenshot selection (tracks any movement)
        self.transparent_window.draggable_widget.signal_selection_change_light.connect(self.update_selection)
        self.transparent_window.signal_selection_change.connect(self.update_selection)

        # Connect the signal from the TransparentWindow to get updates of the selection (not while dragging/resizing)
        self.transparent_window.signal_selection_change.connect(self.capture_image)

    def close_screenshot(self):
        '''
        Close the screenshot i.e. close the transparent window.
        '''
        if self.transparent_window:
            self.transparent_window.close()
            self.transparent_window = None

    def change_selection(self, selection: Box):
        '''
        Handle change of the selection via the ScreenshooterGUI.
        '''
        selection = Box(int(self.gui.field_left.text()),
                        int(self.gui.field_top.text()),
                        int(self.gui.field_width.text()),
                        int(self.gui.field_height.text()))
        # Send the selection to the TransparentWindow
        self.transparent_window.on_change_selection_from_screenshot_app(selection)
        # Update the image in the Zoomable label in PyPainter
        self.capture_image()

    def update_selection(self):
        '''
        Update the selection when it is being hcanged from a place that is not the gui. This allows for
        the selection to be changed from the TransparentWindow.
        '''
        # Block signals to prevent triggering on_change_selection when programmatically updating values
        self.gui.field_left.blockSignals(True)
        self.gui.field_top.blockSignals(True)
        self.gui.field_width.blockSignals(True)
        self.gui.field_height.blockSignals(True)
        # Update the Position and Size fields
        selection = self.transparent_window.draggable_widget.selection
        self.gui.field_left.setValue(selection.left)
        self.gui.field_top.setValue(selection.top)
        self.gui.field_width.setValue(selection.width)
        self.gui.field_height.setValue(selection.height)
        # Unblock signals after the programmatic update
        self.gui.field_left.blockSignals(False)
        self.gui.field_top.blockSignals(False)
        self.gui.field_width.blockSignals(False)
        self.gui.field_height.blockSignals(False)

    def capture_image(self):
        '''
        Capture the screenshot based on current selection and update the QLabel with the image
        Update the screenshot that is showing in the QLabel element for the creenshot based on the selection 
        '''
        try:
            selection = self.transparent_window.draggable_widget.selection
            image = self.screenshot_image[selection.top : selection.top + selection.height,
                                          selection.left : selection.left + selection.width]
            if self.callback_capture is not None:
                self.callback_capture(image)
            return image
        except:
            return None