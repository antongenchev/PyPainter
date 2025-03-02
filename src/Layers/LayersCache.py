from typing import Tuple, List, Any, Generator
from datetime import datetime

'''
The LayerCache does not know about the LayerList or the Layers.
Instead the LayerCahce sees layers as just their indices in the
LayerList.
The LayerList uses LayersCache to store cached unions of layers.
'''

class LayersCache:

    def __init__(self):
        self.cache = {}

    def add_cache(self, layers_tuple: Tuple[int], precompiled_data: Any) -> None:
        '''
        Add a cached / precompiled data (e.g. cv2 image) for the layers in the layers_tuple
        '''
        self.cache[layers_tuple] = {
            'data': precompiled_data,
            'last_updated': datetime.now(),
            'last_used': None # None if not used at all. Otherwise a timestamp. 
        }

    def get_intersection(self, layer: int) -> Generator[Tuple[int], None, None]:
        '''
        Get all the layer tuples in the cache that contain the layer provided.

        Args:
            layer (int): The layer provided.
        Returns:
            Generator[Tuple[int]]: The layer tuples in the cache that contain the layer provided.
        '''
        return (x for x in self.cache.keys() if layer in x)

    def get_precalculated(self, layers_tuple: Tuple[int]) -> List[Tuple]:
        '''
        Get the best set of cached layer tuples to simplify the calculation of the
        `layers_tuple` requested. The purpose of this is to avoid drawing / overlaying
        all the layers from the layers_tuple.

        Args:
            layers_tuple (Tuple[int]): The set of layers which need to be drawn.

        Returns:
            List[Tuple]: A list of non-overlaping tuples of layers which are already
                cached in LayersCache.self.
        Example:
            >>> cache = LayersCache()
            >>> cache.add_cache((1,2))
            >>> cache.add_cache((1,2,3))
            >>> cache.add_cache((0,1,2,3))
            >>> cache.add_cache((5,6))
            >>> cache.get_precalculated((1,2,3,4,5,6))
            [(1,2,3),(5,6)]

            In this case 2 additional calculations will need to be made later: combining (1,2,3)
            and 4, and combining (1,2,3,4) and (5,6).
        '''
        T = layers_tuple
        n = len(T)

        # Get only the part of the cache that is contained in the layers_tuple.
        intervals = [] # Each interval is (start_index, end_index, cached_tuple)
        for cache in self.cache:
            L = len(cache)
            for i in range(n - L + 1):
                if T[i:i+L] == cache:
                    intervals.append((i, i+L, cache))
                    break

        # If there are no caches that are useful return an empty list.
        if not intervals:
            return []

        # optimal_covers[i] is a tuple (score, caches)
        # where score is the number of layer unions saved and caches is just a list caches
        # optimal_covers[i] considers only layers up to and including interval[i].
        optimal_covers = [None for _ in len(intervals)]

        # Base case: only the first interval is considered
        optimal_covers[0] = (len(intervals[0][2]) - 1, intervals[0][2])

        # Non-base cases: only the first i intervals are considered
        for i in range(1, len(intervals)):
            tup_i = intervals[i][2]
            score_i = len(tup_i) - 1

            # Option 1: Exclude the ith interval
            score_without, selection_without = optimal_covers[i-1]

            # Option 2: Include the ith interval
            j = find_last_non_overlapping_interval(i)
            if j != -1:
                score_with = score_i + optimal_covers[j][0]
                selection_with = optimal_covers[j][1] + [tup_i]
            else:
                score_with = score_i
                selection_with = [tup_i]

        # Choose Option 1 or 2: Which one saves more layer unions?
        if (score_with > score_without):
            optimal_covers[i] = (score_with, selection_with)
        else:
            optimal_covers[i] = (score_without, selection_without)

        return optimal_covers[-1][2]


def find_last_non_overlapping_interval(idx: int, intervals: List[int]) -> int:
    '''
    Helper function. Implements binary search for the rightmost interval that ends
    before the idxth interval.

    Args:
        idx (int): The index of the interval we are currently considering.
        intervals (List[int]): All the intervals ordered by their endpoint
    Returns:
        int: The index of the rightmost interval that is to the left of intervals[idx].
            If such an interval does not exist return -1.
    '''
    lo, hi = 0, idx - 1
    result = -1
    start_i = intervals[idx][0]
    while lo <= hi:
        mid = (lo + hi) // 2
        if intervals[mid][1] <= start_i:
            result = mid
            lo = mid + 1
        else:
            hi = mid - 1
    return result