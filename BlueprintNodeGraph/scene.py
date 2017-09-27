from PySide import QtGui, QtCore

from .constants import VIEWER_BG_COLOR, VIEWER_GRID_OVERLAY


class NodeScene(QtGui.QGraphicsScene):

    def __init__(self, parent=None):
        super(NodeScene, self).__init__(parent)
        self.background_color = VIEWER_BG_COLOR
        self.grid = VIEWER_GRID_OVERLAY

    def __str__(self):
        return '{}(parent=\'{}\')'.format(
            self.__class__.__name__, self.viewer()
        )

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
        painter.setRenderHint(QtGui.QPainter.Antialiasing, False)
        painter.setBrush(self._bg_color)
        painter.drawRect(rect.normalized())
        if not self._grid:
            return
        pen = QtGui.QPen(QtGui.QColor(255, 255, 255, 15), 0.5)
        self._draw_grid(painter, rect, pen, 30)
        pen = QtGui.QPen(QtGui.QColor(0, 0, 0, 100), 1.0)
        self._draw_grid(painter, rect, pen, 150)

    def mousePressEvent(self, event):
        selected_nodes = self.viewer().selected_nodes()
        if self.viewer():
            self.viewer().sceneMousePressEvent(event)
        super(NodeScene, self).mousePressEvent(event)
        keep_selection = any([
            event.button() == QtCore.Qt.MiddleButton,
            event.button() == QtCore.Qt.RightButton
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
    def background_color(self):
        return self._bg_color.toTuple()

    @background_color.setter
    def background_color(self, color):
        self._bg_color = QtGui.QColor(
            color[0], color[1], color[2], color[3]
        )
