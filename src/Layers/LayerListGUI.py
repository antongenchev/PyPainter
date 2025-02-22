from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QListWidget,
                             QListWidgetItem, QLabel, QScrollArea,
                             QPushButton, QHBoxLayout, QGridLayout,
                             QMenu, QAction)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from src.Layers.Layer import Layer
from src.utils.image_rendering import cv2_to_qpixmap, create_svg_icon
from collections import defaultdict
from typing import Optional
import cv2
import os

class LayerListGUI(QWidget):

    # Signals
    layer_added = pyqtSignal()
    layer_inserted_above = pyqtSignal(Layer)
    layer_inserted_below = pyqtSignal(Layer)
    layer_deleted = pyqtSignal(Layer)
    layer_moved_to_top = pyqtSignal(Layer)
    layer_visibility_toggled = pyqtSignal(Layer, bool)
    layer_selected = pyqtSignal(Layer)

    def __init__(self):
        super().__init__()

        self.resource_path = '/home/anton-genchev/projects/Screenshot-utility/resources/layerlist'

        # Mapping layer ids to dictionary of gui elements
        self.gui_mapping = defaultdict(lambda: defaultdict(lambda: None), {})

        self.initGUI()

    def initGUI(self) -> None:
        '''
        Initialise the gui for the layer list.
        '''
        layout = QVBoxLayout()
        layout.setSpacing(10)

        # Menu with Buttons
        menu_layout = QHBoxLayout()
        button_add = QPushButton("+")
        button_add.setFixedSize(30, 30)
        button_add.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 18px;
                border-radius: 15px;
                border: none;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        button_add.clicked.connect(lambda: self.layer_added.emit())
        menu_layout.addWidget(button_add)
        menu_layout.addStretch()

        # Scroll Area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFixedSize(140, 200)
        self.scroll_container = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_container)
        self.scroll_layout.setAlignment(Qt.AlignTop)
        self.scroll_area.setWidget(self.scroll_container)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        layout.addLayout(menu_layout)
        layout.addWidget(self.scroll_area)
        self.setLayout(layout)

        self.icon_eye_enable = create_svg_icon(os.path.join(self.resource_path, 'eye_enable.svg'))
        self.icon_eye_disable = create_svg_icon(os.path.join(self.resource_path, 'eye_disable.svg'))

    def add_layer_in_gui(self, layer: Layer) -> None:
        '''
        Add a clickable image to the GUI of the LayerList to represent
        a single layer.

        Args:
            layer (Layer): The layer to be added in the gui.
        '''
        # Get the qpixmap image representing the layer
        qpixmap = cv2_to_qpixmap(layer.final_image).scaled(100, 75, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        item_widget = QWidget()
        item_layout = QGridLayout(item_widget)
        item_layout.setContentsMargins(0, 0, 0, 0)
        item_layout.setSpacing(0)

        # Clickable Image Label
        image_label = ClickableLabel(layer_list_gui=self, layer=layer)
        image_label.setPixmap(qpixmap)
        image_label.setStyleSheet("border: 4px solid #ccc; border-radius: 3px;")
        image_label.clicked.connect(lambda: self.on_image_clicked(layer))

        # Small Button (e.g., "Remove" or "Options")
        button_eye = QPushButton()
        button_eye.setIcon(self.icon_eye_enable)
        button_eye.setIconSize(QSize(24, 24))
        button_eye.setFixedSize(QSize(36, 36))
        button_eye.clicked.connect(lambda: self.on_eye_clicked(button_eye, layer))
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_eye.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
            }
            QPushButton::hover {
                background: rgba(255, 255, 255, 30);
                border-radius: 18px;
            }
        """)
        button_layout.addWidget(button_eye)
        button_layout.setContentsMargins(0, 0, 0, 0)

        # Add items to layout
        item_layout.addWidget(image_label, 0, 0, Qt.AlignTop | Qt.AlignRight)  # Add image below
        item_layout.addLayout(button_layout, 0, 0, Qt.AlignTop | Qt.AlignRight)  # Add button at top
        item_widget.setLayout(item_layout)

        # Add widgets to the gui dictionary for controlling later
        self.gui_mapping[layer.id]['image_label'] = image_label
        self.gui_mapping[layer.id]['item_widget'] = item_widget

        # Add to scroll layout
        self.scroll_layout.insertWidget(0, item_widget)

    def set_active_layer_in_gui(self, new_active_layer: Layer, previous_active_layer: Layer):
        '''
        Highlight the active layer in the gui.
        '''
        print('[LayerListGUI] Set active layer')
        self.gui_mapping[previous_active_layer.id]['image_label'] .setStyleSheet("border: 4px solid #ccc; border-radius: 3px;")
        self.gui_mapping[new_active_layer.id]['image_label'] .setStyleSheet("border: 4px solid #aaa; border-radius: 5px;")

    def delete_layer_in_gui(self, layer: Layer):
        '''
        Delete a layer.

        Args:
            layer (Layer): The layer to be deleted.
        '''
        # Delete all the widgets associated with the layer        
        item_widget = self.gui_mapping[layer.id]['item_widget']
        self.scroll_layout.removeWidget(item_widget)
        item_widget.setParent(None)
        item_widget.deleteLater()

        # Delete from the gui mapping dictionary.
        del self.gui_mapping[layer.id]

    def on_image_clicked(self, layer):
        '''
        Handles clicks on the layer image in the layer list gui.
        '''
        print('[EVENT] on_image_clicked')
        self.layer_selected.emit(layer)

    def on_eye_clicked(self, button_eye: QPushButton, layer: Layer) -> None:
        '''
        Handles clicks on the eye button. Toggles the visiblity of the layer.

        Args:
            button_eye (QPushButton): The button with the eye. The icon of this button
                will be updated.
            layer (Layer): The layer corresponding to the eye button clicked
        '''
        print('[EVENT] on_eye_clicked')
        new_visibility_state = not layer.visible
        if new_visibility_state:
            button_eye.setIcon(self.icon_eye_enable)
        else:
            button_eye.setIcon(self.icon_eye_disable)
        # Emit a signal with the new visibility state of the layer.
        self.layer_visibility_toggled.emit(layer, new_visibility_state)



class ClickableLabel(QLabel):
    """Custom QLabel that emits a signal when clicked"""
    clicked = pyqtSignal()

    def __init__(self, parent=None, layer_list_gui:LayerListGUI=None, layer:Layer=None):
        '''
        Pass the layer_list_gui and layer so that actions on the layer performed by the LayerList
        can be triggered.
        '''
        super().__init__(parent)
        self.layer_list_gui = layer_list_gui
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
        action_move_to_top.triggered.connect(lambda: self.layer_list_gui.layer_moved_to_top(self.layer))
        action_insert_above.triggered.connect(lambda: self.layer_list_gui.layer_inserted_above(self.layer))
        action_insert_below.triggered.connect(lambda: self.layer_list_gui.layer_inserted_below(self.layer))
        action_delete.triggered.connect(lambda: self.layer_list_gui.layer_deleted.emit(self.layer))

        # Add actions to menu
        menu.addAction(action_move_to_top)
        menu.addAction(action_insert_above)
        menu.addAction(action_insert_below)
        menu.addSeparator()
        menu.addAction(action_delete)

        # Show the menu at the cursor position
        menu.exec_(event.globalPos())
