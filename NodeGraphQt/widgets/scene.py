#!/usr/bin/python
from .. import QtGui, QtCore, QtWidgets

from ..constants import (VIEWER_BG_COLOR,
                                                    VIEWER_GRID_SIZE,
                                                    VIEWER_GRID_OVERLAY,
                                                    VIEWER_GRID_COLOR)


class NodeScene(QtWidgets.QGraphicsScene):

    def __init__(self, parent=None):
        super(NodeScene, self).__init__(parent)
        self.background_color = VIEWER_BG_COLOR
        self.grid = VIEWER_GRID_OVERLAY
        self.grid_color = VIEWER_GRID_COLOR

        self.setBackgroundBrush(self._bg_qcolor)

    def __repr__(self):
        return '{}.{}(\'{}\')'.format(self.__module__,
                                      self.__class__.__name__,
                                      self.viewer())

    def _draw_grid(self, painter, rect, pen, grid_size):
        left = int(rect.left())
        right = int(rect.right())
        top = int(rect.top())
        bottom = int(rect.bottom())

        first_left = left - (left % grid_size)
        first_top = top - (top % grid_size)

        lines = []
        lines.extend([QtCore.QLine(x, top, x, bottom) for x in range(first_left, right, grid_size)])
        lines.extend([QtCore.QLine(left, y, right, y) for y in range(first_top, bottom, grid_size)])

        painter.setPen(pen)
        painter.drawLines(lines)

    def drawBackground(self, painter, rect):
        super(NodeScene, self).drawBackground(painter, rect)

        painter.save()

        painter.setRenderHint(QtGui.QPainter.Antialiasing, False)
        painter.setBrush(self.backgroundBrush())

        if not self._grid:
            painter.restore()
            return

        zoom = self.viewer().get_zoom()

        if zoom > -0.5:
            pen = QtGui.QPen(QtGui.QColor(*self.grid_color), 0.65)
            self._draw_grid(painter, rect, pen, VIEWER_GRID_SIZE)

        color = self._bg_qcolor.darker(150)
        if zoom < -0.0:
            color = color.darker(100 - int(zoom * 110))
        pen = QtGui.QPen(color, 0.65)
        self._draw_grid(painter, rect, pen, VIEWER_GRID_SIZE * 8)

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
    def grid(self):
        return self._grid

    @grid.setter
    def grid(self, mode=True):
        self._grid = mode

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
        self._bg_qcolor = QtGui.QColor(*self._bg_color)
