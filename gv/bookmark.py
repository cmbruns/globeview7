from PySide6.QtGui import QAction
from gv.view_state import ViewState


class Bookmark(object):
    def __init__(self, name: str, view_state: ViewState, ui_parent, updatable):
        self.name = name
        self.view_state = view_state
        self.memento = self.view_state.memento()  # Persist original values
        self.updatable = updatable
        self.action = QAction(name, ui_parent)
        self.action.triggered.connect(self.navigate_to_bookmark)

    def navigate_to_bookmark(self):
        self.view_state.restore_memento(self.memento)
        self.updatable.update()
