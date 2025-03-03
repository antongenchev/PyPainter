import importlib
import os
import yaml
from typing import List
from src.config import config


class ToolManager:
    def __init__(self, image_processor):
        self.image_processor = image_processor
        self.tools = {}
        self.tools_dir = 'src/ImageProcessingTools/'

    def discover_available_tools(self) -> List[dict]:
        '''
        Find all the tools downloaded and available in the ImageProcessingTools folder.

        Returns:
            List[dict]: A list of dictionaries. Each dictionary represents a single tool.
        '''
        discovered_tools = []
        for subdir in os.listdir(self.tools_dir):
            subdir_path = os.path.join(self.tools_dir, subdir)
            if not os.path.isdir(subdir_path) or not subdir.endswith('Tool'):
                continue

            tool_info = self.read_tool_configuration(os.path.join(subdir_path, 'configuration.yaml'))
            discovered_tools.append(tool_info)
        return discovered_tools

    def discover_downloadable_tools(self) -> List[dict]:
        pass

    def load_tool(self, name: str):
        '''
        Load a tool from the ImageProcessingTools directory.

        Args:
            name (str): The name of the tool to be loaded e.g. 'PencilTool'.
        '''
        # Check that the tool is not already loaded
        if name in self.tools:
            return # Do not load a tool if it is already loaded

        module = importlib.import_module(f'src.ImageProcessingTools.{name}.{name}')
        tool_class = getattr(module, name)
        tool_obj = tool_class(self.image_processor)
        self.tools[name] = {
            'class': tool_class,
            'object': tool_obj,
            'order': 5 # TODO don't leave that hardcoded!!!
        }

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

    def read_tool_configuration(self, path: str) -> dict:
        '''
        Read the tool configuration file and parse it returning a dictionary

        Args:
            path (str): The path to the configuration.yaml file of the tool.

        Returns:
            dict: A dictionary with all the information from the yaml file.
        '''
        try:
            with open(path, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {path}")
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Error parsing YAML file: {e}")