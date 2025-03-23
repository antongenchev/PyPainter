import pytest
from datetime import datetime
from src.Layers.LayersCache import LayersCache

@pytest.fixture
def cache():
    return LayersCache()

def test_initialization(cache: LayersCache):
    """Ensure the cache starts empty."""
    assert len(cache.cache) == 0

def test_add_cache(cache: LayersCache):
    """Ensure layers are added to the cache correctly."""
    cache.add_cache((1, 2, 3), "image_data")
    assert (1, 2, 3) in cache.cache
    assert cache.cache[(1, 2, 3)]['data'] == "image_data"
    assert isinstance(cache.cache[(1, 2, 3)]['last_updated'], datetime)
    assert cache.cache[(1, 2, 3)]['last_used'] is None

def test_get_intersection(cache: LayersCache):
    """Ensure the function returns correct cached layers containing a given layer."""
    cache.add_cache((1, 2), "data1")
    cache.add_cache((2, 3), "data2")
    cache.add_cache((4, 5), "data3")

    results = list(cache.get_intersection(2))
    assert set(results) == {(1, 2), (2, 3)}

    results = list(cache.get_intersection(4))
    assert results == [(4, 5)]

    results = list(cache.get_intersection(6))
    assert results == []

def test_get_precalculated(cache: LayersCache):
    """Ensure `get_precalculated` returns the best non-overlapping cached tuples."""
    cache.add_cache((1, 2), "data1")
    cache.add_cache((1, 2, 3), "data2")
    cache.add_cache((0, 1, 2, 3), "data3")
    cache.add_cache((5, 6), "data4")

    result = cache.get_precalculated((1, 2, 3, 4, 5, 6))
    expected = [(1, 2, 3), (5, 6)]
    assert set(result) == set(expected)

def test_get_precalculated_no_cache(cache: LayersCache):
    """Ensure `get_precalculated` returns an empty list when no cache matches."""
    result = cache.get_precalculated((7, 8, 9))
    assert result == []

def test_get_precalculated_partial_match(cache: LayersCache):
    """Ensure `get_precalculated` works with partial cache matches."""
    cache.add_cache((1, 2), "data1")
    cache.add_cache((3, 4), "data2")
    cache.add_cache((6, 7, 8), "data3")

    result = cache.get_precalculated((1, 2, 3, 4, 5, 6, 7, 8, 9))
    expected = [(1, 2), (3, 4), (6, 7, 8)]
    assert set(result) == set(expected)

def test_get_precalculated_overlapping_choices(cache: LayersCache):
    """Ensure it picks the best possible cached sets when multiple overlap."""
    cache.add_cache((1, 2), "data1")
    cache.add_cache((2, 3), "data2")
    cache.add_cache((1, 2, 3), "data3")
    cache.add_cache((4, 5, 6), "data4")

    result = cache.get_precalculated((1, 2, 3, 4, 5, 6))
    expected = [(1, 2, 3), (4, 5, 6)]
    assert set(result) == set(expected)

def test_get_instructions(cache: LayersCache):
    """Test that a single-layer request returns an empty instruction list."""
    result = cache.get_overlay_instructions((1,))
    assert result == []


def test_get_overlay_instructions_no_cache(cache: LayersCache):
    """Test when no cache is available, each layer is treated separately."""
    result = cache.get_overlay_instructions((1, 2, 3))
    expected = [((1,), (2,)), ((1, 2), (3,))]
    assert result == expected

def test_get_overlay_instructions_with_cache(cache: LayersCache):
    """Test when cache has some precomputed layers available."""
    cache.add_cache((1, 2), "data1")
    cache.add_cache((3,), "data2")
    result = cache.get_overlay_instructions((1, 2, 3))
    expected = [((1, 2), (3,))]
    assert result == expected

def test_get_overlay_instructions_complex(cache: LayersCache):
    """Test with more complex combinations and multiple cached layers."""
    cache.add_cache((1, 2), "data1")
    cache.add_cache((3, 4), "data2")
    cache.add_cache((5,), "data3")
    result = cache.get_overlay_instructions((1, 2, 3, 4, 5))
    expected = [((3, 4), (5,)), ((1, 2), (3,4,5))]
    assert result == expected
