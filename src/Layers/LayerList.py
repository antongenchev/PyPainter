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

    def on_delete_layer(self, layer: Layer) -> None:
        '''
        Delete a layer

        Args:
            layer (Layer): The layer to be deleted.
        '''

    def on_move_layer_to_top(self, layer: Layer) -> None:
        '''
        Move a layer to the top of the layer list.

        Args:
            layer (Layer): The layer to be moved.
        '''

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
                pass # TODO

        # If the active index is after idx_do_delete we need to adjust it
        if idx_to_delete < self.active_layer_idx:
            self.active_layer_idx -= 1

        # Delete the layer from the gui
        self.gui.delete_layer_in_gui(layer)
        # Delete the layer from the layerlist
        del self.layer_list[idx_to_delete]


class ClickableLabel(QLabel):
    """Custom QLabel that emits a signal when clicked"""
    clicked = pyqtSignal()

    def __init__(self, parent=None, layer_list:LayerList=None, layer:Layer=None):
        '''
        Pass the layer_list and layer so that actions on the layer performed by the LayerList
        can be triggered.
        '''
        super().__init__(parent)
        self.layer_list = layer_list
        self.layer = layer

    def mousePressEvent(self, event):
        self.clicked.emit()  # Emit signal when clicked

    def contextMenuEvent(self, event):
        """
        Override the context menu event to show a custom menu on right-click.
        """
        menu = QMenu(self)

        # Create actions
        action_move_to_top = QAction("Move to Top", self)
        action_insert_above = QAction("Insert Above", self)
        action_insert_below = QAction("Insert Below", self)
        action_delete = QAction("Delete", self)

        # Connect actions to methods
        action_move_to_top.triggered.connect(lambda: self.move_to_top())
        action_insert_above.triggered.connect(lambda: self.insert_above())
        action_insert_below.triggered.connect(lambda: self.insert_below())
        action_delete.triggered.connect(lambda: self.delete())

        # Add actions to menu
        menu.addAction(action_move_to_top)
        menu.addAction(action_insert_above)
        menu.addAction(action_insert_below)
        menu.addSeparator()
        menu.addAction(action_delete)

        # Show the menu at the cursor position
        menu.exec_(event.globalPos())

    def move_to_top(self):
        """Moves the current layer to the top of the layer list."""
        self.layer_list.on_move_layer_to_top(self.layer)

    def insert_above(self):
        """Inserts a new layer directly above this one."""
        self.layer_list.on_insert_layer_above(self.layer)

    def insert_below(self):
        """Inserts a new layer directly below this one."""
        self.layer_list.on_insert_layer_below(self.layer)

    def delete(self):
        """Deletes the current layer."""
        self.layer_list.on_delete_layer(self.layer)

