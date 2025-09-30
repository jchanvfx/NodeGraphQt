#!/usr/bin/python
import math

from Qt import QtCore, QtGui, QtWidgets

from NodeGraphQt.constants import Z_VAL_NODE_WIDGET, PipeSlicerEnum


class SlicerPipeItem(QtWidgets.QGraphicsPathItem):
    """
    Base item used for drawing the pipe connection slicer.
    """

    def __init__(self):
        super(SlicerPipeItem, self).__init__()
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
        color = QtGui.QColor(*PipeSlicerEnum.COLOR.value)
        p1 = self.path().pointAtPercent(0)
        p2 = self.path().pointAtPercent(1)
        size = 6.0
        offset = size / 2
        arrow_size = 4.0

        painter.save()
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)

        font = painter.font()
        font.setPointSize(12)
        painter.setFont(font)
        text = 'slice'
        text_x = painter.fontMetrics().horizontalAdvance(text) / 2
        text_y = painter.fontMetrics().height() / 1.5
        text_pos = QtCore.QPointF(p1.x() - text_x, p1.y() - text_y)
        text_color = QtGui.QColor(*PipeSlicerEnum.COLOR.value)
        text_color.setAlpha(80)
        painter.setPen(QtGui.QPen(
            text_color, PipeSlicerEnum.WIDTH.value, QtCore.Qt.SolidLine
        ))
        painter.drawText(text_pos, text)

        painter.setPen(QtGui.QPen(
            color, PipeSlicerEnum.WIDTH.value, QtCore.Qt.DashDotLine
        ))
        painter.drawPath(self.path())

        pen = QtGui.QPen(
            color, PipeSlicerEnum.WIDTH.value, QtCore.Qt.SolidLine
        )
        pen.setCapStyle(QtCore.Qt.RoundCap)
        pen.setJoinStyle(QtCore.Qt.MiterJoin)
        painter.setPen(pen)
        painter.setBrush(color)

        rect = QtCore.QRectF(p1.x() - offset, p1.y() - offset, size, size)
        painter.drawEllipse(rect)

        arrow = QtGui.QPolygonF()
        arrow.append(QtCore.QPointF(-arrow_size, arrow_size))
        arrow.append(QtCore.QPointF(0.0, -arrow_size * 0.9))
        arrow.append(QtCore.QPointF(arrow_size, arrow_size))

        transform = QtGui.QTransform()
        transform.translate(p2.x(), p2.y())
        radians = math.atan2(p2.y() - p1.y(),
                             p2.x() - p1.x())
        degrees = math.degrees(radians) - 90
        transform.rotate(degrees)

        painter.drawPolygon(transform.map(arrow))
        painter.restore()

    def draw_path(self, p1, p2):
        path = QtGui.QPainterPath()
        path.moveTo(p1)
        path.lineTo(p2)
        self.setPath(path)
