
from src.ImageProcessingTools.ImageProcessingTool import ImageProcessingTool
from PyQt5.QtWidgets import QPushButton, QWidget, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import QSize, QPoint
from PyQt5.QtGui import QCursor, QPixmap, QPainter
from src.utils.image_rendering import *
from functools import partial


class EraserTool(ImageProcessingTool):
    def __init__(self, image_processor):
        super().__init__(image_processor)

    def create_ui(self):
        """Create the button for the eraser tool."""
        self.button = QPushButton()
        self.button.setIcon(create_svg_icon(f'{self.resources_path}/tool_button.svg'))
        self.button.setIconSize(QSize(36, 36))
        self.button.setFixedSize(QSize(36, 36))
        self.button.clicked.connect(partial(self.set_tool))
        return self.button
    
    def create_settings_ui(self):
        settings_widget = QWidget()
        layout = QHBoxLayout()

        # Size Slider
        size_slider_layout = QVBoxLayout()

        layout.addLayout(size_slider_layout)

        settings_widget.setLayout(layout)
        return settings_widget

    def enable(self) -> None:
        self.button.setStyleSheet("background-color: lightgray; border-radius: 5px;")
        self.set_cursor_to_eraser()
        super().enable()

    def disable(self) -> None:
        '''
        Overide of the disable function from the ImageProcessingTool to save the last Text Widget.
        '''
        # Remove highlight from button
        self.button.setStyleSheet("")
        super().disable()

    def on_mouse_down(self, x: int, y: int):
        pass

    def on_mouse_up(self, x: int, y: int):
        pass

    def on_mouse_move(self, x: int, y: int):
        pass

    def set_cursor_to_eraser(self):
        '''
        Set the cursor inside the zoomable widget to an eraser.
        '''
                # Create a QPixmap to hold the rendered SVG image
        pixmap = QPixmap(32, 32)  # Specify the size of the pixmap for the cursor
        pixmap.fill(Qt.transparent)  # Fill it with transparency
        # Use QSvgRenderer to render the SVG onto the QPixmap
        renderer = QSvgRenderer(f'{self.resources_path}/cursor_eraser.svg')
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()

        #Set the cursor hotspot to the lower-left corner
        hotspot = QPoint(0, pixmap.height() - 1)

        # Create the cursor and set it
        cursor = QCursor(pixmap, hotspot.x(), hotspot.y())
        self.image_processor.zoomable_widget.setCursor(cursor)