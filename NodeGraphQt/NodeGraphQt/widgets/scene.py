#!/usr/bin/python
from NodeGraphQt import QtGui, QtCore, QtWidgets

from NodeGraphQt.constants import (VIEWER_BG_COLOR,
                                   VIEWER_GRID_SIZE,
                                   VIEWER_GRID_OVERLAY,
                                   VIEWER_GRID_COLOR)


class NodeScene(QtWidgets.QGraphicsScene):

    def __init__(self, parent=None):
        super(NodeScene, self).__init__(parent)
        self.background_color = VIEWER_BG_COLOR
        self.grid = VIEWER_GRID_OVERLAY
        self.grid_color = VIEWER_GRID_COLOR

    def __repr__(self):
        return '{}.{}(\'{}\')'.format(self.__module__,
                                      self.__class__.__name__,
                                      self.viewer())

    def _draw_grid(self, painter, rect, pen, grid_size):
        lines = []
        left = int(rect.left()) - (int(rect.left()) % grid_size)
        top = int(rect.top()) - (int(rect.top()) % grid_size)
        x = left
        while x < rect.right():
            x += grid_size
            lines.append(QtCore.QLineF(x, rect.top(), x, rect.bottom()))
        y = top
        while y < rect.bottom():
            y += grid_size
            lines.append(QtCore.QLineF(rect.left(), y, rect.right(), y))
        painter.setPen(pen)
        painter.drawLines(lines)

    def drawBackground(self, painter, rect):
        painter.save()

        bg_color = QtGui.QColor(*self._bg_color)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, False)
        painter.setBrush(bg_color)
        painter.drawRect(rect)

        if not self._grid:
            painter.restore()
            return

        zoom = self.viewer().get_zoom()

        if zoom > -0.5:
            pen = QtGui.QPen(QtGui.QColor(*self.grid_color), 0.65)
            self._draw_grid(painter, rect, pen, VIEWER_GRID_SIZE)

        color = bg_color.darker(150)
        if zoom < -0.0:
            color = color.darker(100 - int(zoom * 110))
        pen = QtGui.QPen(color, 0.65)
        self._draw_grid(painter, rect, pen, VIEWER_GRID_SIZE * 8)

        # fix border issue on the scene edge.
        pen = QtGui.QPen(bg_color, 2)
        pen.setCosmetic(True)
        path = QtGui.QPainterPath()
        path.addRect(rect)
        painter.setBrush(QtCore.Qt.NoBrush)
        painter.setPen(pen)
        painter.drawPath(path)

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
