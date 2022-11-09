from PySide6.QtGui import QAction
from gv.view_state import ViewState


class Bookmark(object):
    def __init__(self, name: str, view_state: ViewState, ui_parent, updatable):
        self.name = name
        self.view_state = view_state
        self.view_state_memento = self.view_state.memento()  # Persist original values
        self.updatable = updatable
        self.action = QAction(name, ui_parent)
        self.action.triggered.connect(self.navigate_to_bookmark)

    def restore_memento(self, memento):
        self.name = memento["name"]
        self.view_state_memento = memento["view_state_memento"]

    def memento(self):
        return {
            "name": self.name,
            "view_state_memento": self.view_state_memento,
        }

    def navigate_to_bookmark(self):
        self.view_state.restore_memento(self.view_state_memento)
        self.updatable.update()
