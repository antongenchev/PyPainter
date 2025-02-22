import cv2
import numpy as np
from typing import List, Union
import copy
from src.DrawableElement import DrawableElement

class Layer:
    def __init__(self, image=None, visible=True):
        self.image = image # The starting image on which we draw
        self.final_image = copy.deepcopy(image)
        self.visible = visible # Is the layer visible
        self.drawing_enabled = False
        self.elements:List[DrawableElement] = []

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

