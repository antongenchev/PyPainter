from PyQt5.QtWidgets import QMenuBar, QMenu, QAction
from PyQt5.QtCore import pyqtSignal


class MenuBar(QMenuBar):
    load_image_signal = pyqtSignal()  # Signal emitted when "Load Image" is clicked
    save_image_signal = pyqtSignal()  # Signal emitted when "Save Image" is clicked
    manage_plugins_signal = pyqtSignal()  # Signal emitted when "Manage Plugins" is clicked

    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        """Initialize the menu bar with File and Plugins menus"""

        # **File Menu**
        file_menu = QMenu("File", self)
        self.addMenu(file_menu)

        action_load = QAction("Load Image", self)
        action_load.triggered.connect(self.load_image_signal.emit)  # Emit signal when clicked
        file_menu.addAction(action_load)

        action_save = QAction("Save Image", self)
        action_save.triggered.connect(self.save_image_signal.emit)
        file_menu.addAction(action_save)

        # **Plugins Menu**
        plugins_menu = QMenu("Plugins", self)
        self.addMenu(plugins_menu)

        action_manage_plugins = QAction("Manage Plugins", self)
        action_manage_plugins.triggered.connect(self.manage_plugins_signal.emit)
        plugins_menu.addAction(action_manage_plugins)
