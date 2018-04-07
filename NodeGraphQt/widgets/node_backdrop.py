#!/usr/bin/python
from PySide import QtGui, QtCore

from .constants import Z_VAL_PIPE, NODE_SEL_COLOR, NODE_SEL_BORDER_COLOR
from .node_abstract import AbstractNodeItem


class BackdropSizer(QtGui.QGraphicsItem):

    def __init__(self, parent=None, size=6.0, color=(255, 255, 255, 20)):
        super(BackdropSizer, self).__init__(parent)
        self.setFlag(self.ItemIsSelectable, True)
        self.setFlag(self.ItemIsMovable, True)
        self.setFlag(self.ItemSendsScenePositionChanges, True)
        self.setCursor(QtGui.QCursor(QtCore.Qt.SizeFDiagCursor))
        self.setToolTip('Resize Backdrop')
        self._size = size
        self._color = color
        self._hovered = False

    @property
    def size(self):
        return self._size

    def set_pos(self, x, y):
        x -= self._size
        y -= self._size
        self.setPos(x, y)

    def boundingRect(self):
        return QtCore.QRectF(0.0, 0.0, self._size, self._size)

    def itemChange(self, change, value):
        if change == self.ItemPositionChange:
            item = self.parentItem()
            mx, my = item.min_size
            x = mx if value.x() < mx else value.x()
            y = my if value.y() < my else value.y()
            value = QtCore.QPointF(x, y)
            item.on_sizer_pos_changed(value)
            return value
        return super(BackdropSizer, self).itemChange(change, value)

    def mouseDoubleClickEvent(self, event):
        item = self.parentItem()
        item.on_sizer_double_clicked()
        super(BackdropSizer, self).mouseDoubleClickEvent(event)

    def paint(self, painter, option, widget):
        painter.save()

        rect = self.boundingRect()
        color = QtGui.QColor(*self._color)
        painter.setBrush(color)
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawRect(rect)

        painter.restore()


class BackdropNodeItem(AbstractNodeItem):
    """
    Base Backdrop item.
    """

    def __init__(self, name='backdrop', text='', parent=None):
        super(BackdropNodeItem, self).__init__(name, parent)
        self.setZValue(Z_VAL_PIPE - 1)
        self.add_property('backdrop_text', text)
        self._min_size = 150, 150
        self.width = 50
        self.height = 50
        self.color = (5, 129, 138, 255)

        self._sizer = BackdropSizer(self, 10.0)
        self._sizer.set_pos(self.width, self.height)

    # def mousePressEvent(self, event):
    #     if event.modifiers() == QtCore.Qt.AltModifier:
    #         event.ignore()
    #         return
    #     if event.button() == QtCore.Qt.MouseButton.LeftButton:
    #         # rect = self.boundingRect()
    #         print self.viewer()
    #     super(BackdropNodeItem, self).mousePressEvent(event)
    #
    # def mouseReleaseEvent(self, event):
    #     if event.modifiers() == QtCore.Qt.AltModifier:
    #         event.ignore()
    #         return
    #     super(BackdropNodeItem, self).mouseReleaseEvent(event)

    def on_sizer_pos_changed(self, pos):
        self.width = pos.x() + self._sizer.size
        self.height = pos.y() + self._sizer.size

    def on_sizer_double_clicked(self):
        width, height = self._min_size
        self._sizer.set_pos(width, height)

    def paint(self, painter, option, widget):
        painter.save()

        rect = self.boundingRect()
        color = (self.color[0], self.color[1], self.color[2], 50)
        painter.setBrush(QtGui.QColor(*color))
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawRect(rect)

        top_rect = QtCore.QRectF(0.0, 0.0, rect.width(), 20.0)
        painter.setBrush(QtGui.QColor(*self.color))
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawRect(top_rect)

        if self.selected and NODE_SEL_COLOR:
            sel_color = [x for x in NODE_SEL_COLOR]
            sel_color[-1] = 10
            painter.setBrush(QtGui.QColor(*sel_color))
            painter.setPen(QtCore.Qt.NoPen)
            painter.drawRect(rect)

        path = QtGui.QPainterPath()
        path.addRect(rect)
        border_color = self.color
        if self.selected and NODE_SEL_BORDER_COLOR:
            border_color = NODE_SEL_BORDER_COLOR
        painter.setBrush(QtCore.Qt.NoBrush)
        painter.setPen(QtGui.QPen(QtGui.QColor(*border_color), 1))
        painter.drawPath(path)

        painter.setPen(QtGui.QColor(255, 255, 255, 255))
        painter.drawText(top_rect, QtCore.Qt.AlignCenter, self.name)

        painter.restore()

    @property
    def min_size(self):
        return self._min_size

    @property
    def text(self):
        return self._properties['backdrop_text']

    @text.setter
    def text(self, text):
        self._properties['backdrop_text'] = text

    @AbstractNodeItem.width.setter
    def width(self, width=0.0):
        AbstractNodeItem.width.fset(self, width)

    @AbstractNodeItem.height.setter
    def height(self, height=0.0):
        AbstractNodeItem.height.fset(self, height)
