import sys
from PySide6 import QtWidgets

from main_window import GlobeViewMainWindow


def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("GlobeView")  # Not "python"
    app.setOrganizationName("Brunsgen Scientific")
    # app.setApplicationDisplayName("ApplicationDisplayName")  # Overrides setApplicationName in title bar
    window = GlobeViewMainWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
