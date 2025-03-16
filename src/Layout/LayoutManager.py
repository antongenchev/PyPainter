from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget, QSizePolicy, QLabel


class LayoutManager(QWidget):
    _instance = None  # Singleton instance

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(LayoutManager, cls).__new__(cls)
            QWidget.__init__(cls._instance)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self.layer_guis = {}
            self.config = self.load_config()
            self.selected_layout_config = None
            self.setup_layout()

    def load_config(self) -> dict:
        '''
        Get the config for the Layout Manager.
        '''
        from src.config import config
        if 'layout' in config:
            self.config = config['layout']
            return self.config
        # Default to an empty dict if config section is not found.
        return {}

    def choose_layout_config(self, current_width, current_height) -> dict:
        '''
        Get the best layout for a window/device with the current dimensions.
        '''
        best_config = None
        best_distance = float('inf')
        for layout_config in self.config.get('layouts', []):
            target_width = layout_config.get('width', 0)
            target_height = layout_config.get('height', 0)
            # Calculate Euclidean distance between current size and layout config size
            distance = ((current_width - target_width) ** 2 + (current_height - target_height) ** 2) ** 0.5
            if distance < best_distance:
                best_distance = distance
                best_config = layout_config
        return best_config

    def setup_layout(self):
        # Get the current window dimensions (fallback to default if not set)
        current_width = self.width() if self.width() > 0 else 800
        current_height = self.height() if self.height() > 0 else 600

        # Pick the layout configuration that best matches current dimensions
        self.selected_layout_config = self.choose_layout_config(current_width, current_height)

        # Create the layout container widget
        main_widget = self.create_layout_from_config(self.selected_layout_config.get("areas", []), "vertical")

        # Create a new layout and add main_widget
        main_layout = QVBoxLayout()
        main_layout.addWidget(main_widget)

        self.setLayout(main_layout)

    def create_layout_from_config(self, areas, parent_type):
        '''
        Recursively create layouts from a list of area defintions.
        '''
        container = QWidget()  # This will hold the layout
        layout = QVBoxLayout() if parent_type == 'vertical' else QHBoxLayout()
        container.setLayout(layout)

        # Set margins and padding to 0
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        for area in areas:
            area_type = area.get('type', 'vertical')
            sub_container = QWidget()

            sub_layout = QVBoxLayout() if area_type == 'vertical' else QHBoxLayout()
            # Set margins and padding to 0
            sub_layout.setContentsMargins(0, 0, 0, 0)
            sub_layout.setSpacing(0)

            sub_container.setLayout(sub_layout)

            # Set size policy if needed
            if 'size' in area:
                size_info = area['size']
                if 'width' in size_info:
                    sub_container.setFixedWidth(size_info['width'])
                if 'height' in size_info:
                    sub_container.setFixedHeight(size_info['height'])
                sub_container.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            else:
                sub_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

            # If there are nested areas, recursively build the nested layout
            if 'children' in area:
                nested_container = self.create_layout_from_config(area['children'], area_type)
                sub_layout.addWidget(nested_container)  # Add nested layout container

            # Save a reference to this sublayout for future modifications
            self.layer_guis[area.get('name', 'default')] = sub_layout

            # Use a stretch factor if provided (default 0 means no stretch)
            stretch = area.get('stretch', 0)

            layout.addWidget(sub_container, stretch)

        return container  # Return the top-level container widget

    def resizeEvent(self, event):
        # TODO
        super().resizeEvent(event)