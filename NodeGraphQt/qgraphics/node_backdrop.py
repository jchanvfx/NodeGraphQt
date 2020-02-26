#!/usr/bin/python

from .. import QtGui, QtCore, QtWidgets
from ..constants import (Z_VAL_PIPE,
                         NODE_SEL_COLOR,
                         NODE_SEL_BORDER_COLOR)
from .node_abstract import AbstractNodeItem
from .pipe import Pipe
from .port import PortItem


class BackdropSizer(QtWidgets.QGraphicsItem):
    """
    Sizer item for resizing a backdrop item.

    Args:
        parent (BackdropNodeItem): the parent node item.
        size (float): sizer size.
    """

    def __init__(self, parent=None, size=6.0):
        super(BackdropSizer, self).__init__(parent)
        self.setFlag(self.ItemIsSelectable, True)
        self.setFlag(self.ItemIsMovable, True)
        self.setFlag(self.ItemSendsScenePositionChanges, True)
        self.setCursor(QtGui.QCursor(QtCore.Qt.SizeFDiagCursor))
        self.setToolTip('double-click auto resize')
        self._size = size

    @property
    def size(self):
        return self._size

    def set_pos(self, x, y):
        x -= self._size
        y -= self._size
        self.setPos(x, y)

    def boundingRect(self):
        return QtCore.QRectF(0.5, 0.5, self._size, self._size)

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

    def paint(self, painter, option, widget):
        """
        Draws the backdrop sizer on the bottom right corner.

        Args:
            painter (QtGui.QPainter): painter used for drawing the item.
            option (QtGui.QStyleOptionGraphicsItem):
                used to describe the parameters needed to draw.
            widget (QtWidgets.QWidget): not used.
        """
        painter.save()

        rect = self.boundingRect()
        item = self.parentItem()
        if item and item.selected:
            color = QtGui.QColor(*NODE_SEL_BORDER_COLOR)
        else:
            color = QtGui.QColor(*item.color)
            color = color.darker(110)
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

    Args:
        name (str): name displayed on the node.
        text (str): backdrop text.
        parent (QtWidgets.QGraphicsItem): parent item.
    """

    def __init__(self, name='backdrop', text='', parent=None):
        super(BackdropNodeItem, self).__init__(name, parent)
        self.setZValue(Z_VAL_PIPE - 1)
        self._properties['backdrop_text'] = text
        self._min_size = 80, 80
        self._sizer = BackdropSizer(self, 20.0)
        self._sizer.set_pos(*self._min_size)
        self._nodes = [self]

    def _combined_rect(self, nodes):
        group = self.scene().createItemGroup(nodes)
        rect = group.boundingRect()
        self.scene().destroyItemGroup(group)
        return rect

    def mouseDoubleClickEvent(self, event):
        viewer = self.viewer()
        if viewer:
            viewer.node_double_clicked.emit(self.id)
        super(BackdropNodeItem, self).mouseDoubleClickEvent(event)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            pos = event.scenePos()
            rect = QtCore.QRectF(pos.x() - 5, pos.y() - 5, 10, 10)
            item = self.scene().items(rect)[0]

            if isinstance(item, (PortItem, Pipe)):
                self.setFlag(self.ItemIsMovable, False)
                return
            if self.selected:
                return

            viewer = self.viewer()
            [n.setSelected(False) for n in viewer.selected_nodes()]

            self._nodes += self.get_nodes(False)
            [n.setSelected(True) for n in self._nodes]

    def mouseReleaseEvent(self, event):
        super(BackdropNodeItem, self).mouseReleaseEvent(event)
        self.setFlag(self.ItemIsMovable, True)
        [n.setSelected(True) for n in self._nodes]
        self._nodes = [self]

    def on_sizer_pos_changed(self, pos):
        self._width = pos.x() + self._sizer.size
        self._height = pos.y() + self._sizer.size

    def on_sizer_double_clicked(self):
        self.auto_resize()

    def paint(self, painter, option, widget):
        """
        Draws the backdrop rect.

        Args:
            painter (QtGui.QPainter): painter used for drawing the item.
            option (QtGui.QStyleOptionGraphicsItem):
                used to describe the parameters needed to draw.
            widget (QtWidgets.QWidget): not used.
        """
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

        if self.backdrop_text:
            painter.setPen(QtGui.QColor(*self.text_color))
            txt_rect = QtCore.QRectF(
                top_rect.x() + 5.0, top_rect.height() + 2.0,
                rect.width() - 5.0, rect.height())
            painter.setPen(QtGui.QColor(*self.text_color))
            painter.drawText(txt_rect,
                             QtCore.Qt.AlignLeft | QtCore.Qt.TextWordWrap,
                             self.backdrop_text)

        if self.selected and NODE_SEL_COLOR:
            sel_color = [x for x in NODE_SEL_COLOR]
            sel_color[-1] = 10
            painter.setBrush(QtGui.QColor(*sel_color))
            painter.setPen(QtCore.Qt.NoPen)
            painter.drawRect(rect)

        txt_rect = QtCore.QRectF(top_rect.x(), top_rect.y() + 1.2,
                                 rect.width(), top_rect.height())
        painter.setPen(QtGui.QColor(*self.text_color))
        painter.drawText(txt_rect, QtCore.Qt.AlignCenter, self.name)

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
        nodes = nodes or self.get_nodes(True)
        if nodes:
            padding = 40
            nodes_rect = self._combined_rect(nodes)
            self.xy_pos = [nodes_rect.x() - padding, nodes_rect.y() - padding]
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
            self.xy_pos = [rect.x() - padding, rect.y() - padding]
            self._sizer.set_pos(rect.width() + (padding * 2),
                                rect.height() + (padding * 2))
        else:
            self.xy_pos = pos

    @property
    def minimum_size(self):
        return self._min_size

    @minimum_size.setter
    def minimum_size(self, size=(50, 50)):
        self._min_size = size

    @property
    def backdrop_text(self):
        return self._properties['backdrop_text']

    @backdrop_text.setter
    def backdrop_text(self, text):
        self._properties['backdrop_text'] = text
        self.update(self.boundingRect())

    @AbstractNodeItem.width.setter
    def width(self, width=0.0):
        AbstractNodeItem.width.fset(self, width)
        self._sizer.set_pos(self._width, self._height)

    @AbstractNodeItem.height.setter
    def height(self, height=0.0):
        AbstractNodeItem.height.fset(self, height)
        self._sizer.set_pos(self._width, self._height)
