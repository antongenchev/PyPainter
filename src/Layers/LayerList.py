from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QListWidget,
                             QListWidgetItem, QLabel, QScrollArea,
                             QPushButton, QHBoxLayout, QGridLayout,
                             QMenu, QAction)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from src.Layers.Layer import Layer
from src.utils.image_rendering import cv2_to_qpixmap, create_svg_icon
import cv2
import os

class LayerList(QWidget):
    def __init__(self, image_processor):
        super().__init__()
        self.image_processor = image_processor

        self.resource_path = '/home/anton-genchev/projects/Screenshot-utility/resources/layerlist'

        self.layer_list = []
        self.active_layer_idx: int = None

        self.initGUI()
        self.add_layer_in_gui(Layer(image_processor, cv2.imread('/home/anton-genchev/Desktop/papers/hq720.jpg')))

    def __iter__(self):
        return iter(self.layer_list)

    def __getitem__(self, index):
        return self.layer_list[index]

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
        button_add.clicked.connect(lambda: self.on_button_add())
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
        image_label = ClickableLabel(layer_list=self, layer=layer)
        image_label.setPixmap(qpixmap)
        image_label.setStyleSheet("border: 4px solid #ccc; border-radius: 3px;")  # Optional styling
        image_label.clicked.connect(lambda: self.on_image_clicked())  # Connect click event

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

        # Add to scroll layout
        self.scroll_layout.insertWidget(0, item_widget)

    def on_button_add(self):
        '''
        Handle adding a new layer 
        '''
        # Create the new layer and add it to the list of layers
        new_layer = Layer(self.image_processor, cv2.imread(f'{self.resource_path}/Space Probes.jpeg'))
        self.layer_list.append(new_layer)

        # Add the new layer to the layer list gui
        self.add_layer_in_gui(new_layer)

    def on_image_clicked(self):
        """Handles image click events."""
        print(f"Image clicked!")

    def on_eye_clicked(self, button_eye: QPushButton, layer: Layer) -> None:
        '''
        Handles clicks on the eye button. Toggles the visiblity of the layer.

        Args:
            button_eye (QPushButton): The button with the eye. The icon of this button
                will be updated.
            layer (Layer): The layer corresponding to the eye button clicked
        '''
        layer.toggle_visibility()
        if layer.visible:
            button_eye.setIcon(self.icon_eye_enable)
        else:
            button_eye.setIcon(self.icon_eye_disable)

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

