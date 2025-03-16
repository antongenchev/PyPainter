import numpy as np
import cv2
from typing import Tuple
from PyQt5.QtGui import QPixmap, QImage, QIcon, QPainter, QColor
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtCore import Qt

def qpixmap_to_qimage(pixmap: QPixmap) -> QImage:
    """Convert QPixmap to QImage."""
    return pixmap.toImage()

def qimage_to_cv2(qimage: QImage) -> np.ndarray:
    """Convert QImage to OpenCV (cv2) image."""
    width, height = qimage.width(), qimage.height()
    ptr = qimage.bits()
    ptr.setsize(qimage.byteCount())
    arr = np.array(ptr).reshape((height, width, 4))
    cv2_image = cv2.cvtColor(arr, cv2.COLOR_BGRA2RGBA)
    return cv2_image

def qpixmap_to_cv2(pixmap: QPixmap) -> np.ndarray:
    """Convert QPixmap to OpenCV (cv2) image."""
    return qimage_to_cv2(qpixmap_to_qimage(pixmap))

def cv2_to_qpixmap(cv_image: np.ndarray) -> QPixmap:
    """Converts a cv2 image (numpy array) to a QPixmap."""
    # Check if the image has an alpha channel (i.e., 4 channels)
    if cv_image.shape[2] == 4:
        # Convert from BGRA to RGBA
        rgba_image = cv2.cvtColor(cv_image, cv2.COLOR_BGRA2RGBA)
        # Create a QImage with Format_RGBA8888 which supports transparency
        qimage = QImage(rgba_image.data,
                        rgba_image.shape[1],
                        rgba_image.shape[0],
                        rgba_image.strides[0],
                        QImage.Format_RGBA8888)
    else:
        # Otherwise assume a 3-channel image and convert BGR to RGB
        rgb_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
        qimage = QImage(rgb_image.data,
                        rgb_image.shape[1],
                        rgb_image.shape[0],
                        rgb_image.strides[0],
                        QImage.Format_RGB888)
    
    return QPixmap.fromImage(qimage)

def create_svg_icon(icon_path:str, size: Tuple[int, int]=(24, 24)):
        '''
        Helper function to create QIcon from SVG file path
        '''
        icon = QIcon()
        renderer = QSvgRenderer(icon_path)
        pixmap = QPixmap(size[0], size[1])
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        icon.addPixmap(pixmap)
        return icon

def generate_checkerboard(width: int, height: int, square_size: int = 10) -> QPixmap:
    """
    Generate a checkerboard QPixmap to represent transparency.

    Args:
        width (int): Width of the checkerboard.
        height (int): Height of the checkerboard.
        square_size (int): Size of each checker square.

    Returns:
        QPixmap: A checkerboard pixmap.
    """
    checkerboard = QPixmap(width, height)
    painter = QPainter(checkerboard)
    color1 = QColor(200, 200, 200)  # Light gray
    color2 = QColor(150, 150, 150)  # Dark gray

    for y in range(0, height, square_size):
        for x in range(0, width, square_size):
            color = color1 if (x // square_size) % 2 == (y // square_size) % 2 else color2
            painter.fillRect(x, y, square_size, square_size, color)

    painter.end()
    return checkerboard

def overlay_pixmap_on_checkerboard(pixmap: QPixmap, width: int, height: int, square_size: int = 10) -> QPixmap:
    """
    Overlays a checkerboard background behind a given QPixmap.

    Parameters:
        pixmap (QPixmap): The original image pixmap.
        width (int): Width of the output pixmap.
        height (int): Height of the output pixmap.
        square_size (int): Size of each checkerboard square.

    Returns:
        QPixmap: The final pixmap with a checkerboard background.
    """
    final_pixmap = QPixmap(width, height)

    # Create and draw a checkerboard background
    checkerboard = generate_checkerboard(width, height, square_size)
    painter = QPainter(final_pixmap)
    painter.drawPixmap(0, 0, checkerboard)

    # Calculate offsets for positioning the input pixmap.
    p_width = pixmap.width()
    p_height = pixmap.height()
    offset_x = (width - p_width) // 2
    offset_y = (height - p_height) // 2
    
    # Draw the original pixmap on top
    painter.drawPixmap(offset_x, offset_y, pixmap)
    painter.end()

    return final_pixmap