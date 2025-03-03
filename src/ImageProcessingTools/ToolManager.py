import importlib
from typing import List
from src.config import config


class ToolManager:
    def __init__(self, image_processor):
        self.image_processor = image_processor
        self.tools = {}

    def discover_available_tools(self) -> List[dict]:
        pass

    def discover_downloadable_tools(self) -> List[dict]:
        pass

    def load_tool(self, name: str):
        '''
        Load a tool from the ImageProcessingTools directory.

        Args:
            name (str): The simple name of the tool to be loaded.
                E.g. 'Pencil' instead of 'PencilTool'.
        '''

    def load_tools_from_config(self) -> None:
        '''
        Load all the tools from the config.json into the ImageProcessor.
        '''
        for tool in config['tools']:
            tool_name = tool['name']
            module = importlib.import_module(f'src.ImageProcessingTools.{tool_name}.{tool_name}')
            tool_class = getattr(module, tool_name)
            tool_obj = tool_class(self.image_processor)
            self.tools[tool_name] = {
                'class': tool_class,
                'object': tool_obj,
                'order': tool['order']
            }
