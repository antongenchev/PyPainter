import pytest
import importlib
import os
import yaml
from unittest.mock import MagicMock, patch, mock_open
from src.ImageProcessingTools.ToolManager import ToolManager

@pytest.fixture
def mock_image_processor():
    return MagicMock()

@pytest.fixture
def tool_manager(mock_image_processor):
    return ToolManager(mock_image_processor)

def test_discover_available_tools(tool_manager: ToolManager):
    mock_tools = ['PencilTool', 'TextTool']
    with patch('os.listdir', return_value=mock_tools), \
         patch('os.path.isdir', return_value=True), \
         patch.object(tool_manager, "read_tool_configuration", \
                      return_value={"name": "PencilTool", "x": 1}):
        tools = tool_manager.discover_available_tools()
        assert len(tools) == len(mock_tools)
        assert tools[0]['name'] == 'PencilTool'

def test_load_tool(tool_manager: ToolManager):
    mock_module = MagicMock()
    mock_class = MagicMock()
    mock_instance = MagicMock()

    mock_class.return_value = mock_instance
    mock_module.MockTool = mock_class
    with patch("importlib.import_module", return_value=mock_module):
        tool_manager.load_tool("MockTool")
        assert "MockTool" in tool_manager.tools
        assert tool_manager.tools["MockTool"]["object"] == mock_instance

def test_load_tool_already_loaded(tool_manager):
    tool_manager.tools["MockTool"] = {"class": MagicMock(), "object": MagicMock()}
    with patch("importlib.import_module") as mock_import:
        tool_manager.load_tool("MockTool")
        mock_import.assert_not_called()

