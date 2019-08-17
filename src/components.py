# <STPDF convert scans to pdf>
# Copyright (C) <2019>  <Alexandre Cortegaça>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import locale
import gettext
from PyQt5.QtWidgets import (QMainWindow, QWidget, QPushButton,
                             QGridLayout, QCheckBox, QSlider, QLabel,
                             QApplication, QStyleOptionSlider, QComboBox,
                             QToolTip, QMessageBox)
from PyQt5.QtGui import QIcon, QDesktopServices
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QThread, pyqtSignal, QUrl
from _version import (__version__, __version2__,
                      __releaseDate__, __releaseDate2__,
                      __developer__, __developer2__, __devhome__)

from stpdf.core.stpdf_core import STPDFCore


class ThreadedConverter(QThread):
    exception_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, cvt_args):
        QThread.__init__(self)
        self.cvt_args = cvt_args

    def do_stop(self):
        self.is_running = False

    def run(self):
        self.is_running = True
        cvt_args = self.cvt_args
        fl = cvt_args["fl"]
        fd = cvt_args["fd"]
        di = cvt_args["di"]
        ds = cvt_args["ds"]
        sa = cvt_args["sa"]
        pd = cvt_args["pd"]
        dc = cvt_args["dc"]
        la = cvt_args["lang"]
        converter = STPDFCore(fl, fd, split=(ds, sa),
                              deskew=di, lang=la,
                              make_pdf=pd, copy_files=dc)
        try:
            for line in converter.process_all():
                # Implementing the stop functionality here
                # causes the app to hang for a few seconds
                if not self.is_running:
                    brk_msg = _("Stop received, terminating the converter")
                    print(brk_msg)
                    self.progress_signal.emit(brk_msg)
                    break
                print("alive")
                self.progress_signal.emit(line)
        except Exception as e:
            print("THREAD_EXCEPTION: %s" % e)
            en = e.__class__.__name__
            msg = ""
            if en == "TesseractNotFoundError":
                msg = _("Failed to find tesseract on your system, verify it is installed and on PATH environment variable")
            else:
                msg = "%s: %s" % (_("Thread exception"), str(e))
            self.exception_signal.emit(msg)
        # If a stop wasn't requested send the finished signal
        # this is to avoid calling do_stop multiple times
        self.finished.emit()


# https://stackoverflow.com/a/31658984
class TipSlider(QSlider):

    def __init__(self, *args, tip_offset=QtCore.QPoint(0, -45), **kwargs):
        super(TipSlider, self).__init__(*args)
        self.tip_offset = tip_offset

        parent = kwargs.get("parent", None)

        self.style = QApplication.style()
        self.opt = QStyleOptionSlider()

        self.valueChanged.connect(self.show_tip)

        # this seems to do nothing ??
        if parent is not None:
            pallete = getattr(self.parent, "app_pallete", None)
            if pallete is not None:
                self.setPalette(pallete)

    def show_tip(self, _):
        self.initStyleOption(self.opt)
        rectHandle = self.style.subControlRect(self.style.CC_Slider,
                                               self.opt,
                                               self.style.SC_SliderHandle)

        pos_local = rectHandle.topLeft() + self.tip_offset
        pos_global = self.mapToGlobal(pos_local)
        QToolTip.showText(pos_global, str(self.value()), self)


class AboutWindow(QMainWindow):
    """docstring for AboutWindow."""

    def __init__(self, parent):
        super(AboutWindow, self).__init__(parent)
        self.parent = parent
        gettext.install("stpdf_components")
        lang = self.parent.app_lang
        modl = "%s_components" % lang
        current_locale, __ = locale.getdefaultlocale()
        cl = current_locale.split("_")
        if lang != "en":
            if lang != cl[0]:
                current_locale = "%s_%s" % (lang, lang.upper())
            lang = gettext.translation(modl,
                                       "locale/", [current_locale])
            lang.install()
        self.title = _("About")
        self.init_ui()

    # overrides close event, removes settings_window's reference from parent
    def closeEvent(self, event):
        self.parent.about_window = None
        # let the window close
        event.accept()

    def init_ui(self):
        # Main window
        window = QWidget(self)
        self.setWindowTitle(self.title)
        self.status_bar = self.statusBar()

        # Layout ---------------------
        # horizontal grid
        h_grid = QGridLayout()
        h_grid.setSpacing(10)
        # addWidget(widget,fromRow,fromCol,rowSpan,colSpan)
        about_s = QLabel(_("About STPDF"))
        about_s.setFont(QtGui.QFont("Times", 15, QtGui.QFont.Bold))
        h_grid.addWidget(about_s, 0, 1)
        build = QLabel(_("Build with:"))
        build.setFont(QtGui.QFont("Times", 12, QtGui.QFont.Bold))
        h_grid.addWidget(build, 1, 0)
        bw = QPushButton("Python, PyQt5")
        bw.setEnabled(False)
        h_grid.addWidget(bw, 1, 1)
        version = QLabel(_("Version:"))
        version.setFont(QtGui.QFont("Times", 12, QtGui.QFont.Bold))
        h_grid.addWidget(version, 2, 0)
        ver = QPushButton(str(__version__))
        ver.setEnabled(False)
        ver.setStatusTip(str(__version2__))
        h_grid.addWidget(ver, 2, 1)
        r_date = QLabel(_("Release date:"))
        r_date.setFont(QtGui.QFont("Times", 12, QtGui.QFont.Bold))
        h_grid.addWidget(r_date, 3, 0)
        rdt = QPushButton(str(__releaseDate__))
        rdt.setEnabled(False)
        rdt.setStatusTip(str(__releaseDate2__))
        h_grid.addWidget(rdt, 3, 1)
        developed = QLabel(_("Developed by:"))
        developed.setFont(QtGui.QFont("Times", 12, QtGui.QFont.Bold))
        h_grid.addWidget(developed, 4, 0)
        dev = QPushButton(str(__developer__))
        dev.setStatusTip(str(__developer2__))
        dev.clicked.connect(
            lambda: QDesktopServices.openUrl(
                QUrl(str(__devhome__))
            )
        )
        h_grid.addWidget(dev, 4, 1)

        # set layouts and Geometry
        window.setLayout(h_grid)
        window.setGeometry(20, 0, 300, 200)
        self.setGeometry(500, 600, 260, 300)
        self.setFixedSize(400, 300)
        pallete = getattr(self.parent, "app_pallete", None)
        if pallete is not None:
            window.setPalette(pallete)
        self.show()


class SettingsWindow(QMainWindow):
    """docstring for SettingsWindow."""

    def __init__(self, parent):
        super(SettingsWindow, self).__init__(parent)
        self.parent = parent
        self.warning = None
        gettext.install("stpdf_components")
        lang = self.parent.app_lang
        modl = "%s_components" % lang
        current_locale, __ = locale.getdefaultlocale()
        cl = current_locale.split("_")
        if lang != "en":
            if lang != cl[0]:
                current_locale = "%s_%s" % (lang, lang.upper())
            lang = gettext.translation(modl,
                                       "locale/", [current_locale])
            lang.install()
        self.title = _("Settings")
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

    # manually calls save from the parent
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
        # let the window close
        event.accept()

    # opens a message box to ask the user to restart the app
    def lang_warning(self, event):
        if self.warning is None:
            r_msg = _("Please restart the app to apply the changes")
            info = QMessageBox.information(self, self.title, r_msg)

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
        self.choose_lang_combo.activated.connect(self.lang_warning)

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
        h_grid.addWidget(QLabel(_("Language:")), 0, 0)
        h_grid.addWidget(self.choose_lang_combo, 0, 2)
        h_grid.addWidget(QLabel(_("Theme:")), 1, 0)
        h_grid.addWidget(self.app_theme_combo, 1, 2)
        h_grid.addWidget(QLabel(_("Log level:")), 2, 0)
        h_grid.addWidget(self.log_level_combo, 2, 2)
        h_grid.addWidget(QLabel(_("Keep values:")), 3, 0)
        h_grid.addWidget(self.keep_vals_check, 3, 2)
        h_grid.addWidget(self.save_button_label, 6, 0)
        h_grid.addWidget(self.save_button, 6, 2)

        # set layouts and Geometry
        window.setLayout(h_grid)
        # this moves the widget not really necessary
        # if the geometry is set
        # window.move(100, 100)
        # Set the Main window and widget geometry
        # # x: screen x pos, y: screen y pos, width, height
        window.setGeometry(0, 0, 300, 300)
        self.setGeometry(600, 600, 260, 350)
        self.setFixedSize(450, 300)
        self.load_settings()
        pallete = getattr(self.parent, "app_pallete", None)
        if pallete is not None:
            window.setPalette(pallete)
        self.show()
