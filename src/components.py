from PyQt5.QtCore import QPoint
from PyQt5.QtWidgets import QSlider,QApplication,QStyleOptionSlider,QToolTip
from PyQt5 import QtGui

# https://stackoverflow.com/a/31658984
class TipSlider(QSlider):
    def __init__(self, *args, tip_offset=QPoint(0, -45)):
        super(QSlider, self).__init__(*args)
        self.tip_offset = tip_offset

        self.style = QApplication.style()
        self.opt = QStyleOptionSlider()

        self.valueChanged.connect(self.show_tip)
        # self.enterEvent = self.show_tip
        # self.mouseReleaseEvent = self.show_tip

    def show_tip(self, _):
        self.initStyleOption(self.opt)
        rectHandle = self.style.subControlRect(self.style.CC_Slider, self.opt, self.style.SC_SliderHandle)

        pos_local = rectHandle.topLeft() + self.tip_offset
        pos_global = self.mapToGlobal(pos_local)
        QToolTip.showText(pos_global, str(self.value()), self)
