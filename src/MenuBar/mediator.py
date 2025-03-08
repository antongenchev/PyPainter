from src.MenuBar.MenuBar import MenuBar

def MenuBarMediator(PyPainter) -> MenuBar:
    menu_bar = MenuBar()
    menu_bar.callback_update_image = PyPainter.update_image
    return menu_bar