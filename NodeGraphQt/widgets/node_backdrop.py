#!/usr/bin/python

from PySide import QtGui, QtCore

from .constants import Z_VAL_PIPE
from .node_skeleton import NodeSkeletonItem


class BackdropSizer(QtGui.QGraphicsItem):
    """
    
    """

    def __init__(self, parent=None, size=6.0):
        super(BackdropSizer, self).__init__(parent)
        self.setFlag(self.ItemIsSelectable, False)
        self.setFlag(self.ItemIsMovable, True)
        self.setFlag(self.ItemSendsScenePositionChanges, True)
        self.setCursor(QtGui.QCursor(QtCore.Qt.SizeFDiagCursor))
        self._size = size

    def boundingRect(self):
        return QtCore.QRectF(0.0, 0.0, self._size, self._size)

    def itemChange(self, change, value):
        if change == self.ItemPositionChange:
            x, y = value.x(), value.y()
            for cb in self.posChangeCallbacks:
                res = cb(x, y)
                if res:
                    x, y = res
                    value = QtCore.QPointF(x, y)
            return value
        return super(BackdropSizer, self).itemChange(change, value)

    def paint(self, painter, option, widget):
        return

    def mouseDoubleClickEvent(self, event):
        self.parentItem().adjustSize()
        super(BackdropSizer, self).mouseDoubleClickEvent(event)

    def mouseMoveEvent(self, event):
        super(BackdropSizer, self).mouseMoveEvent(event)
        self.setSelected(False)

    def mousePressEvent(self, event):
        super(BackdropSizer, self).mousePressEvent(event)
        self.setSelected(False)

    def mouseReleaseEvent(self, event):
        super(BackdropSizer, self).mouseReleaseEvent(event)


class BackdropNodeItem(NodeSkeletonItem):
    """

    """

    def __init__(self, name='backdrop', text='', parent=None):
        super(BackdropNodeItem, self).__init__(name, parent)
        self.setZValue(Z_VAL_PIPE - 1)
        self._text = text
        self._sizer = BackdropSizer(self, 6.0)
        self.width = 300
        self.height = 300
