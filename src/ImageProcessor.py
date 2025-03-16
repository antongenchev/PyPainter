from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt5.QtCore import pyqtSignal, QTimer
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import cv2
import numpy as np
from enum import IntEnum, auto
import importlib
import copy
from typing import List, Tuple
from scipy.interpolate import CubicSpline
from src.ZoomableLabel import ZoomableLabel
from src.ZoomableWidget import ZoomableWidget
from src.Layers.Layer import FakeLayer
from src.Layers.Layer import Layer
from src.Layers.LayerList import LayerList
from src.DrawableElement import DrawableElement
from src.config import config

from src.ImageProcessingToolSetting import ImageProcessingToolSetting
# Import ImageProcessingTools
from src.ImageProcessingTools.ImageProcessingTool import ImageProcessingTool
from src.ImageProcessingTools.ToolManager import ToolManager

class ImageProcessor(QWidget):

    # The available image processing tools
    class tools(IntEnum):
        move = 0
        pencil = auto()

    def __init__(self,
                 zoomable_widget:ZoomableWidget,
                 image_processing_tool_setting:ImageProcessingToolSetting):
        super().__init__()
        self.tool_manager = ToolManager(self)
        self.zoomable_widget = zoomable_widget
        self.zoomable_label = zoomable_widget.zoomable_label
        self.current_tool = None
        self.tool_classes = {}
        self.layer_list = LayerList()
        self.fake_layer:FakeLayer = None # layer for visualising stuff not part of what is drawn

        self.final_image = None # The final image after adding all the layers together
        self.canvas_shape: Tuple[int, int] = None # The shape of the layers, image, etc. but w/o 3rd term

        self.image_processing_tool_setting = image_processing_tool_setting

        # Load the Tools from the config file
        self.tool_manager.load_tools_from_config()

        # Connect the signals from different gui parts
        self.connect_signals()

        self.initUI()

    def initUI(self):
        layout = QHBoxLayout()
        layout.setSpacing(6)
        layout.setAlignment(Qt.AlignLeft) 

        # Generate the gui for the tools from the
        for tool_name in sorted(self.tool_manager.tools.keys(), key=lambda k: self.tool_manager.tools[k]['order']):
            tool_obj = self.tool_manager.tools[tool_name]['object']
            tool_widget = tool_obj.create_ui()
            layout.addWidget(tool_widget)

        self.setLayout(layout)

    def connect_signals(self):
        '''
        Connect the signals / events coming from GUI parts to methods of the image processort.
        '''
        self.layer_list.gui.layer_added.connect(self.add_layer)
        self.layer_list.gui.layer_visibility_toggled.connect(self.set_layer_visibility)
        self.layer_list.gui.layer_selected.connect(self.set_active_layer)
        self.layer_list.gui.layer_deleted.connect(self.delete_layer)
        self.layer_list.gui.layer_moved_to_top.connect(self.move_layer_to_top)
        self.layer_list.gui.layer_inserted_above.connect(lambda l: self.insert_empty_layer(l, True))
        self.layer_list.gui.layer_inserted_below.connect(lambda l: self.insert_empty_layer(l, False))

    def update_zoomable_label(self):
        '''
        Update the image shown in the zoomable label
        '''
        if self.fake_layer.visible:
            # If the fake layer is visible draw it on top
            final_image = self.overlay_images(self.final_image, self.fake_layer.final_image)
            self.zoomable_label.update_transformed_image(final_image)
        else:
            # If the fake layer is not visible display just the final image
            self.zoomable_label.update_transformed_image(self.final_image)

    ################
    # Handle tools #
    ################

    def set_tool(self, tool: ImageProcessingTool):
        # Disable the previous tool
        if self.current_tool is not None:
            self.current_tool.disable()

        self.current_tool = tool

        settings_ui = self.current_tool.create_settings_ui()
        self.image_processing_tool_setting.set_tool_settings_ui(settings_ui)

        # Reset the mouse to be released (bug fix)
        self.zoomable_label.mouse_pressed = False

    ##################
    # Handle signals #
    ##################

    def on_mouse_move(self, x:int, y:int):
        '''
        Handle signals from the ZoomableLabel.

        Parameters:
            x - the x coordinate of the event on the image
            y - the y coordinate of the event on the image
        '''
        self.current_tool.on_mouse_move(x, y)

    def on_mouse_down(self, x:int, y:int):
        '''
        Handle signals from the ZoomableLabel for left mouse button down event

        Parameters:
            x - the x coordinate of the event on the image
            y - the y coordinate of the event on the image
        '''
        self.current_tool.on_mouse_down(x, y)

    def on_mouse_up(self, x:int, y:int):
        '''
        Handle signals from the ZoomableLabel for left mouse button release event

        Parameters:
            x - the x coordinate of the event on the image
            y - the y coordinate of the event on the image
        '''
        self.current_tool.on_mouse_up(x, y)

    def on_new_image(self):
        '''
        Handle signals from the ZoomableLable about a new image
        '''
        self.layer_list.delete_all_layers()
        image = copy.deepcopy(self.zoomable_label.original_image)

        # Get the new canvas size
        self.canvas_shape = (image.shape[0], image.shape[1])

        # Add an alpha channel in case there isn't already one
        if image.shape[2] == 3:
            alpha_channel = np.full((*self.canvas_shape, 1), 255, dtype=np.uint8)
            image = np.concatenate((image, alpha_channel), axis=2)

        # Add a layer with the image and set the active layer index
        self.layer_list.add_layer(Layer(image))

        # Initialize the fake layer with a zeroed image)
        empty_image = np.zeros((*self.canvas_shape, 4), dtype=np.uint8)
        self.fake_layer = FakeLayer(image=empty_image)

        # Initialise the final image
        self.final_image = copy.deepcopy(image)


    #################
    # Layer methods #
    #################

    @property
    def active_layer(self) -> Layer:
        return self.layer_list[self.layer_list.active_layer_idx]

    def add_layer(self):
        '''
        Add a new layer to the top of the layer list.
        '''
        print('[ImageProcessor] add_layer')
        self.layer_list.add_layer(self.create_empty_layer())

    def create_empty_layer(self) -> Layer:
        '''
        Create an empty layer. That is a layer with no drawable elements and a fully black
        and transparent final image.
        '''
        return Layer(np.zeros((*self.canvas_shape, 4), dtype=np.uint8))

    def set_layer_visibility(self, layer: Layer, is_visible: bool) -> None:
        print('[ImageProcessor] Set layer visibility')
        self.layer_list.set_layer_visibility(layer, is_visible)
        self.render_layers()

    def set_active_layer(self, layer: Layer) -> None:
        '''
        Set the active layer.

        Args:
            layer (Layer): The new active layer to be set.
        '''
        self.layer_list.set_active_layer(layer)

    def delete_layer(self, layer: Layer) -> None:
        '''
        Delete a layer.

        Args:
            layer (Layer): The layer to be deleted.
        '''
        print('[ImageProcessor] delete_layer')
        self.layer_list.delete_layer(layer)
        self.render_layers()

    def move_layer_to_top(self, layer: Layer) -> None:
        '''
        Move a layer to the top of the layer list.

        Args:
            layer (Layer): The layer to be moved to the top.
        '''
        print('[ImageProcessor] move_layer_to_top')
        self.layer_list.move_layer_to_top(layer)
        self.render_layers()

    def insert_empty_layer(self, layer: Layer, above: bool) -> None:
        '''
        Insert an empty layer above or below the layer provided.
        Set the new layer as the active layer.

        Args:
            layer (Layer): The layer above or below which to insert the new layer.
            above (bool): If True insert the new layer above the layer provided.
                If False insert the new layer below the layer provided
        '''
        print('[ImageProcessor] insert_layer_above')
        # Get the index at which to insert the new layer
        insert_index = self.layer_list.get_layer_idx(layer)
        if above:
            insert_index += 1

        # Insert the new layer
        self.layer_list.insert_empty_layer(insert_index, self.create_empty_layer())

    def render_partial_layer(self, layer:Layer, start_index:int, end_index:int) -> np.ndarray:
        '''
        Render part of a layer by adding the drawable elements together.

        Args:
            layer (Layer): The layer which will be partially rendered.
            start_index (int): The index of the first drawable element to draw.
            end_index (int): The index of the last drawable element to draw.
        '''
        # Create a new image on which we will draw
        image = np.zeros_like(self.final_image)
        # Draw the drawable elements on top of the image
        for i in range(start_index, end_index):
            self.overlay_element_on_image(image, layer.elements[i])
        return image

    def render_layers(self):
        '''
        Render all layers
        '''
        self.final_image = None
        for layer in (l for l in self.layer_list if l.visible):
            if self.final_image is None:
                self.final_image = layer.final_image
                continue
            self.final_image = self.overlay_images(self.final_image, layer.final_image)

        # If there is no final_image to be drawn then draw empty canvas
        if self.final_image is None:
            self.final_image = np.zeros((*self.canvas_shape, 4))

        self.update_zoomable_label()

    def overlay_images(self, image_bottom:np.ndarray, image_top:np.ndarray) -> np.ndarray:
        '''
        Overlay two images and return the result

        Parameters:
            image_bottom: the image on the bottom. cv2 image with 4 channels
            image_top: the image on the top. cv2 image with 4 channels
        Returns:
            cv2 image with 4 channels. The result of placing image_top on top of image_bottom
        '''
        bottom_alpha = image_bottom[:, :, 3] / 255.0
        overlay_rgb = image_top[:, :, :3]
        overlay_alpha = image_top[:, :, 3] / 255.0
        image_result = np.zeros_like(image_bottom)
        for c in range(3): # Loop over the RGB channels
            image_result[:, :, c] = (overlay_rgb[:, :, c] * overlay_alpha +
                                   image_bottom[:, :, c] * (1 - overlay_alpha)).astype(np.uint8)
        # Compute the final alpha channel
        image_result[:, :, 3] = ((overlay_alpha + bottom_alpha * (1.0 - overlay_alpha)) * 255).astype(np.uint8)
        return image_result

    ###################
    # Element methods #
    ###################

    def render_element(self, drawable_element:DrawableElement, redraw:bool) -> None:
        if (not redraw) and drawable_element.image is not None:
            # Do not redraw if the image is already drawn
            return
        tool_name = drawable_element.tool
        tool_obj = self.tool_manager.tools[tool_name]['object']
        tool_obj.draw_drawable_element(drawable_element)

    def add_element(self, drawable_element:DrawableElement):
        # Add the element to the current layer
        self.active_layer.add_element(drawable_element)
        self.render_element(drawable_element, redraw=False) # render the drawable element
        self.active_layer.final_image = self.overlay_element_on_image(self.active_layer.final_image, drawable_element)
        # Add the layers together to get the final image
        self.render_layers()

    def apply_element_transformation(self, drawable_element:DrawableElement) -> None:
        '''
        This function applies the transformation of a drawable_element and redraws the layer which contains it.
        The drawable element must be in the active layer.

        Args:
            drawable_element (DrawableElement): The drawable_element. It must be in the elements list of the
                currently active layer.
        '''
        # Find the index of the updated drawable element
        element_index = self.active_layer.get_element_index(drawable_element)

        # Render everything below the chosen drawable element
        image_below = self.render_partial_layer(self.active_layer, 0, end_index=element_index)

        # Render everything above the chosen drawable element
        image_above = self.render_partial_layer(self.active_layer,
                                                start_index=element_index,
                                                end_index=len(self.active_layer.elements))

        # Combine image_below, the drawable element, and image_above to get the final image
        self.active_layer.final_image = copy.deepcopy(self.active_layer.image)
        self.active_layer.final_image = self.overlay_images(self.active_layer.final_image, image_below)
        self.overlay_element_on_image(self.active_layer.final_image, drawable_element)
        self.active_layer.final_image = self.overlay_images(self.active_layer.final_image, image_above)

        # Update the final image
        self.render_layers()

    def overlay_element_on_image(self, image:np.ndarray, drawable_element:DrawableElement):
        '''
        Modify an image by overlaying a drawable_element on top of it. Take into account opacity.
        The image is modified in place and returned as modified. If the use case requires
        for the original image to be unchanged you need to deepcopy the image before calling
        this method, or add an `in_place` parameter to overlay_element_on_image.

        Parameters:
            image: an opencv image
            drawable_element: A drawable element that has already been rendered.
                If the drawable element has an affine transformation it will be applied when overlayig it
        '''
        # Get the transformation
        transformation = drawable_element.get_transformation()
        # Apply the affine transformation
        transformed_element_img = cv2.warpAffine(drawable_element.image,
                                                 transformation,
                                                 (image.shape[1], image.shape[0]))

        overlay_rgb = transformed_element_img[:, :, :3] # RGB channels of the drawable element
        overlay_alpha = transformed_element_img[:, :, 3] / 255.0 # The alpha channel of the drawable element
        image_alpha = 1.0 - overlay_alpha
        for c in range(3):
            image[:, :, c] = (overlay_rgb[:, :, c] * overlay_alpha +
                              image[:, :, c] * image_alpha).astype(np.uint8)
        # Compute the final alpha channel
        image[:, :, 3] = ((overlay_alpha + (image[:, :, 3] / 255) * (1.0 - overlay_alpha)) * 255).astype(np.uint8)

        return image

    def get_touch_element(self, x, y, r) -> DrawableElement:
        return self.active_layer.get_touched_element(x, y, r)