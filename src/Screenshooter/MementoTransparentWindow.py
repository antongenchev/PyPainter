from src.Memento import Memento
from src.config import config

class MementoTransparentWindow(Memento):
    def is_related(self, m:'Memento') -> bool:
        '''
        If the source is the PyPainter and
        '''
        if self._source == 'Screenshooter' and m._source == 'Screenshooter':
            # If the source Screenshooter and the events happened quickly one after another they are related
            if self._timestamp_created - m._timestamp_created < config['mementos']['time_limits']['MementoTransparentWindow']:
                return True
        return False