from PyQt5.QtWidgets import QHBoxLayout, QGridLayout, QWidget, QLabel, QMenu, QPushButton, QScrollArea, QSizePolicy
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from collections import defaultdict
import os
from src.DrawableElement import DrawableElement
from src.Layout.LayoutManager import LayoutManager
from src.utils.image_rendering import cv2_to_qpixmap, create_svg_icon, overlay_pixmap_on_checkerboard

class ElementListGUI(QWidget):

    # Signals
    element_selected = pyqtSignal(DrawableElement)
    element_visibility_toggled = pyqtSignal(DrawableElement, bool)

    def __init__(self):
        super().__init__()

        self.resource_path = '/home/anton-genchev/projects/Screenshot-utility/resources/layerlist'

        # Mapping element ids to dictionary of gui elements
        self.gui_mapping = defaultdict(lambda: defaultdict(lambda: None), {})

        self.initGUI()

    def initGUI(self):
        '''
        Initialise the gui for the layer list.
        '''
        layout = QHBoxLayout()
        layout.setSpacing(10)

        # Scroll Area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFixedSize(500, 140)
        self.scroll_container = QWidget()
        self.scroll_layout = QHBoxLayout(self.scroll_container)

        self.scroll_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.scroll_layout.setSpacing(10)
        self.scroll_area.setWidget(self.scroll_container)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        layout.addWidget(self.scroll_area)
        self.setLayout(layout)

        self.icon_eye_enable = create_svg_icon(os.path.join(self.resource_path, 'eye_enable.svg'))
        self.icon_eye_disable = create_svg_icon(os.path.join(self.resource_path, 'eye_disable.svg'))

    def add_element_in_gui(self, element: DrawableElement, *, index=0) -> None:
        '''
        Add an element in the gui.
        '''
        # Get the qpixmap image representing the element
        qpixmap = cv2_to_qpixmap(element.image).scaled(100, 75, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        qpixmap = overlay_pixmap_on_checkerboard(qpixmap, 100, 75)

        item_widget = QWidget()
        item_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        item_layout = QGridLayout(item_widget)
        item_layout.setContentsMargins(0, 0, 0, 0)

        # Clickable Image Label
        image_label = ClickableElementLabel(element_list_gui=self, element=element)
        image_label.setPixmap(qpixmap)
        image_label.setStyleSheet("border: 4px solid #ccc; border-radius: 3px;")
        image_label.clicked.connect(lambda: self.on_image_clicked(element))

        # Button for toggling visibility
        button_eye = QPushButton()
        button_eye.setIcon(self.icon_eye_enable)
        button_eye.setIconSize(QSize(24, 24))
        button_eye.setFixedSize(QSize(36, 36))
        button_eye.clicked.connect(lambda: self.on_eye_clicked(button_eye, element))
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
        self.scroll_layout.insertWidget(index, item_widget)

    def set_as_active(self):
        """Show the GUI for this layer and hide the previous if such is shown."""
        LayoutManager().layer_guis['element_list_gui'].addWidget(self)

    def set_as_inactive(self):
        """Hide the GUI."""

    def on_image_clicked(self, element):
        """Handles clicks on the element image in the element list gui"""
        self.element_selected.emit(element)

    def on_eye_clicked(self, button_eye: QPushButton, element: DrawableElement) -> None:
        '''
        Handles clicks on the eye button. Toggles the visiblity of the element.

        Args:
            button_eye (QPushButton): The button with the eye. The icon of this button
                will be updated.
            element (DrawableElement): The element corresponding to the eye button clicked
        '''
        print('[GUI] on_eye_clicked')
        new_visibility_state = not element.visible
        if new_visibility_state:
            button_eye.setIcon(self.icon_eye_enable)
        else:
            button_eye.setIcon(self.icon_eye_disable)
        # Emit a signal with the new visibility state of the layer.
        self.element_visibility_toggled.emit(element, new_visibility_state)



class ClickableElementLabel(QLabel):
    """Custom QLabel that emits a signal when clicked"""
    clicked = pyqtSignal()

    def __init__(self, parent=None, element_list_gui: ElementListGUI=None, element: DrawableElement=None):
        '''
        Pass the element_list_gui and element so that actions on the element can be triggered.
        '''
        super().__init__(parent)
        self.element_list_gui = element_list_gui
        self.element = element

    def mousePressEvent(self, event):
        self.clicked.emit()  # Emit signal when clicked

    def contextMenuEvent(self, event):
        """
        Override the context menu event to show a custom menu on right-click.
        """
        menu = QMenu(self)

        # Show the menu at the cursor position
        menu.exec_(event.globalPos())