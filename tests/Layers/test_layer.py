import pytest
import numpy as np
from unittest.mock import MagicMock
from src.Layers.Layer import Layer, FakeLayer
from src.DrawableElement import DrawableElement


@pytest.fixture
def sample_image():
    """Fixture to create a sample image for testing."""
    return np.zeros((100, 100, 3), dtype=np.uint8) # Create a black image (100x100)

@pytest.fixture
def layer(sample_image):
    """Fixture to create a Layer instance for testing."""
    return Layer(image=sample_image, visible=True)

def test_layer_initialization(layer, sample_image):
    """Ensure Layer is initialized correctly."""
    assert layer.image is sample_image
    assert layer.final_image is not sample_image  # final_image should be a deepcopy
    assert layer.visible is True
    assert layer.drawing_enabled is False
    assert layer.id == 0  # First layer should have id 0
    assert len(layer.elements) == 0  # No elements initially

def test_toggle_visibility(layer):
    """Ensure toggle visibility works as expected."""
    assert layer.visible is True
    layer.toggle_visibility()
    assert layer.visible is False
    layer.toggle_visibility()
    assert layer.visible is True

def test_add_element(layer: Layer):
    """Ensure that elements can be added to the layer."""
    element = MagicMock(DrawableElement)
    layer.add_element(element)
    assert len(layer.elements) == 1
    assert layer.elements[0] is element

def test_remove_element(layer):
    """Ensure elements can be removed from the layer."""
    element1 = MagicMock(DrawableElement)
    element2 = MagicMock(DrawableElement)
    layer.add_element(element1)
    layer.add_element(element2)
    
    # Remove the first element
    layer.remove_element(0)
    assert len(layer.elements) == 1
    assert layer.elements[0] is element2
    
    # Try removing an out-of-range element
    layer.remove_element(10)
    assert len(layer.elements) == 1  # No change

def test_get_elements(layer):
    """Ensure get_elements returns the correct list of elements."""
    element1 = MagicMock(DrawableElement)
    element2 = MagicMock(DrawableElement)
    layer.add_element(element1)
    layer.add_element(element2)
    elements = layer.get_elements()
    assert elements == [element1, element2]

def test_get_element_index(layer):
    """Ensure get_element_index returns the correct index."""
    element1 = MagicMock(DrawableElement)
    element2 = MagicMock(DrawableElement)
    layer.add_element(element1)
    layer.add_element(element2)
    index = layer.get_element_index(element2)
    assert index == 1

    # If element not found
    assert layer.get_element_index(MagicMock(DrawableElement)) is None

def test_get_touched_element(layer: Layer):
    """Ensure the topmost element is returned when clicked."""
    element1 = MagicMock(DrawableElement)
    element2 = MagicMock(DrawableElement)
    layer.add_element(element1)
    layer.add_element(element2)
    
    # Top element is clicked
    element2.is_touched = MagicMock(return_value=True)
    touched_element = layer.get_touched_element(10, 10, 5)
    assert touched_element is element2

    # Bottom element is clicked
    element1.is_touched = MagicMock(return_value=True)
    element2.is_touched = MagicMock(return_value=False)
    touched_element = layer.get_touched_element(10, 10, 5)
    assert touched_element is element1

    # No element is touched
    element1.is_touched = MagicMock(return_value=False)
    element2.is_touched = MagicMock(return_value=False)
    touched_element = layer.get_touched_element(10, 10, 5)
    assert touched_element is None
