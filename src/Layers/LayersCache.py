from typing import Tuple, List, Any
from datetime import datetime

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

    def get_intersection(self, layer: int) -> List[Tuple[int]]:
        '''
        Get all the layer tuples in the cache that contain the layer provided.

        Args:
            layer (int): The layer provided.
        Returns:
            List[Tuple[int]]: The layer tuples in the cache that contain the layer provided.
        '''

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