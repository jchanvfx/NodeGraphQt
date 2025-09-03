#!/usr/bin/python
from Qt import QtCore, QtGui, QtWidgets

from NodeGraphQt.constants import Z_VAL_NODE_WIDGET


class XDisabledItem(QtWidgets.QGraphicsItem):
    """
    Node disabled overlay item.

    Args:
        parent (NodeItem): the parent node item.
        text (str): disable overlay text.
    """

    def __init__(self, parent=None, text=None):
        super(XDisabledItem, self).__init__(parent)
        self.setZValue(Z_VAL_NODE_WIDGET + 2)
        self.setVisible(False)
        self.proxy_mode = False
        self.color = (0, 0, 0, 255)
        self.text = text

    def boundingRect(self):
        rect = self.parentItem().boundingRect()

        # marging (base margin = 20, point size = 4, pen width bleed = 4)
        margin = 28

        return QtCore.QRectF(
            rect.left() - margin / 2,
            rect.top() - margin / 2,
            rect.width() + margin,
            rect.height() + margin,
        )

    def paint(self, painter, option, widget):
        """
        Draws the overlay disabled X item on top of a node item.

        Args:
            painter (QtGui.QPainter): painter used for drawing the item.
            option (QtGui.QStyleOptionGraphicsItem):
                used to describe the parameters needed to draw.
            widget (QtWidgets.QWidget): not used.
        """
        painter.save()

        margin = 20
        rect = self.parentItem().boundingRect()
        dis_rect = QtCore.QRectF(
            rect.left() - (margin / 2),
            rect.top() - (margin / 2),
            rect.width() + margin,
            rect.height() + margin,
        )

        if not self.proxy_mode:
            pen = QtGui.QPen(QtGui.QColor(*self.color), 8)
            pen.setCapStyle(QtCore.Qt.RoundCap)
            painter.setPen(pen)
            painter.drawLine(dis_rect.topLeft(), dis_rect.bottomRight())
            painter.drawLine(dis_rect.topRight(), dis_rect.bottomLeft())

        bg_color = QtGui.QColor(*self.color)
        bg_color.setAlpha(100)
        bg_margin = -0.5
        bg_rect = QtCore.QRectF(
            dis_rect.left() - (bg_margin / 2),
            dis_rect.top() - (bg_margin / 2),
            dis_rect.width() + bg_margin,
            dis_rect.height() + bg_margin,
        )
        painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0, 0)))
        painter.setBrush(bg_color)
        painter.drawRoundedRect(bg_rect, 5, 5)

        if not self.proxy_mode:
            point_size = 4.0
            pen = QtGui.QPen(QtGui.QColor(155, 0, 0, 255), 0.7)
        else:
            point_size = 8.0
            pen = QtGui.QPen(QtGui.QColor(155, 0, 0, 255), 4.0)

        painter.setPen(pen)
        painter.drawLine(dis_rect.topLeft(), dis_rect.bottomRight())
        painter.drawLine(dis_rect.topRight(), dis_rect.bottomLeft())

        point_pos = (
            dis_rect.topLeft(),
            dis_rect.topRight(),
            dis_rect.bottomLeft(),
            dis_rect.bottomRight(),
        )
        painter.setBrush(QtGui.QColor(255, 0, 0, 255))
        for p in point_pos:
            p.setX(p.x() - (point_size / 2))
            p.setY(p.y() - (point_size / 2))
            point_rect = QtCore.QRectF(p, QtCore.QSizeF(point_size, point_size))
            painter.drawEllipse(point_rect)

        if self.text and not self.proxy_mode:
            font = painter.font()
            font.setPointSize(10)

            painter.setFont(font)
            font_metrics = QtGui.QFontMetrics(font)
            font_width = font_metrics.horizontalAdvance(self.text)
            font_height = font_metrics.height()
            txt_w = font_width * 1.25
            txt_h = font_height * 2.25
            text_bg_rect = QtCore.QRectF(
                (rect.width() / 2) - (txt_w / 2),
                (rect.height() / 2) - (txt_h / 2),
                txt_w,
                txt_h,
            )
            painter.setPen(QtGui.QPen(QtGui.QColor(255, 0, 0), 0.5))
            painter.setBrush(QtGui.QColor(*self.color))
            painter.drawRoundedRect(text_bg_rect, 2, 2)

            text_rect = QtCore.QRectF(
                (rect.width() / 2) - (font_width / 2),
                (rect.height() / 2) - (font_height / 2),
                txt_w * 2,
                font_height * 2,
            )

            painter.setPen(QtGui.QPen(QtGui.QColor(255, 0, 0), 1))
            painter.drawText(text_rect, self.text)

        painter.restore()
