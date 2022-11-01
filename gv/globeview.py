import sys
from PySide6 import QtWidgets
from PySide6.QtGui import QSurfaceFormat

from main_window import GlobeViewMainWindow


def main():
    # Set OpenGL version *before* constructing QApplication()
    gl_format = QSurfaceFormat()
    gl_format.setMajorVersion(4)
    gl_format.setMinorVersion(6)
    gl_format.setProfile(QSurfaceFormat.CoreProfile)
    QSurfaceFormat.setDefaultFormat(gl_format)
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("GlobeView")  # Not "python"
    app.setOrganizationName("Brunsgen Scientific")
    # app.setApplicationDisplayName("ApplicationDisplayName")  # Overrides setApplicationName in title bar
    window = GlobeViewMainWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
