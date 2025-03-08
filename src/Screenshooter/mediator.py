'''
Create a Screenshooter and connect it to the main part of
the app (the PyPainter class). The reason behind using this
Mediator callable is to not have to pass a reference to the
main part of the app to a feature like the Screenshooter.
This way we can connect the Screenshooter without letting
it use the PyPainter for unneccessary things.
'''
from src.Screenshooter.Screenshooter import Screenshooter

def ScreenshooterMediator(PyPainter) -> Screenshooter:
    screenshooter = Screenshooter(
        callback_capture = PyPainter.update_image
    )
    PyPainter.close_application_signal.connect(screenshooter.close)
    return screenshooter