#!/usr/bin/python
from .. import QtCore, QtGui, QtWidgets
from ..constants import Z_VAL_NODE_WIDGET, PIPE_SLICER_COLOR


class SlicerPipe(QtWidgets.QGraphicsPathItem):
    """
    Base item used for drawing the pipe connection slicer.
    """

    def __init__(self):
        super(SlicerPipe, self).__init__()
        self.setZValue(Z_VAL_NODE_WIDGET + 2)

    def paint(self, painter, option, widget):
        """
        Draws the slicer pipe.

        Args:
            painter (QtGui.QPainter): painter used for drawing the item.
            option (QtGui.QStyleOptionGraphicsItem):
                used to describe the parameters needed to draw.
            widget (QtWidgets.QWidget): not used.
        """
        color = QtGui.QColor(*PIPE_SLICER_COLOR)
        p1 = self.path().pointAtPercent(0)
        p2 = self.path().pointAtPercent(1)
        size = 6.0
        offset = size / 2

        painter.save()
        painter.setRenderHint(painter.Antialiasing, True)

        font = painter.font()
        font.setPointSize(12)
        painter.setFont(font)
        text = 'slice'
        text_x = painter.fontMetrics().width(text) / 2
        text_y = painter.fontMetrics().height() / 1.5
        text_pos = QtCore.QPointF(p1.x() - text_x, p1.y() - text_y)
        text_color = QtGui.QColor(*PIPE_SLICER_COLOR)
        text_color.setAlpha(80)
        painter.setPen(QtGui.QPen(text_color, 1.5, QtCore.Qt.SolidLine))
        painter.drawText(text_pos, text)

        painter.setPen(QtGui.QPen(color, 1.5, QtCore.Qt.DashLine))
        painter.drawPath(self.path())

        painter.setPen(QtGui.QPen(color, 1.5, QtCore.Qt.SolidLine))
        painter.setBrush(color)

        rect = QtCore.QRectF(p1.x() - offset, p1.y() - offset, size, size)
        painter.drawEllipse(rect)

        rect = QtCore.QRectF(p2.x() - offset, p2.y() - offset, size, size)
        painter.drawEllipse(rect)
        painter.restore()

    def draw_path(self, p1, p2):
        path = QtGui.QPainterPath()
        path.moveTo(p1)
        path.lineTo(p2)
        self.setPath(path)
