#!/usr/bin/python
from Qt import QtGui, QtCore, QtWidgets

from ..constants import (VIEWER_BG_COLOR,
                         VIEWER_GRID_SIZE,
                         VIEWER_GRID_COLOR,
                         VIEWER_GRID_NONE,
                         VIEWER_GRID_DOTS,
                         VIEWER_GRID_LINES)


class NodeScene(QtWidgets.QGraphicsScene):

    def __init__(self, parent=None):
        super(NodeScene, self).__init__(parent)
        self.background_color = VIEWER_BG_COLOR
        self.grid_color = VIEWER_GRID_COLOR
        self._grid_mode = VIEWER_GRID_LINES
        self.editable = True

    def __repr__(self):
        cls_name = str(self.__class__.__name__)
        return '<{}("{}") object at {}>'.format(
            cls_name, self.viewer(), hex(id(self)))

    def _draw_text(self, painter, pen):
        font = QtGui.QFont()
        font.setPixelSize(48)
        painter.setFont(font)
        parent = self.viewer()
        pos = QtCore.QPoint(20, parent.height()-20)
        painter.setPen(pen)
        painter.drawText(parent.mapToScene(pos), 'Not Editable')

    def _draw_grid(self, painter, rect, pen, grid_size):
        """
        draws the grid lines in the scene.

        Args:
            painter (QtGui.QPainter): painter object.
            rect (QtCore.QRectF): rect object.
            pen (QtGui.QPen): pen object.
            grid_size (int): grid size.
        """
        left = int(rect.left())
        right = int(rect.right())
        top = int(rect.top())
        bottom = int(rect.bottom())

        first_left = left - (left % grid_size)
        first_top = top - (top % grid_size)

        lines = []
        lines.extend([
            QtCore.QLineF(x, top, x, bottom)
            for x in range(first_left, right, grid_size)
        ])
        lines.extend([
            QtCore.QLineF(left, y, right, y)
            for y in range(first_top, bottom, grid_size)]
        )

        painter.setPen(pen)
        painter.drawLines(lines)

    def _draw_dots(self, painter, rect, pen, grid_size):
        """
        draws the grid dots in the scene.

        Args:
            painter (QtGui.QPainter): painter object.
            rect (QtCore.QRectF): rect object.
            pen (QtGui.QPen): pen object.
            grid_size (int): grid size.
        """
        zoom = self.viewer().get_zoom()
        if zoom < 0:
            grid_size = int(abs(zoom) / 0.3 + 1) * grid_size

        left = int(rect.left())
        right = int(rect.right())
        top = int(rect.top())
        bottom = int(rect.bottom())

        first_left = left - (left % grid_size)
        first_top = top - (top % grid_size)

        pen.setWidth(grid_size / 10)
        painter.setPen(pen)

        [painter.drawPoint(int(x), int(y))
         for x in range(first_left, right, grid_size)
         for y in range(first_top, bottom, grid_size)]

    def drawBackground(self, painter, rect):
        super(NodeScene, self).drawBackground(painter, rect)

        painter.save()
        painter.setRenderHint(QtGui.QPainter.Antialiasing, False)
        painter.setBrush(self.backgroundBrush())

        if self._grid_mode is VIEWER_GRID_DOTS:
            pen = QtGui.QPen(QtGui.QColor(*self.grid_color), 0.65)
            self._draw_dots(painter, rect, pen, VIEWER_GRID_SIZE)

        elif self._grid_mode is VIEWER_GRID_LINES:
            zoom = self.viewer().get_zoom()
            if zoom > -0.5:
                pen = QtGui.QPen(QtGui.QColor(*self.grid_color), 0.65)
                self._draw_grid(painter, rect, pen, VIEWER_GRID_SIZE)

            color = QtGui.QColor(*self._bg_color).darker(150)
            if zoom < -0.0:
                color = color.darker(100 - int(zoom * 110))
            pen = QtGui.QPen(color, 0.65)
            self._draw_grid(painter, rect, pen, VIEWER_GRID_SIZE * 8)

        if not self.editable:
            pen = QtGui.QPen(QtGui.QColor(*(90, 90, 90)))
            self._draw_text(painter, pen)

        painter.restore()

    def mousePressEvent(self, event):
        selected_nodes = self.viewer().selected_nodes()
        if self.viewer():
            self.viewer().sceneMousePressEvent(event)
        super(NodeScene, self).mousePressEvent(event)
        keep_selection = any([
            event.button() == QtCore.Qt.MiddleButton,
            event.button() == QtCore.Qt.RightButton,
            event.modifiers() == QtCore.Qt.AltModifier
        ])
        if keep_selection:
            for node in selected_nodes:
                node.setSelected(True)

    def mouseMoveEvent(self, event):
        if self.viewer():
            self.viewer().sceneMouseMoveEvent(event)
        super(NodeScene, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.viewer():
            self.viewer().sceneMouseReleaseEvent(event)
        super(NodeScene, self).mouseReleaseEvent(event)

    def viewer(self):
        return self.views()[0] if self.views() else None

    @property
    def grid_mode(self):
        return self._grid_mode

    @grid_mode.setter
    def grid_mode(self, mode=VIEWER_GRID_LINES):
        self._grid_mode = mode

    @property
    def grid_color(self):
        return self._grid_color

    @grid_color.setter
    def grid_color(self, color=(0, 0, 0)):
        self._grid_color = color

    @property
    def background_color(self):
        return self._bg_color

    @background_color.setter
    def background_color(self, color=(0, 0, 0)):
        self._bg_color = color
        self.setBackgroundBrush(QtGui.QColor(*self._bg_color))
