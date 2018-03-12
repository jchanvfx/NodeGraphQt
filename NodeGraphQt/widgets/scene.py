from PySide import QtGui, QtCore

from .constants import VIEWER_BG_COLOR, VIEWER_GRID_OVERLAY, VIEWER_GRID_COLOR


class NodeScene(QtGui.QGraphicsScene):

    def __init__(self, parent=None):
        super(NodeScene, self).__init__(parent)
        self.background_color = VIEWER_BG_COLOR
        self.grid = VIEWER_GRID_OVERLAY
        self.grid_color = VIEWER_GRID_COLOR

    def __repr__(self):
        return '{}.{}(parent=\'{}\')'.format(
            self.__module__, self.__class__.__name__, self.viewer()
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
        painter.save()
        color = QtGui.QColor(*self._bg_color)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, False)
        painter.setBrush(color)
        painter.drawRect(rect.normalized())
        if not self._grid:
            return
        grid_size = 20
        zoom = self.viewer().get_zoom()
        color = QtGui.QColor(*self.grid_color)
        grid_alpha = 8
        if zoom > -4:
            color.setAlpha(grid_alpha)
            pen = QtGui.QPen(color, 0.65)
            self._draw_grid(painter, rect, pen, grid_size)
        if zoom < 0:
            color.setAlpha(grid_alpha * (0.05 * (zoom * -1) + 1.0))
        else:
            color.setAlpha(grid_alpha * 1.1)
        pen = QtGui.QPen(color, 0.5)
        self._draw_grid(painter, rect, pen, grid_size * 8)
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
    def background_color(self, color=(0, 0, 0, 0)):
        self._bg_color = color
