from PySide2.QtWidgets import QWidget
from PySide2extn.RoundProgressBar import roundProgressBar

class MyWidget(QWidget):
    def __init__(self, parent, close_p, all_p):
        super().__init__(parent)

        self.rpb = roundProgressBar()
        self.rpb.rpb_setBarStyle('Hybrid2')
        self.rpb.rpb_setRange(0, all_p)
        self.rpb.rpb_setValue(close_p)

