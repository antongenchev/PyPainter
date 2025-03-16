from PyQt5.QtCore import pyqtSignal, QObject
import numpy as np
from typing import List, Union
import copy
from src.DrawableElement import DrawableElement
from src.Layers.ElementListGUI import ElementListGUI

class Layer(QObject):

    _id_counter = 0 # Class variable to ensure unique IDs.

    # Signals
    layer_image_updated = pyqtSignal()

    def __init__(self, image=None, visible=True):
        super().__init__()
        self.image = image # The starting image on which we draw
        self._final_image = copy.deepcopy(image)
        self.visible = visible # Is the layer visible
        self.drawing_enabled = False
        self.elements:List[DrawableElement] = []

        # Assign a unqiue id to the layer
        self.id = Layer._id_counter
        Layer._id_counter += 1

        self.gui = ElementListGUI()

    @property
    def final_image(self) -> np.ndarray:
        return self._final_image

    @final_image.setter
    def final_image(self, value):
        self._final_image = value

        # Send a signal notifying that the image has been changed
        self.layer_image_updated.emit()

    def set_as_active(self) -> None:
        """
        There is one active layer, i.e. the layer that we are
        currently working on. This method sets the Layer as the active
        layer and tries to shows its ElementListGUI.
        """
        self.gui.set_as_active()

    def set_as_inactive(self) -> None:
        """Set the layer as inactive and try ot hide its ElementListGUI."""
        self.gui.set_as_inactive()

    def toggle_visibility(self):
        self.visible = not self.visible

    def add_element(self, element:DrawableElement):
        '''
        Add a new element to the layer. Put it at the top of the layer.
        Update the final image of the layer

        Parameters:
            element: the drawable element to be added
        '''
        self.elements.append(element) # add the drawable element

        # Inform the GUI about the added element
        self.gui.add_element_in_gui(element)

    def remove_element(self, index:int) -> None:
        if 0 <= index < len(self.elements):
            del self.elements[index]

    def get_elements(self:DrawableElement) -> List[DrawableElement]:
        return self.elements

    def get_element_index(self, element:DrawableElement) -> Union[int, None]:
        '''
        Given a drawable element return the index of the element in the list of element

        Parameters:
            element - the drawable element
        Retruns: the index of the drawable element
        '''
        for i in range(len(self.elements)):
            if element is self.elements[i]:
                return i

    def get_touched_element(self, x:int, y:int, r:int) -> DrawableElement:
        '''
        Parameters:
            x - the x coordinate
            y - the y coordinate
            r - the radius around (x, y)
        Returns:
            DrawablElement: return the topmost drawable element that was clicked.
                If there is no such element return None
        '''
        for element in reversed(self.elements):
            if element.is_touched(x, y, r):
                return element

class FakeLayer(Layer):
    def __init__(self, image=None, visible=True):
        super().__init__(image, visible)

    def clear_final_image(self) -> None:
        '''
        Clears just the final_image of the layer. This is used when we have drawn
        directly to the final_image without modifying the actual contents of the layer
        '''
        self.final_image = np.zeros_like(self.final_image)

