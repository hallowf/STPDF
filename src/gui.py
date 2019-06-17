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

# main modules
import sys
import pickle
import logging
import os
import gettext
import configparser
import locale
from multiprocessing import Process
from threading import Thread
# PyQt5
from PyQt5.QtWidgets import (QMainWindow, QWidget, QAction, qApp, QPushButton,
                             QHBoxLayout, QVBoxLayout, QGridLayout, QCheckBox,
                             QSlider, QLabel, QTextEdit, QFileDialog,
                             QApplication)
from PyQt5 import QtGui
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtCore import Qt, QUrl

# Custom components
from components import TipSlider, SettingsWindow, AboutWindow

# Backend and other requirements
from stpdf.custom_exceptions import DirMissing, OutDirNotEmpty
from stpdf.converter import Converter
from stpdf.utils import terminate_thread
from pytesseract.pytesseract import TesseractNotFoundError
from pytesseract import image_to_string
from PIL import Image


class MainWindow(QMainWindow):

    def __init__(self, parent):
        super().__init__()
        # App required parameters
        self.parent = parent
        self.stop_thread = False
        self.converter_thread = None
        self.title = 'STPDF'
        self.icon = QtGui.QIcon('stpdf.ico')
        self.user_themes = {"default": "default"}
        self.settings = None
        self.user_values = None
        self.retries = 0
        self.files_location = ""
        self.files_destination = ""
        self.app_lang = None
        self.log_levels = ["debug", "info", "warning", "error", "critical"]
        self.is_running = False
        self.settings_window = None
        self.about_window = None
        self.app_pallete = None
        self.has_tesseract = self.check_tesseract()
        self.available_langs = [
            "pt",
            "en",
            "es"
        ]
        # Console logger
        # logger is initialized in load_settings
        self.logger = None
        # Menus ---------------------
        # Main menu bar ---------------------
        main_menu = self.menuBar()
        # Save
        menu_save = QAction(_("Save"), self)
        menu_save.setShortcut("Ctrl+S")
        menu_save.setStatusTip(_("Save your settings to a file"))
        menu_save.triggered.connect(self.do_save)

        # Exit
        menu_exit = QAction(_("Exit"), self)
        menu_exit.setShortcut("Ctrl+Q")
        menu_exit.setStatusTip(_("Leave The App"))
        menu_exit.triggered.connect(qApp.quit)

        # Help link
        self.menu_help = QAction(_("Help"), self)
        self.menu_help.setStatusTip(_("Open the documentation in a browser"))
        self.menu_help.triggered.connect(
            lambda: QDesktopServices.openUrl(
                QUrl("https://github.com/hallowf/STPDF")))

        # About link
        self.menu_about = QAction(_("About STPDF"), self)
        self.menu_about.setStatusTip(_("Open info page"))
        self.menu_about.triggered.connect(
            lambda: self.on_menu_action("about"))
        # SettingsWindow
        self.menu_settings = QAction(_("Settings"), self)
        self.menu_settings.setShortcut("Ctrl+O")
        self.menu_settings.setStatusTip(_("Open settings window"))
        self.menu_settings.triggered.connect(
            lambda: self.on_menu_action("settings"))

        # Add menus
        file_menu = main_menu.addMenu(_("App"))
        file_menu.addAction(menu_save)
        file_menu.addAction(menu_exit)
        options_menu = main_menu.addMenu(_("Options"))
        options_menu.addAction(self.menu_settings)
        options_menu.addAction(self.menu_help)
        options_menu.addAction(self.menu_about)

        self.init_ui()

    # Initializes the user interface after loading settings and values
    def init_ui(self):
        # Main window
        window = QWidget(self)
        self.setCentralWidget(window)
        self.status_bar = self.statusBar()
        self.setWindowTitle(self.title)
        self.setWindowIcon(self.icon)
        # Buttons / sliders / checkboxes --------------
        self.source_button = QPushButton(_("Search"))
        self.source_button.clicked.connect(lambda: self.open_dir_dlg("source"))
        self.source_button.setStatusTip(_("Location of the files"))
        self.dest_button = QPushButton(_("Search"))
        self.dest_button.clicked.connect(lambda: self.open_dir_dlg("dest"))
        self.dest_button.setStatusTip(_("Destination of files created"))
        self.do_split = QCheckBox()
        self.do_split.setStatusTip(_("Split into multiple PDF files"))
        self.deskew_check = QCheckBox()
        if not self.has_tesseract:
            self.deskew_check.setEnabled(False)
            m = _("The app failed to find tesseract on your system")
            self.deskew_check.setStatusTip(m)
        else:
            self.deskew_check.setStatusTip(_("Removes rotation"))
        self.split_slider = TipSlider(Qt.Horizontal, parent=self)
        self.split_slider.setFocusPolicy(Qt.StrongFocus)
        self.split_slider.setTickPosition(QSlider.TicksBothSides)
        self.run_button = QPushButton(_("Run"))
        self.run_button.setStatusTip(_("Run the program"))
        self.run_button.clicked.connect(self.do_run)
        self.stop_button = QPushButton(_("Stop"))
        self.stop_button.setStatusTip(_("Stops the program"))
        self.stop_button.clicked.connect(self.do_stop)
        self.show_vals = QPushButton(_("Show values"))
        self.show_vals.clicked.connect(self.show_values)
        self.show_vals.setStatusTip(_("Show your current input values"))
        self.clean_button = QPushButton(_("Clean log"))
        self.clean_button.clicked.connect(self.clean_gui_logger)
        self.clean_button.setStatusTip(_("Cleans the current log"))
        # TODO: This options must be changeable in the settings
        self.split_slider.setTickInterval(10)
        self.split_slider.setSingleStep(1)
        # GUI logger
        self.gui_logger = QTextEdit(self)
        self.gui_logger.resize(150, 300)
        self.gui_logger.setDisabled(True)
        # Layouts ---------------------
        # Main vertical box
        v_box = QVBoxLayout()
        # Center horizontal box
        ch_box = QHBoxLayout()
        # Left grid
        lh_grid = QGridLayout()
        lh_grid.setSpacing(15)
        lh_grid.addWidget(QLabel(_("Source:")), 1, 0)
        lh_grid.addWidget(self.source_button, 1, 1)
        lh_grid.addWidget(QLabel(_("Destination:")), 2, 0)
        lh_grid.addWidget(self.dest_button, 2, 1)
        lh_grid.addWidget(QLabel(_("Deskew:")), 3, 0)
        lh_grid.addWidget(self.deskew_check, 3, 1)
        lh_grid.addWidget(QLabel(_("Split scans:")), 4, 0)
        lh_grid.addWidget(self.do_split, 4, 1)
        # lh_grid.addWidget(self.split_slider_label,4,1)
        lh_grid.addWidget(QLabel(_("Split at:")), 5, 0)
        lh_grid.addWidget(self.split_slider, 5, 1)
        lh_grid.addWidget(self.show_vals, 6, 0)
        lh_grid.addWidget(self.clean_button, 6, 1)
        lh_grid.addWidget(self.run_button, 7, 0)
        lh_grid.addWidget(self.stop_button, 7, 1)
        # Right Box
        rh_box = QHBoxLayout()
        rh_box.addWidget(self.gui_logger)
        # set layouts and Geometry
        ch_box.addLayout(lh_grid, 1)
        ch_box.addLayout(rh_box, 2)
        v_box.addLayout(ch_box, 3)
        window.setLayout(v_box)
        # x: screen x pos, y: screen y pos, width, height
        self.setGeometry(600, 600, 700, 300)
        self.setFixedSize(600, 300)
        self.load_settings()
        self.load_theme(self.settings["app_theme"])
        self.show()

    # directory: "source" or "dest"
    def open_dir_dlg(self, directory):
        if directory == "source":
            dir = QFileDialog.getExistingDirectory(self,
                                                   "Source", ".",
                                                   QFileDialog.ShowDirsOnly)
            self.files_location = dir
            self.user_values["source"] = self.files_location
        elif directory == "dest":
            dir = QFileDialog.getExistingDirectory(self,
                                                   "Destination", ".",
                                                   QFileDialog.ShowDirsOnly)
            self.files_destination = dir
            self.user_values["dest"] = self.files_destination
        else:
            self.logger.error("%s %s" % (_("Invalid directory parameter"),
                                         directory))

    # Main function that loads the theme provided in settings
    def load_theme(self, theme="default"):
        has_themes = self.load_custom_themes()
        if theme == "default":
            self.logger.debug(_("Theme is default"))
        elif theme == "STPDF-dark" or theme == "STPDF-cmder":
            if has_themes:
                dmsg = "%s: %s" % (_("Changing theme to"), theme)
                self.logger.debug(dmsg)
                theme = os.path.abspath("themes/%s.ini" % theme)
                self.theme_config = configparser.ConfigParser()
                self.theme_config.read(theme)
                self.set_theme()
            else:
                self.logger.error(_("Missing themes folder"))
        else:
            theme_keys = list(self.user_themes.keys())
            if len(self.user_themes) >= 4 and theme in theme_keys:
                theme = self.user_themes[theme]
                self.theme_config = configparser.ConfigParser()
                self.theme_config.read(theme)
                self.set_theme()
            else:
                self.logger.warning("%s: %s" % (_("Invalid theme"), theme))

    # Iterates trough the themes folder and maps all themes
    def load_custom_themes(self):
        if os.path.isdir("themes"):
            for root, dirs, files in os.walk("themes"):
                for file in files:
                    if file.endswith(".ini"):
                        source_path = os.path.join(root, file)
                        theme = file.replace(".ini", "")
                        if theme == "default":
                            self.logger.error(
                                _("Found a default theme in themes folder, but the default theme is already defined"))
                        else:
                            self.user_themes[theme] = source_path
            return True
        else:
            return False

    # Switches colors based on the values provided by the theme
    def set_theme(self):
        self.logger.debug(_("Trying to set theme"))
        allowed = ["lighter", "darker"]
        if False not in self.verify_theme():
            self.logger.debug(_("Successfully verified theme"))
            tv = self.theme_values
            tve = self.theme_values_extras
            qplt = QtGui.QPalette()
            color = QtGui.QColor(*tv["window"])
            if tve["window"] in allowed:
                color = getattr(color, tve["window"])()
            qplt.setColor(QtGui.QPalette.Window,
                          color)
            color = QtGui.QColor(*tv["window_text"])
            if tve["window_text"] in allowed:
                color = getattr(color, tve["window_text"])()
            qplt.setColor(QtGui.QPalette.WindowText,
                          color)
            color = QtGui.QColor(*tv["base"])
            if tve["base"] in allowed:
                color = getattr(color, tve["base"])()
            qplt.setColor(QtGui.QPalette.Base,
                          color)
            color = QtGui.QColor(*tv["background"])
            if tve["background"] in allowed:
                color = getattr(color, tve["background"])()
            qplt.setColor(QtGui.QPalette.Background,
                          color)
            color = QtGui.QColor(*tv["foreground"])
            if tve["foreground"] in allowed:
                color = getattr(color, tve["foreground"])()
            qplt.setColor(QtGui.QPalette.Foreground,
                          color)
            color = QtGui.QColor(*tv["alternate_base"])
            if tve["alternate_base"] in allowed:
                color = getattr(color, tve["alternate_base"])()
            qplt.setColor(QtGui.QPalette.AlternateBase,
                          color)
            color = QtGui.QColor(*tv["tooltip_base"])
            if tve["tooltip_base"] in allowed:
                color = getattr(color, tve["tooltip_base"])()
            qplt.setColor(QtGui.QPalette.ToolTipBase,
                          color)
            color = QtGui.QColor(*tv["tooltip_text"])
            if tve["tooltip_text"] in allowed:
                color = getattr(color, tve["tooltip_text"])()
            qplt.setColor(QtGui.QPalette.ToolTipText,
                          color)
            color = QtGui.QColor(*tv["text"])
            if tve["text"] in allowed:
                color = getattr(color, tve["text"])()
            qplt.setColor(QtGui.QPalette.Text,
                          color)
            color = QtGui.QColor(*tv["button"])
            if tve["button"] in allowed:
                color = getattr(color, tve["button"])()
            qplt.setColor(QtGui.QPalette.Button,
                          color)
            color = QtGui.QColor(*tv["button_text"])
            if tve["button_text"] in allowed:
                color = getattr(color, tve["button_text"])()
            qplt.setColor(QtGui.QPalette.ButtonText,
                          color)
            color = QtGui.QColor(*tv["bright_text"])
            if tve["bright_text"] in allowed:
                color = getattr(color, tve["bright_text"])()
            qplt.setColor(QtGui.QPalette.BrightText,
                          color)
            color = QtGui.QColor(*tv["highlight"])
            if tve["highlight"] in allowed:
                color = getattr(color, tve["highlight"])()
            qplt.setColor(QtGui.QPalette.Highlight,
                          color)
            color = QtGui.QColor(*tv["highlighted_text"])
            if tve["highlighted_text"] in allowed:
                color = getattr(color, tve["highlighted_text"])()
            qplt.setColor(QtGui.QPalette.HighlightedText,
                          color)
            self.app_pallete = qplt
            self.parent.setPalette(qplt)
            self.logger.debug(_("Successfully set theme"))
        else:
            self.logger.error(_("Failed to verify theme"))

    # Verifies the theme values - called by set_theme
    def verify_theme(self):
        self.theme_values = {}
        self.theme_values_extras = {}
        known_values = [
            "window",
            "window_text",
            "base",
            "background",
            "foreground",
            "alternate_base",
            "tooltip_base",
            "tooltip_text",
            "text",
            "button",
            "button_text",
            "bright_text",
            "highlight",
            "highlighted_text"]
        tc = self.theme_config["THEME"]
        ce = self.theme_config["COLOR_EXTRAS"]
        try:
            for value in tc:
                rgb = tc[value].split(",")
                try:
                    rgb = [int(i) for i in rgb]
                except ValueError:
                    self.logger.error(_("Invalid RGB values in app theme"))
                    yield False
                if len(rgb) != 3:
                    m = _("Invalid theme RGB value")
                    self.logger.error("%s: %s = %s" % (m, value, tc[value]))
                    yield False
                if value in known_values:
                    self.theme_values[value] = rgb
                    extra = ce[value]
                    self.theme_values_extras[value] = extra
        except Exception as e:
            en = e.__class__.__name__
            if en == "KeyError":
                msg = _("Your selected theme probably has invalid or missing values")
                self.logger.error(msg)
            else:
                self.logger.critical(e)
                yield False
                pass
        yield True

    # For opening new windows on menu actions
    def on_menu_action(self, action):
        if action == "settings":
            if self.settings_window is None:
                try:
                    self.settings_window = SettingsWindow(self)
                except Exception as e:
                    raise e
            else:
                msg = _("Settings are already open")
                self.logger.error(msg)
                self.gui_logger.append(msg)
        elif action == "about":
            if self.about_window is None:
                try:
                    self.about_window = AboutWindow(self)
                except Exception as e:
                    raise
        else:
            self.logger.error(_("Invalid action"), action)

    # Sets up the console logger
    def set_up_logger(self):
        # TODO: Log level is not being used by logger
        l_levels = self.log_levels
        l_level = self.settings["log_level"]
        n_level = None
        if l_level not in l_levels:
            sys.stdout.write("%s: %s\n" % (_("Invalid log level"), l_level))
            l_level = "info"
            n_level = getattr(logging, l_level.upper(), 10)
        else:
            n_level = getattr(logging, l_level.upper(), 10)
        # Console logger
        log_format = "%(name)s - %(levelname)s: %(message)s"
        logging.basicConfig(format=log_format, level=n_level)
        self.logger = logging.getLogger("STPDF")
        msg = "%s: %s" % (_("Console logger is set with log level"), l_level)
        self.logger.info(msg)

    # Loads user settings from settings.pckl
    def load_settings(self):
        if not os.path.isfile("settings.pckl"):
            self.settings = {
                "keep_vals": False,
                "log_level": "info",
                "app_theme": "default",
                "lang": "en"
            }
            self.set_up_logger()
            pickle.dump(self.settings, open("settings.pckl", "wb"))
            self.load_values()
        else:
            self.settings = pickle.load(open("settings.pckl", "rb"))
            self.set_up_logger()
            try:
                lang = self.settings["lang"]
                if lang in self.available_langs and lang != "en":
                    modl = "%s_gui" % lang
                    # for some reason this seems necessary
                    # when running the app as an executable
                    # after building, ofc this returns the system lang,
                    # so when trying to set another language than your
                    # system's or the default it fails to find the module
                    current_locale, _ = locale.getdefaultlocale()
                    cl = current_locale.split("_")
                    if lang != cl[0]:
                        # however this stupid hack seems to work
                        current_locale = "%s_%s" % (lang, lang.upper())
                    lang = gettext.translation(modl,
                                               "locale/", [current_locale])
                    self.app_lang = lang
                    lang.install()
                keep = self.settings["keep_vals"]
                # `if keep or not keep:` sounds a good idea,
                # but the values must be boolean and not "something" or  1
                if keep is True or keep is False:
                    self.load_values()
                # self.logger.debug(_("Settings loaded successfully"))
            except KeyError:
                self.logger.warning(_("Invalid settings found, removing file"))
                os.remove("settings.pckl")
                if self.retries >= 5:
                    self.logger.error("Failed to load settings after %s retries" % (self.retries))
                    self.retries = 0
                else:
                    self.load_settings()

    # Loads user values from values.pckl
    def load_values(self):
        try:
            if self.settings["keep_vals"] or not os.path.isfile("values.pckl"):
                self.logger.debug(_("Loading user values"))
                # TODO: Check keep values menu action
                if not os.path.isfile("values.pckl"):
                    m = _("Values file does not exist, creating one now")
                    self.logger.debug(m)
                    self.user_values = {
                        "source": "",
                        "dest": "",
                        "deskew": False,
                        "split": False,
                        "split_at": 0
                    }
                    pickle.dump(self.user_values, open("values.pckl", "wb"))
                else:
                    self.user_values = pickle.load(open("values.pckl", "rb"))
                    if self.user_values:
                        msg = "%s: %s" % (_("Loaded user values"), self.user_values)
                        self.logger.debug(msg)
                        self.files_location = self.user_values["source"]
                        self.files_destination = self.user_values["dest"]
                        self.deskew_check.setChecked(self.user_values["deskew"])
                        self.do_split.setChecked(self.user_values["split"])
                        self.split_slider.setValue(self.user_values["split_at"])
                    else:
                        self.logger.error("Failed to load user values: %s" % self.user_values)
                        raise KeyError
        except KeyError:
            self.logger.warning(_("Invalid values found, removing file"))
            os.remove("values.pckl")
            if self.retries >= 5:
                self.logger.error("Failed to load values after %s retries" % (self.retries))
                self.retries = 0
            else:
                self.load_values()

    # clears gui TextEdit that serves as visual logeer
    def clean_gui_logger(self):
        self.gui_logger.setText("")

    # Shows all settings and values in gui_logger
    def show_values(self):
        s = "  %s: %s\n" % (_("Files location"), (self.files_location or ""))
        d = "  %s: %s\n" % (_("Files destination"), (self.files_destination or ""))
        di = "  %s: %s\n" % (_("Deskew"), (self.deskew_check.isChecked()))
        ds = "  %s: %s\n" % (_("Split"), (self.do_split.isChecked()))
        sa = "  %s: %s\n" % (_("Split at"), (self.split_slider.value()))
        values = "%s:\n%s%s%s%s%s" % (_("Values are"), s, d, di, ds, sa)
        self.gui_logger.append(values)
        self.logger.debug(values)
        # kv = "  Keep values: %s\n" % self.menu_keep.isChecked()
        kv = "  %s: %s\n" % (_("Keep values"), self.settings["keep_vals"])
        t = "  %s: %s\n" % (_("App theme"), self.settings["app_theme"])
        l = "  %s: %s\n" % (_("App language"), self.settings["lang"])
        ll = "  %s: %s\n" % (_("Console log Level"), self.settings["log_level"])
        settings = "%s:\n%s%s%s%s" % (_("Settings are"), kv, t, l, ll)
        self.gui_logger.append(settings)
        self.logger.debug(settings)

    # Checks if it has required input to run
    def verify_required(self):
        fl = self.files_location
        fd = self.files_destination
        ds = self.do_split.isChecked()
        sa = self.split_slider.value()
        if not fl or not fd:
            fl = fl or "None"
            fd = fd or "None"
            return _("Location or destination undefined") + \
                "\n\t%s %s\n\t%s %s" % (_("Source:"),
                                        fl,
                                        _("Destination:"),
                                        fd)
        elif not os.path.isdir(self.files_location):
            return _("Missing files location")
        elif len(os.listdir(self.files_location)) <= 1:
            return _("Location is empty, no files to copy")
        elif ds and sa < 3:
            return _("Minimum split is 3")
        else:
            return True

    # Save settings and values if keep_vals is checked
    def do_save(self):
        msg = _("Saving")
        self.logger.info(msg)
        self.gui_logger.append(msg)
        vs = self.user_values
        for val in vs:
            if val == "source" and vs[val] != self.files_location:
                vs[val] = self.files_location
            elif val == "dest" and vs[val] != self.files_destination:
                vs[val] = self.files_destination
            elif val == "deskew" and vs[val] != self.deskew_check.isChecked():
                vs[val] = self.deskew_check.isChecked()
            elif val == "split" and vs[val] != self.do_split.isChecked():
                vs[val] = self.do_split.isChecked()
            elif val == "split_at" and vs[val] != self.split_slider.value():
                vs[val] = self.split_slider.value()
        if self.settings["keep_vals"]:
            self.logger.debug("User values: %s" % vs)
            pickle.dump(vs, open("values.pckl", "wb"))
        self.logger.debug("Settings: %s" % self.settings)
        pickle.dump(self.settings, open("settings.pckl", "wb"))

    # Checks for tesseract in the system
    def check_tesseract(self):
        img = Image.new('RGB', (60, 30), color='red')
        try:
            image_to_string(img)
            return True
        except TesseractNotFoundError:
            return False

    # A function that runs converter in a new thread
    # and appends the yielded string to the loggers
    def threaded_run(self):
        fl = self.files_location
        fd = self.files_destination
        di = self.deskew_check.isChecked()
        ds = self.do_split.isChecked()
        sa = self.split_slider.value()
        cvt = Converter(fl, fd, split=(ds, sa),
                        deskew=di, lang=self.app_lang)
        try:
            for line in cvt.verify_copy_size():
                if self.stop_thread:
                    break
                self.gui_logger.append(str(line))
                self.logger.info(str(line))
            for line in cvt.make_pdf():
                if self.stop_thread:
                    break
                self.gui_logger.append(line)
                self.logger.info(line)
        except Exception as e:
            en = e.__class__.__name__
            if en == "TesseractNotFoundError":
                msg = _("Failed to find tesseract on your system, verify it is installed and on PATH environment variable")
                self.logger.error(msg)
                self.gui_logger.append(msg)
            else:
                print("Thread exception", e)
        self.is_running = False
        self.stop_thread = False

    # Tries to kill the thread if it is alive
    def do_stop(self):
        if self.is_running:
            if self.converter_thread is not None:
                self.logger.debug(_("Found alive thread trying to join it"))
                self.stop_thread = True
                res = self.converter_thread.join(5)
                if self.converter_thread._is_stopped:
                    terminate_thread(self.converter_thread)
                    self.is_running = False
                    self.stop_thread = False
                else:
                    self.logger.debug(_("Thread hasn't stopped retrying"))
                    self.do_stop()
            else:
                self.is_running = False
        else:
            msg = _("Program is not running")
            self.gui_logger.append(msg)
            self.logger.info(msg)

    # Runs stpdf-core by calling it in a new thread
    def do_run(self):
        if not self.is_running:
            if self.converter_thread is not None:
                self.do_stop()
            has_req = self.verify_required()
            if has_req is True:
                self.is_running = True
                self.converter_thread = Thread(target=self.threaded_run, args=())
                self.logger.debug("Thread is: {}".format(self.converter_thread))
                self.converter_thread.start()
            else:
                self.logger.error(has_req)
                self.gui_logger.append(has_req)
        else:
            msg = _("Program is already running")
            self.logger.error(msg)
            self.gui_logger.append(msg)


if __name__ == '__main__':
    # Defaults to the original text
    gettext.install("stpdf_gui")
    app = QApplication([])
    # If fusion style is not set less color values can be edited,
    # however if this is done to the app inside MainWindow, it breaks TipSlider
    app.setStyle("Fusion")
    MainWindow(app).init_ui()
    sys.exit(app.exec_())
