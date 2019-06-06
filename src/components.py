from PyQt5.QtWidgets import (QMainWindow, QWidget, QAction, QPushButton,
    QHBoxLayout, QVBoxLayout, QGridLayout, QCheckBox, QSlider, QLabel,
    QApplication, QStyleOptionSlider, QComboBox, QToolTip)
from PyQt5.QtGui import QIcon
from PyQt5 import QtCore

# https://stackoverflow.com/a/31658984
class TipSlider(QSlider):
    def __init__(self, *args, tip_offset=QtCore.QPoint(0, -45), **kwargs):
        super(QSlider, self).__init__(*args)
        self.tip_offset = tip_offset

        parent = kwargs.get("parent", None)

        self.style = QApplication.style()
        self.opt = QStyleOptionSlider()

        self.valueChanged.connect(self.show_tip)

        # this seems to do nothing ??
        if parent != None:
            pallete = getattr(self.parent, "app_pallete", None)
            if pallete != None:
                self.setPalette(pallete)

    def show_tip(self, _):
        self.initStyleOption(self.opt)
        rectHandle = self.style.subControlRect(self.style.CC_Slider,
            self.opt, self.style.SC_SliderHandle)

        pos_local = rectHandle.topLeft() + self.tip_offset
        pos_global = self.mapToGlobal(pos_local)
        QToolTip.showText(pos_global, str(self.value()), self)



class SettingsWindow(QMainWindow):
    """docstring for SettingsWindow."""

    def __init__(self, parent):
        super(SettingsWindow, self).__init__(parent)
        self.parent = parent
        self.title = _("Settings")
        self.icon = QIcon('Icon.ico')
        # main_menu = self.menuBar()
        self.init_ui()

    # Check the user settings and set everything accordingly
    def load_settings(self):
        for val in self.parent.settings:
            if val == "keep_vals":
                self.keep_vals_check.setChecked(self.parent.settings[val])
            elif val == "lang":
                index = self.choose_lang_combo.findText(self.parent.settings[val],
                    QtCore.Qt.MatchFixedString)
                if index >= 0:
                    self.choose_lang_combo.setCurrentIndex(index)
            elif val == "log_level":
                index = self.log_level_combo.findText(self.parent.settings[val],
                    QtCore.Qt.MatchFixedString)
                if index >= 0:
                    self.log_level_combo.setCurrentIndex(index)
            elif val == "app_theme":
                index = self.app_theme_combo.findText(self.parent.settings[val],
                    QtCore.Qt.MatchFixedString)
                if index >= 0:
                    self.app_theme_combo.setCurrentIndex(index)
            else:
                msg = "%s: %s" % (_("Found invalid setting"), val)
                self.logger.error(msg)

    def save_settings(self):
        try:
            kv = self.keep_vals_check.isChecked()
            self.parent.settings["keep_vals"] = kv
            lang = str(self.choose_lang_combo.currentText())
            self.parent.settings["lang"] = lang
            log_level = str(self.log_level_combo.currentText())
            self.parent.settings["log_level"] = log_level
            app_theme = str(self.app_theme_combo.currentText())
            self.parent.settings["app_theme"] = app_theme
            log_level = str(self.log_level_combo.currentText())
            self.parent.do_save()
        except KeyError as e:
            msg = _("Failed to save settings, please delete your setting.pckl and values.pckl files, and restart the app")
            self.parent.gui_logger(msg)
            self.parent.logger.error(msg)


    # overrides close event, removes settings_window's reference from parent
    def closeEvent(self, event):
        self.parent.settings_window = None
        event.accept() # let the window close

    def init_ui(self):
        # Main window
        window = QWidget(self)
        # this seems to break the app
        # self.setCentralWidget(self)
        self.status_bar = self.statusBar()
        self.setWindowTitle(self.title)
        # self.setWindowIcon(self.icon)
        # Buttons / sliders / checkboxes --------------
        self.choose_lang_combo = QComboBox()
        self.choose_lang_combo.setStatusTip(_("Language of the app"))
        for lang in self.parent.available_langs:
            self.choose_lang_combo.addItem(lang)

        self.app_theme_combo = QComboBox()
        self.app_theme_combo.setStatusTip(_("Theme of the app"))
        for theme in self.parent.user_themes:
            self.app_theme_combo.addItem(theme)

        self.log_level_combo = QComboBox()
        self.log_level_combo.setStatusTip(_("Console log level"))
        for ll in self.parent.log_levels:
            self.log_level_combo.addItem(ll)

        self.keep_vals_check = QCheckBox()
        msg = _("Keeps your source, destination, etc.. stored in a file and loads it on startup")
        self.keep_vals_check.setStatusTip(msg)

        self.save_button_label = QLabel(_("Apply settings"))
        self.save_button = QPushButton(_("apply"))
        self.save_button.clicked.connect(self.save_settings)
        self.save_button.setStatusTip(_("Saves your current settings to a file"))

        # Layout ---------------------
        # horizontal grid
        h_grid = QGridLayout()
        h_grid.setSpacing(5)
        # addWidget(widget,fromRow,fromCol,rowSpan,colSpan)
        h_grid.addWidget(QLabel(_("Language:")),0,0)
        h_grid.addWidget(self.choose_lang_combo,0,2)
        h_grid.addWidget(QLabel(_("Theme:")),1,0)
        h_grid.addWidget(self.app_theme_combo,1,2)
        h_grid.addWidget(QLabel(_("Log level:")),2,0)
        h_grid.addWidget(self.log_level_combo,2,2)
        h_grid.addWidget(QLabel(_("Keep values:")),3,0)
        h_grid.addWidget(self.keep_vals_check,3,2)
        h_grid.addWidget(self.save_button_label,6,0)
        h_grid.addWidget(self.save_button,6,2)

        # set layouts and Geometry
        window.setLayout(h_grid)
        # this moves the widget not really necessary
        # if the geometry is set
        # window.move(100, 100)
        # Set the Main window and widget geometry
        # # x: screen x pos, y: screen y pos, width, height
        window.setGeometry(0, 0, 300, 300)
        self.setGeometry(600, 600, 260, 350)
        self.setFixedSize(450,300)
        self.load_settings()
        pallete = getattr(self.parent, "app_pallete", None)
        if pallete != None:
            window.setPalette(pallete)
        self.show()
