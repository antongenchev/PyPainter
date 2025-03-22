"""
The class ElementListEmitter is an emitter for signals happening from
the ElementListGUI objects. ElementListEmitter is a singleton and all
ElementListGUI objects rely on the same ElementListEmitter to send
signals.

The reason behind using a separate emitter class is to avoid the
coupling of ElementListGUI and Layer with objects that are higher up.
The two main alternatives are:
    1. Passing a reference from the ImageProcessor all the way down;
    2. Creating a signal chain Layer -> LayerList -> ImageProcessor.

The ElementListEmitter.emit can be used to emit signals. The information
that has to be provided to the ElementListEmitter should be of the form:
    (drawable_element, command, arg).
Where `command` comes from an IntEnum defined in ElementListEmitter.
`arg` is an integer used to send additional information e.g. the index
at which a drawable elemnt is added or moved.
"""

from PyQt5.QtCore import QObject, pyqtSignal
from enum import IntEnum, auto
from src.DrawableElement import DrawableElement


class ElementListEmitter(QObject):
    """
    Singleton emitter for signals from ElementListGUI instances.
    Ensures decoupling between ElementListGUI and higher-level objects
    like ImageProcessor.
    """
    _instance = None


    class Command(IntEnum):
        SELECT = 0  # NO arg needed
        MOVE = auto()  # arg = the index at which the element is moved
        DELETE = auto()  # NO arg needed
        COPY_PASTE = auto()  # arg = the index at which it is pasted
        VISIBILITY_ON = auto() # NO arg needed
        VISIBILITY_OFF = auto() # NO arg needed


    # Signals (element, arg) or (element)
    element_selected = pyqtSignal(DrawableElement)
    element_moved = pyqtSignal(DrawableElement, int)
    element_deleted = pyqtSignal(DrawableElement)
    copy_pasted = pyqtSignal(DrawableElement, int)
    visibility_toggled = pyqtSignal(DrawableElement, bool)

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ElementListEmitter, cls).__new__(cls)
            super(ElementListEmitter, cls._instance).__init__()
        return cls._instance

    def emit(self, element: DrawableElement, command: Command, arg: int = 0):
        """Emit an event signal with given parameters."""
        match command:
            case self.Command.SELECT:
                self.element_selected.emit(element)
            case self.Command.MOVE:
                self.element_moved.emit(element, arg)
            case self.Command.DELETE:
                self.element_deleted.emit(element)
            case self.Command.COPY_PASTE:
                self.copy_pasted.emit(element, arg)
            case self.Command.VISIBILITY_ON:
                self.visibility_toggled.emit(element, True)
            case self.Command.VISIBILITY_OFF:
                self.visibility_toggled.emit(element, False)

    ######################## Shortcut methods ##########################
    def select(self, element: DrawableElement):
        """Emit a select event."""
        self.emit(element, self.Command.SELECT, 0)

    def move(self, element: DrawableElement, index: int):
        """Emit a move event with the target index."""
        self.emit(element, self.Command.MOVE, index)

    def delete(self, element: DrawableElement):
        """Emit a delete event."""
        self.emit(element, self.Command.DELETE, 0)

    def copy_paste(self, element: DrawableElement, index: int):
        """Emit a copy-paste event with the target index."""
        self.emit(element, self.Command.COPY_PASTE, index)

    def toggle_visibility(self, element: DrawableElement, visibile: bool):
        """Emit a toggle-visiblity event."""
        if visibile:
            self.emit(element, self.Command.VISIBILITY_ON)
        else:
            self.emit(element, self.Command.VISIBILITY_OFF)
    ####################################################################


element_list_emitter = ElementListEmitter()