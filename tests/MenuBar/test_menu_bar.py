import pytest
import cv2
import numpy as np
from unittest.mock import MagicMock, patch
from PyQt5.QtWidgets import QApplication
from src.MenuBar.MenuBar import MenuBar
from PyQt5.QtWidgets import QFileDialog


@pytest.fixture
def menubar() -> MenuBar:
    """
    Fixture to create a MenuBar instance with a mock callback.
    """
    menu_bar = MenuBar()
    menu_bar.callback_update_image = MagicMock()
    return menu_bar

def test_load_image(menubar: MenuBar, mocker):
    mocker.patch.object(QFileDialog, 'getOpenFileName', return_value=("fake_path.jpg", "Images (*.png *.jpg *.jpeg *.bmp *.tiff *.webp)"))
    mocker.patch.object(cv2, 'imread', return_value="fake_image_array")
    menubar.load_image()
    QFileDialog.getOpenFileName.assert_called_once_with(None, "Open Image", "", "Images (*.png *.jpg *.jpeg *.bmp *.tiff *.webp)")

    cv2.imread.assert_called_once_with("fake_path.jpg", cv2.IMREAD_UNCHANGED)
    menubar.callback_update_image.assert_called_once_with("fake_image_array")

def test_load_image_cancel(menubar: MenuBar, mocker):
    mocker.patch.object(QFileDialog, 'getOpenFileName', return_value=("", "Images (*.png *.jpg *.jpeg *.bmp *.tiff *.webp)"))
    mocker.patch.object(cv2, 'imread', return_value=None)
    
    menubar.load_image()
    QFileDialog.getOpenFileName.assert_called_once_with(None, "Open Image", "", "Images (*.png *.jpg *.jpeg *.bmp *.tiff *.webp)")

    cv2.imread.assert_not_called()
    menubar.callback_update_image.assert_not_called()
