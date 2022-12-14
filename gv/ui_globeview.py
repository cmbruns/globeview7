# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'globeview.ui'
##
## Created by: Qt User Interface Compiler version 6.2.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QAbstractSpinBox, QApplication, QComboBox, QDoubleSpinBox,
    QGroupBox, QHBoxLayout, QLabel, QListWidgetItem,
    QMainWindow, QMenu, QMenuBar, QPushButton,
    QSizePolicy, QSpacerItem, QSplitter, QStatusBar,
    QVBoxLayout, QWidget)

from geocanvas import GeoCanvas
from gv.layer import LayerListWidget

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 600)
        self.actionQuit = QAction(MainWindow)
        self.actionQuit.setObjectName(u"actionQuit")
        self.actionReset_View = QAction(MainWindow)
        self.actionReset_View.setObjectName(u"actionReset_View")
        self.actionFull_Screen = QAction(MainWindow)
        self.actionFull_Screen.setObjectName(u"actionFull_Screen")
        self.actionFull_Screen.setCheckable(True)
        self.actionNormal_View = QAction(MainWindow)
        self.actionNormal_View.setObjectName(u"actionNormal_View")
        self.actionBookmark_This_View = QAction(MainWindow)
        self.actionBookmark_This_View.setObjectName(u"actionBookmark_This_View")
        self.actionSave_Screenshot = QAction(MainWindow)
        self.actionSave_Screenshot.setObjectName(u"actionSave_Screenshot")
        self.actionClear_All_Bookmarks = QAction(MainWindow)
        self.actionClear_All_Bookmarks.setObjectName(u"actionClear_All_Bookmarks")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout_4 = QHBoxLayout(self.centralwidget)
        self.horizontalLayout_4.setSpacing(0)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.widget_8 = QWidget(self.centralwidget)
        self.widget_8.setObjectName(u"widget_8")
        self.horizontalLayout_5 = QHBoxLayout(self.widget_8)
        self.horizontalLayout_5.setSpacing(0)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.splitter_2 = QSplitter(self.widget_8)
        self.splitter_2.setObjectName(u"splitter_2")
        self.splitter_2.setStyleSheet(u"QSplitter::handle {\n"
"    background-color: #99a;\n"
"}")
        self.splitter_2.setOrientation(Qt.Horizontal)
        self.splitter = QSplitter(self.splitter_2)
        self.splitter.setObjectName(u"splitter")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.splitter.sizePolicy().hasHeightForWidth())
        self.splitter.setSizePolicy(sizePolicy)
        self.splitter.setOrientation(Qt.Horizontal)
        self.leftArea_widget = QWidget(self.splitter)
        self.leftArea_widget.setObjectName(u"leftArea_widget")
        self.verticalLayout = QVBoxLayout(self.leftArea_widget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBox_2 = QGroupBox(self.leftArea_widget)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.verticalLayout_3 = QVBoxLayout(self.groupBox_2)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.layers_listWidget = LayerListWidget(self.groupBox_2)
        self.layers_listWidget.setObjectName(u"layers_listWidget")

        self.verticalLayout_3.addWidget(self.layers_listWidget)


        self.verticalLayout.addWidget(self.groupBox_2)

        self.splitter.addWidget(self.leftArea_widget)
        self.widget_3 = QWidget(self.splitter)
        self.widget_3.setObjectName(u"widget_3")
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy1.setHorizontalStretch(2)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.widget_3.sizePolicy().hasHeightForWidth())
        self.widget_3.setSizePolicy(sizePolicy1)
        self.verticalLayout_7 = QVBoxLayout(self.widget_3)
        self.verticalLayout_7.setSpacing(0)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.verticalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.openGLWidget = GeoCanvas(self.widget_3)
        self.openGLWidget.setObjectName(u"openGLWidget")
        sizePolicy1.setHeightForWidth(self.openGLWidget.sizePolicy().hasHeightForWidth())
        self.openGLWidget.setSizePolicy(sizePolicy1)

        self.verticalLayout_7.addWidget(self.openGLWidget)

        self.splitter.addWidget(self.widget_3)
        self.splitter_2.addWidget(self.splitter)
        self.rightArea_widget = QWidget(self.splitter_2)
        self.rightArea_widget.setObjectName(u"rightArea_widget")
        self.verticalLayout_2 = QVBoxLayout(self.rightArea_widget)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.groupBox_4 = QGroupBox(self.rightArea_widget)
        self.groupBox_4.setObjectName(u"groupBox_4")
        self.verticalLayout_8 = QVBoxLayout(self.groupBox_4)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.widget = QWidget(self.groupBox_4)
        self.widget.setObjectName(u"widget")
        self.horizontalLayout_7 = QHBoxLayout(self.widget)
        self.horizontalLayout_7.setSpacing(6)
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.horizontalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.label_2 = QLabel(self.widget)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.horizontalLayout_7.addWidget(self.label_2)

        self.lonSpinBox = QDoubleSpinBox(self.widget)
        self.lonSpinBox.setObjectName(u"lonSpinBox")
        self.lonSpinBox.setWrapping(True)
        self.lonSpinBox.setButtonSymbols(QAbstractSpinBox.PlusMinus)
        self.lonSpinBox.setAccelerated(True)
        self.lonSpinBox.setKeyboardTracking(False)
        self.lonSpinBox.setDecimals(4)
        self.lonSpinBox.setMinimum(-180.000000000000000)
        self.lonSpinBox.setMaximum(180.000000000000000)
        self.lonSpinBox.setSingleStep(5.000000000000000)

        self.horizontalLayout_7.addWidget(self.lonSpinBox)


        self.verticalLayout_8.addWidget(self.widget)

        self.widget_2 = QWidget(self.groupBox_4)
        self.widget_2.setObjectName(u"widget_2")
        self.horizontalLayout_8 = QHBoxLayout(self.widget_2)
        self.horizontalLayout_8.setSpacing(6)
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.horizontalLayout_8.setContentsMargins(0, 0, 0, 0)
        self.label_3 = QLabel(self.widget_2)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.horizontalLayout_8.addWidget(self.label_3)

        self.latSpinBox = QDoubleSpinBox(self.widget_2)
        self.latSpinBox.setObjectName(u"latSpinBox")
        self.latSpinBox.setWrapping(False)
        self.latSpinBox.setButtonSymbols(QAbstractSpinBox.PlusMinus)
        self.latSpinBox.setAccelerated(True)
        self.latSpinBox.setKeyboardTracking(False)
        self.latSpinBox.setDecimals(4)
        self.latSpinBox.setMinimum(-90.000000000000000)
        self.latSpinBox.setMaximum(90.000000000000000)
        self.latSpinBox.setSingleStep(5.000000000000000)

        self.horizontalLayout_8.addWidget(self.latSpinBox)


        self.verticalLayout_8.addWidget(self.widget_2)


        self.verticalLayout_2.addWidget(self.groupBox_4)

        self.groupBox = QGroupBox(self.rightArea_widget)
        self.groupBox.setObjectName(u"groupBox")
        self.verticalLayout_6 = QVBoxLayout(self.groupBox)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.projectionComboBox = QComboBox(self.groupBox)
        self.projectionComboBox.addItem("")
        self.projectionComboBox.addItem("")
        self.projectionComboBox.addItem("")
        self.projectionComboBox.addItem("")
        self.projectionComboBox.addItem("")
        self.projectionComboBox.addItem("")
        self.projectionComboBox.addItem("")
        self.projectionComboBox.setObjectName(u"projectionComboBox")

        self.verticalLayout_6.addWidget(self.projectionComboBox)


        self.verticalLayout_2.addWidget(self.groupBox)

        self.groupBox_3 = QGroupBox(self.rightArea_widget)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.groupBox_3.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.verticalLayout_5 = QVBoxLayout(self.groupBox_3)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.widget_9 = QWidget(self.groupBox_3)
        self.widget_9.setObjectName(u"widget_9")
        self.horizontalLayout_6 = QHBoxLayout(self.widget_9)
        self.horizontalLayout_6.setSpacing(0)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.horizontalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.widget_5 = QWidget(self.widget_9)
        self.widget_5.setObjectName(u"widget_5")
        self.widget_5.setLayoutDirection(Qt.LeftToRight)
        self.verticalLayout_4 = QVBoxLayout(self.widget_5)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.widget_6 = QWidget(self.widget_5)
        self.widget_6.setObjectName(u"widget_6")
        self.horizontalLayout_2 = QHBoxLayout(self.widget_6)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_3)

        self.northUpButton = QPushButton(self.widget_6)
        self.northUpButton.setObjectName(u"northUpButton")
        sizePolicy2 = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.northUpButton.sizePolicy().hasHeightForWidth())
        self.northUpButton.setSizePolicy(sizePolicy2)

        self.horizontalLayout_2.addWidget(self.northUpButton)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_4)


        self.verticalLayout_4.addWidget(self.widget_6)

        self.widget_4 = QWidget(self.widget_5)
        self.widget_4.setObjectName(u"widget_4")
        self.horizontalLayout = QHBoxLayout(self.widget_4)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.northLeftButton = QPushButton(self.widget_4)
        self.northLeftButton.setObjectName(u"northLeftButton")

        self.horizontalLayout.addWidget(self.northLeftButton)

        self.northRightButton = QPushButton(self.widget_4)
        self.northRightButton.setObjectName(u"northRightButton")

        self.horizontalLayout.addWidget(self.northRightButton)


        self.verticalLayout_4.addWidget(self.widget_4)

        self.widget_7 = QWidget(self.widget_5)
        self.widget_7.setObjectName(u"widget_7")
        self.horizontalLayout_3 = QHBoxLayout(self.widget_7)
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer)

        self.northDownButton = QPushButton(self.widget_7)
        self.northDownButton.setObjectName(u"northDownButton")
        sizePolicy2.setHeightForWidth(self.northDownButton.sizePolicy().hasHeightForWidth())
        self.northDownButton.setSizePolicy(sizePolicy2)

        self.horizontalLayout_3.addWidget(self.northDownButton)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_2)


        self.verticalLayout_4.addWidget(self.widget_7)


        self.horizontalLayout_6.addWidget(self.widget_5)

        self.horizontalSpacer_5 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_6.addItem(self.horizontalSpacer_5)


        self.verticalLayout_5.addWidget(self.widget_9)

        self.label = QLabel(self.groupBox_3)
        self.label.setObjectName(u"label")

        self.verticalLayout_5.addWidget(self.label)

        self.azimuthSpinBox = QDoubleSpinBox(self.groupBox_3)
        self.azimuthSpinBox.setObjectName(u"azimuthSpinBox")
        self.azimuthSpinBox.setWrapping(True)
        self.azimuthSpinBox.setAccelerated(True)
        self.azimuthSpinBox.setKeyboardTracking(False)
        self.azimuthSpinBox.setMaximum(360.000000000000000)
        self.azimuthSpinBox.setSingleStep(5.000000000000000)

        self.verticalLayout_5.addWidget(self.azimuthSpinBox)


        self.verticalLayout_2.addWidget(self.groupBox_3)

        self.altitudeGroupBox = QGroupBox(self.rightArea_widget)
        self.altitudeGroupBox.setObjectName(u"altitudeGroupBox")
        self.altitudeGroupBox.setEnabled(False)
        self.verticalLayout_9 = QVBoxLayout(self.altitudeGroupBox)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.altitudeComboBox = QComboBox(self.altitudeGroupBox)
        self.altitudeComboBox.addItem("")
        self.altitudeComboBox.addItem("")
        self.altitudeComboBox.addItem("")
        self.altitudeComboBox.addItem("")
        self.altitudeComboBox.addItem("")
        self.altitudeComboBox.addItem("")
        self.altitudeComboBox.addItem("")
        self.altitudeComboBox.addItem("")
        self.altitudeComboBox.addItem("")
        self.altitudeComboBox.setObjectName(u"altitudeComboBox")

        self.verticalLayout_9.addWidget(self.altitudeComboBox)

        self.altitudeSpinBox = QDoubleSpinBox(self.altitudeGroupBox)
        self.altitudeSpinBox.setObjectName(u"altitudeSpinBox")
        self.altitudeSpinBox.setAccelerated(True)
        self.altitudeSpinBox.setKeyboardTracking(False)
        self.altitudeSpinBox.setDecimals(0)
        self.altitudeSpinBox.setMinimum(1.000000000000000)
        self.altitudeSpinBox.setMaximum(1000000.000000000000000)
        self.altitudeSpinBox.setSingleStep(500.000000000000000)
        self.altitudeSpinBox.setStepType(QAbstractSpinBox.AdaptiveDecimalStepType)
        self.altitudeSpinBox.setValue(6378.000000000000000)

        self.verticalLayout_9.addWidget(self.altitudeSpinBox)


        self.verticalLayout_2.addWidget(self.altitudeGroupBox)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer)

        self.splitter_2.addWidget(self.rightArea_widget)

        self.horizontalLayout_5.addWidget(self.splitter_2)


        self.horizontalLayout_4.addWidget(self.widget_8)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 800, 22))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuView = QMenu(self.menubar)
        self.menuView.setObjectName(u"menuView")
        self.menuBookmarks = QMenu(self.menuView)
        self.menuBookmarks.setObjectName(u"menuBookmarks")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        font = QFont()
        self.statusbar.setFont(font)
        MainWindow.setStatusBar(self.statusbar)
#if QT_CONFIG(shortcut)
        self.label_2.setBuddy(self.lonSpinBox)
        self.label_3.setBuddy(self.lonSpinBox)
        self.label.setBuddy(self.azimuthSpinBox)
#endif // QT_CONFIG(shortcut)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuView.menuAction())
        self.menuFile.addAction(self.actionSave_Screenshot)
        self.menuFile.addAction(self.actionQuit)
        self.menuView.addAction(self.actionReset_View)
        self.menuView.addAction(self.actionFull_Screen)
        self.menuView.addAction(self.menuBookmarks.menuAction())
        self.menuBookmarks.addAction(self.actionBookmark_This_View)
        self.menuBookmarks.addAction(self.actionClear_All_Bookmarks)
        self.menuBookmarks.addSeparator()

        self.retranslateUi(MainWindow)

        self.projectionComboBox.setCurrentIndex(2)
        self.altitudeComboBox.setCurrentIndex(6)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle("")
        self.actionQuit.setText(QCoreApplication.translate("MainWindow", u"Quit", None))
        self.actionReset_View.setText(QCoreApplication.translate("MainWindow", u"Reset View", None))
        self.actionFull_Screen.setText(QCoreApplication.translate("MainWindow", u"Full Screen", None))
#if QT_CONFIG(shortcut)
        self.actionFull_Screen.setShortcut(QCoreApplication.translate("MainWindow", u"F", None))
#endif // QT_CONFIG(shortcut)
        self.actionNormal_View.setText(QCoreApplication.translate("MainWindow", u"Normal_View", None))
#if QT_CONFIG(shortcut)
        self.actionNormal_View.setShortcut(QCoreApplication.translate("MainWindow", u"Esc", None))
#endif // QT_CONFIG(shortcut)
        self.actionBookmark_This_View.setText(QCoreApplication.translate("MainWindow", u"Bookmark This View...", None))
        self.actionSave_Screenshot.setText(QCoreApplication.translate("MainWindow", u"Save Screenshot...", None))
        self.actionClear_All_Bookmarks.setText(QCoreApplication.translate("MainWindow", u"Clear All Bookmarks", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("MainWindow", u"Layers", None))
        self.groupBox_4.setTitle(QCoreApplication.translate("MainWindow", u"Center Location", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Longitude", None))
        self.lonSpinBox.setSuffix(QCoreApplication.translate("MainWindow", u"\u00b0", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Latitude", None))
        self.latSpinBox.setSuffix(QCoreApplication.translate("MainWindow", u"\u00b0", None))
        self.groupBox.setTitle(QCoreApplication.translate("MainWindow", u"Display Projection", None))
        self.projectionComboBox.setItemText(0, QCoreApplication.translate("MainWindow", u"Perspective", None))
        self.projectionComboBox.setItemText(1, QCoreApplication.translate("MainWindow", u"Orthographic", None))
        self.projectionComboBox.setItemText(2, QCoreApplication.translate("MainWindow", u"Azimuthal Equal Area", None))
        self.projectionComboBox.setItemText(3, QCoreApplication.translate("MainWindow", u"Equirectangular", None))
        self.projectionComboBox.setItemText(4, QCoreApplication.translate("MainWindow", u"Azimuthal Equidistant", None))
        self.projectionComboBox.setItemText(5, QCoreApplication.translate("MainWindow", u"Stereographic", None))
        self.projectionComboBox.setItemText(6, QCoreApplication.translate("MainWindow", u"Gnomonic", None))

        self.groupBox_3.setTitle(QCoreApplication.translate("MainWindow", u"North Direction", None))
        self.northUpButton.setText(QCoreApplication.translate("MainWindow", u"Up", None))
        self.northLeftButton.setText(QCoreApplication.translate("MainWindow", u"Left", None))
        self.northRightButton.setText(QCoreApplication.translate("MainWindow", u"Right", None))
        self.northDownButton.setText(QCoreApplication.translate("MainWindow", u"Down", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Up Azimuth (degrees)", None))
        self.azimuthSpinBox.setSuffix(QCoreApplication.translate("MainWindow", u"\u00b0", None))
        self.altitudeGroupBox.setTitle(QCoreApplication.translate("MainWindow", u"Altitude Above Surface", None))
        self.altitudeComboBox.setItemText(0, QCoreApplication.translate("MainWindow", u"Custom", None))
        self.altitudeComboBox.setItemText(1, QCoreApplication.translate("MainWindow", u"Commercial Airline Jet (12.8 km)", None))
        self.altitudeComboBox.setItemText(2, QCoreApplication.translate("MainWindow", u"SR-71 Spy Plane (25.9 km)", None))
        self.altitudeComboBox.setItemText(3, QCoreApplication.translate("MainWindow", u"Shepard Mercury-Redstone 3 (188 km)", None))
        self.altitudeComboBox.setItemText(4, QCoreApplication.translate("MainWindow", u"Gagarin Vostok-1 (254 km)", None))
        self.altitudeComboBox.setItemText(5, QCoreApplication.translate("MainWindow", u"International Space Station (408 km)", None))
        self.altitudeComboBox.setItemText(6, QCoreApplication.translate("MainWindow", u"Earth Radius (6378 km)", None))
        self.altitudeComboBox.setItemText(7, QCoreApplication.translate("MainWindow", u"Geosynchronous Satellite (36000 km)", None))
        self.altitudeComboBox.setItemText(8, QCoreApplication.translate("MainWindow", u"Earth-Moon  Distance (384000 km)", None))

        self.altitudeSpinBox.setSuffix(QCoreApplication.translate("MainWindow", u" km", None))
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
        self.menuView.setTitle(QCoreApplication.translate("MainWindow", u"View", None))
        self.menuBookmarks.setTitle(QCoreApplication.translate("MainWindow", u"Bookmarks", None))
    # retranslateUi

