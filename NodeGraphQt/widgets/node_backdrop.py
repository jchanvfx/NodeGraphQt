#!/usr/bin/python
from PySide import QtGui, QtCore

from .constants import Z_VAL_PIPE, NODE_SEL_COLOR, NODE_SEL_BORDER_COLOR
from .node_abstract import AbstractNodeItem


class BackdropSizer(QtGui.QGraphicsItem):

    def __init__(self, parent=None, size=6.0):
        super(BackdropSizer, self).__init__(parent)
        self.setFlag(self.ItemIsSelectable, True)
        self.setFlag(self.ItemIsMovable, True)
        self.setFlag(self.ItemSendsScenePositionChanges, True)
        self.setCursor(QtGui.QCursor(QtCore.Qt.SizeFDiagCursor))
        self.setToolTip('double-click auto resize Backdrop')
        self._size = size
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
            mx, my = item.minimum_size
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
        item = self.parentItem()
        if item and item.selected:
            color = QtGui.QColor(*NODE_SEL_BORDER_COLOR)
        else:
            color = QtGui.QColor(*item.color)
            color.setAlpha(60)
        path = QtGui.QPainterPath()
        path.moveTo(rect.topRight())
        path.lineTo(rect.bottomRight())
        path.lineTo(rect.bottomLeft())
        painter.setBrush(color)
        painter.setPen(QtCore.Qt.NoPen)
        painter.fillPath(path, painter.brush())

        painter.restore()


class BackdropNodeItem(AbstractNodeItem):
    """
    Base Backdrop item.
    """

    def __init__(self, name='backdrop', text='', parent=None):
        super(BackdropNodeItem, self).__init__(name, parent)
        self.setZValue(Z_VAL_PIPE - 1)
        self.add_property('backdrop_text', text)
        self.color = (5, 129, 138, 255)
        self._min_size = 80, 80
        self._sizer = BackdropSizer(self, 20.0)
        self._sizer.set_pos(*self._min_size)

    def _combined_rect(self, nodes):
        group = self.scene().createItemGroup(nodes)
        rect = group.boundingRect()
        self.scene().destroyItemGroup(group)
        return rect

    def mousePressEvent(self, event):
        if event.modifiers() == QtCore.Qt.AltModifier:
            event.ignore()
            return

        super(BackdropNodeItem, self).mousePressEvent(event)
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            [n.setSelected(True) for n in self.get_nodes()]

    def on_sizer_pos_changed(self, pos):
        self._width = pos.x() + self._sizer.size
        self._height = pos.y() + self._sizer.size

    def on_sizer_double_clicked(self):
        self.auto_resize()

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

        painter.setPen(QtGui.QColor(255, 255, 255, 255))
        painter.drawText(top_rect, QtCore.Qt.AlignCenter, self.name)

        path = QtGui.QPainterPath()
        path.addRect(rect)
        border_color = self.color
        if self.selected and NODE_SEL_BORDER_COLOR:
            border_color = NODE_SEL_BORDER_COLOR
        painter.setBrush(QtCore.Qt.NoBrush)
        painter.setPen(QtGui.QPen(QtGui.QColor(*border_color), 1))
        painter.drawPath(path)

        painter.restore()

    def get_nodes(self, inc_intersects=False):
        mode = {True: QtCore.Qt.IntersectsItemShape,
                False: QtCore.Qt.ContainsItemShape}
        nodes = []
        if self.scene():
            polygon = self.mapToScene(self.boundingRect())
            rect = polygon.boundingRect()
            items = self.scene().items(rect, mode=mode[inc_intersects])
            for item in items:
                if item == self or item == self._sizer:
                    continue
                if isinstance(item, AbstractNodeItem):
                    nodes.append(item)
        return nodes

    def auto_resize(self, nodes=None):
        nodes = nodes or self.get_nodes(inc_intersects=True)
        if nodes:
            padding = 40
            nodes_rect = self._combined_rect(nodes)
            self.pos = (nodes_rect.x() - padding,
                        nodes_rect.y() - padding)
            self._sizer.set_pos(nodes_rect.width() + (padding * 2),
                                nodes_rect.height() + (padding * 2))
            return

        width, height = self._min_size
        self._sizer.set_pos(width, height)

    def pre_init(self, viewer, pos=None):
        """
        Called before node has been added into the scene.

        Args:
            viewer (NodeGraphQt.widgets.viewer.NodeViewer): main viewer.
            pos (tuple): cursor pos.
        """
        nodes = viewer.selected_nodes()
        if nodes:
            padding = 40
            scene = viewer.scene()
            group = scene.createItemGroup(nodes)
            rect = group.boundingRect()
            scene.destroyItemGroup(group)
            self.pos = (rect.x() - padding,
                        rect.y() - padding)
            self._sizer.set_pos(rect.width() + (padding * 2),
                                rect.height() + (padding * 2))
        else:
            self.pos = pos

    @property
    def minimum_size(self):
        return self._min_size

    @minimum_size.setter
    def minimum_size(self, size=(50, 50)):
        self._min_size = size

    @property
    def text(self):
        return self._properties['backdrop_text']

    @text.setter
    def text(self, text):
        self._properties['backdrop_text'] = text

    @AbstractNodeItem.width.setter
    def width(self, width=0.0):
        AbstractNodeItem.width.fset(self, width)
        self._sizer.set_pos(self._width, self._height)

    @AbstractNodeItem.height.setter
    def height(self, height=0.0):
        AbstractNodeItem.height.fset(self, height)
        self._sizer.set_pos(self._width, self._height)
