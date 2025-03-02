from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QListWidget,
                             QListWidgetItem, QLabel, QScrollArea,
                             QPushButton, QHBoxLayout, QGridLayout,
                             QMenu, QAction)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from src.Layers.Layer import Layer
from src.Layers.LayerListGUI import LayerListGUI
from src.utils.image_rendering import cv2_to_qpixmap, create_svg_icon
import cv2
import os

class LayerList(QWidget):
    def __init__(self):
        super().__init__()

        self.resource_path = '/home/anton-genchev/projects/Screenshot-utility/resources/layerlist'

        self.layer_list = []
        self.active_layer_idx: int = None

        self.gui = LayerListGUI()

    def __iter__(self):
        return iter(self.layer_list)

    def __getitem__(self, index):
        return self.layer_list[index]

    @property
    def active_layer(self) -> Layer:
        return self.layer_list[self.active_layer_idx]

    def get_layer_idx(self, layer: Layer) -> int:
        '''
        Get the index of a layer inside the layer_list. Use `is` checking
        instead of `==`.

        Args:
            layer (Layer): A layer.
        '''
        return next((i for i, l in enumerate(self.layer_list) if l is layer))

    def on_insert_layer_above(self, layer: Layer) -> None:
        '''
        Create a new layer and insert it above the provided layer.

        Args:
            layer (Layer): The layer used to say "above that layer".
        '''

    def on_insert_layer_below(self, layer: Layer) -> None:
        '''
        Create a new layer and insert it below the provided layer.

        Args:
            layer (Layer): The layer used to say "below that layer".
        '''

    def delete_all_layers(self) -> None:
        '''
        Delete all the layers.
        '''
        self.layer_list = []
        self.active_layer_idx = None

    def add_layer(self, layer: Layer, set_active: bool = False) -> None:
        '''
        Add a layer to the layer list. The new layer will be the topmost layer.

        Args:
            layer (Layer): The layer to be added.
            set_active (bool): Whether to set the new layer as the currently active layer.
        '''
        self.layer_list.append(layer)

        if set_active or self.active_layer_idx is None:
            # Set the new layer to be the active layer
            self.active_layer_idx = len(self.layer_list) - 1

        # Inform the GUI about the added layer
        self.gui.add_layer_in_gui(layer)

    def set_layer_visibility(self, layer: Layer, is_visible: bool):
        print('[LayerList] Set layer visibility')
        layer.visible = is_visible

    def set_active_layer(self, layer: Layer):
        '''
        Set the active layer.

        Args:
            layer (Layer): The new active layer to be set.
        '''
        previously_active_layer = self.layer_list[self.active_layer_idx]
        self.active_layer_idx = self.get_layer_idx(layer)
        self.gui.set_active_layer_in_gui(layer, previously_active_layer)

    def delete_layer(self, layer: Layer):
        '''
        Delete a layer.

        Args:
            layer (Layer): The layer to be deleted.
        '''
        print('[LayerList] delete_layer')
        idx_to_delete = self.get_layer_idx(layer)
        # Handle special case: deleting the currently active layer
        if idx_to_delete == self.active_layer_idx:
            if self.active_layer_idx > 0: # Try getting a layer under the active layer
                self.set_active_layer(self.layer_list[self.active_layer_idx - 1])
            elif len(self.layer_list) > 1: # Otherwise get the top layer
                self.set_active_layer(self.layer_list[-1])
            else: # Handle the case of having zero layers left
                self.active_layer_idx = None

        # If the active index is after idx_do_delete we need to adjust it
        if self.active_layer_idx is not None and idx_to_delete < self.active_layer_idx:
            self.active_layer_idx -= 1

        # Delete the layer from the gui
        self.gui.delete_layer_in_gui(layer)
        # Delete the layer from the layerlist
        del self.layer_list[idx_to_delete]

    def move_layer_to_top(self, layer: Layer) -> None:
        '''
        Move a layer to the top of the layer list.

        Args:
            layer (Layer): The layer to be moved to the top.
        '''
        print('[ImageProcessor] move_layer_to_top')
        idx_to_move = self.get_layer_idx(layer) # The original position of the layer

        # Move the layer to the top
        self.layer_list.pop(idx_to_move)
        self.layer_list.append(layer)

        # Update the active layer index
        if self.active_layer_idx == idx_to_move:
            self.active_layer_idx = len(self.layer_list) - 1
        elif self.active_layer_idx > idx_to_move:
            self.active_layer_idx -= 1

        # Update the gui
        self.gui.move_layer_to_top_in_gui(layer)

    def insert_empty_layer(self, insert: int, layer: Layer) -> None:
        '''
        Insert an empty layer above or below the layer provided.
        Set the new layer as the active layer.

        Args:
            insert (int): The index at which to insert hte new layer.
            layer (Layer): The empty layer that will be inserted.
        '''
        print('[LayerList] insert_layer_above')

        # Insert the new layer.
        self.layer_list.insert(insert, layer)
        self.gui.insert_layer(insert, layer)

        # Set the new layer as the active layer.
        if insert <= self.active_layer_idx:
            self.active_layer_idx += 1
        self.set_active_layer(layer)