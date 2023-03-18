from PySide6.QtCore import Qt, QRectF, QTimer
from PySide6.QtGui import QPainter, QPainterPath, QPen, QColor, QBrush, QFont
from PySide6.QtWidgets import QVBoxLayout, QSlider, QWidget, QApplication


class CPBar(QWidget):
    def __init__(self, parent, close_p, all_p):
        super().__init__(parent)
        self.setMinimumSize(243, 241)
        if all_p != 0:
            self.p = close_p / all_p
        else: self.p = 0

    def upd(self):
        self.update()

    def paintEvent(self, e):
        if self.height() > self.width():
            self.setFixedWidth(self.height())
        if self.width() > self.height():
            self.setFixedHeight(self.width())
        pd = self.p * 360
        rd = 360 - pd
        p = QPainter(self)
        p.translate(4, 4)
        p.setRenderHint(QPainter.Antialiasing)
        path, path2 = QPainterPath(), QPainterPath()
        circle_width = self.width() - self.width() / 10
        widht_half = circle_width/2
        path.moveTo(widht_half, 0)
        circle_rect = QRectF(self.rect().left() / 2, self.rect().top() / 2, circle_width, self.height() - self.height() / 10)
        path.arcTo(circle_rect, 90, -pd)
        pen, pen2 = QPen(), QPen()
        pen.setCapStyle(Qt.FlatCap)
        pen.setColor(QColor("#AB27EA"))
        pen_width = self.width()/25
        pen.setWidth(pen_width)
        p.strokePath(path, pen)
        path2.moveTo(widht_half, 0)
        pen2.setWidth(pen_width)
        pen2.setColor(QColor("#ffffff"))
        pen2.setCapStyle(Qt.FlatCap)
        pen2.setDashPattern([1, 0])  # remove this line to have continue cercle line
        path2.arcTo(circle_rect, 90, rd)
        pen2.setDashOffset(2.2) # this one too
        p.strokePath(path2, pen2)

        p.setPen(pen)
        font = QFont()
        percent_size = self.height() / 7
        font.setPointSizeF(percent_size)
        p.setFont(font)
        percent_text_position = self.rect().center()
        p_in_percent = self.p * 100
        percent_text_position.setX(percent_text_position.x() - (
                percent_size + (self.width()/6 if p_in_percent >= 100 else self.width()/10 if p_in_percent >= 10 else + self.width()/40)))
        percent_text_position.setY(percent_text_position.y() + percent_size * 2 / 5)
        p.drawText(percent_text_position, f"{round(self.p * 100, 0)}%")
