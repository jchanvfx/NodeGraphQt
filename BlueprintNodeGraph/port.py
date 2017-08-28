#!/usr/bin/python
from PySide import QtGui, QtCore

from .constants import (IN_PORT, OUT_PORT,
                        PORT_ACTIVE_COLOR,
                        PORT_ACTIVE_BORDER_COLOR)


class PortItem(QtGui.QGraphicsItem):
    """
    Base Port item.
    """

    def __init__(self, parent=None):
        super(PortItem, self).__init__(parent)
        self.setAcceptHoverEvents(True)
        self.setFlag(self.ItemIsSelectable, False)
        self.setFlag(self.ItemSendsScenePositionChanges, True)
        self.setZValue(2)
        self._pipes = []
        self._width = 10.0
        self._height = 10.0
        self._name = 'port'
        self._type = None
        self._multi_connection = False
        self._color = QtGui.QColor(49, 115, 100, 255)
        self._border_color = QtGui.QColor(29, 202, 151, 255)
        self._border_size = 1

    def __str__(self):
        return 'Port({})'.format(self.name)

    def boundingRect(self):
        return QtCore.QRectF(0.0, 0.0, self._width, self._height)

    def paint(self, painter, option, widget):
        color = self._color
        border_color = self._border_color
        if self.connected_pipes:
            r, g, b, a = PORT_ACTIVE_COLOR
            color = QtGui.QColor(r, g, b, a)
            r, g, b, a = PORT_ACTIVE_BORDER_COLOR
            border_color = QtGui.QColor(r, g, b, a)
        painter.setBrush(color)
        painter.setPen(QtGui.QPen(border_color, 1.5))
        painter.drawEllipse(self.boundingRect())

    def itemChange(self, change, value):
        if change == self.ItemScenePositionHasChanged:
            self.redraw_connected_pipes()
        return super(PortItem, self).itemChange(change, value)

    def mousePressEvent(self, event):
        self.viewer_start_connection()
        super(PortItem, self).mousePressEvent(event)
        
    def mouseReleaseEvent(self, event):
        super(PortItem, self).mouseReleaseEvent(event)

    def viewer_start_connection(self):
        viewer = self.scene().viewer()
        viewer.start_connection(self)

    def redraw_connected_pipes(self):
        if not self.connected_pipes:
            return
        for pipe in self.connected_pipes:
            if self.port_type == IN_PORT:
                pipe.draw_path(self, pipe.output_port)
            elif self.port_type == OUT_PORT:
                pipe.draw_path(pipe.input_port, self)

    def add_pipe(self, pipe):
        self._pipes.append(pipe)

    def remove_pipe(self, pipe):
        self._pipes.remove(pipe)

    @property
    def connected_pipes(self):
        return self._pipes

    @property
    def connected_ports(self):
        ports = []
        for pipe in self.connected_pipes:
            if self.port_type == IN_PORT:
                ports.append(pipe.output_port)
            elif self.port_type == OUT_PORT:
                ports.append(pipe.input_port)
        return ports

    @property
    def node(self):
        return self.parentItem()

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name=''):
        self._name = name.strip()

    @property
    def color(self):
        return self._color.toTuple()

    @color.setter
    def color(self, color=(0, 0, 0, 255)):
        self._color = QtGui.QColor(
            color[0], color[1], color[2], color[3]
        )

    @property
    def border_color(self):
        return self._border_color.toTuple()

    @border_color.setter
    def border_color(self, color=(0, 0, 0, 255)):
        self._border_color = QtGui.QColor(
            color[0], color[1], color[2], color[3]
        )

    @property
    def border_size(self):
        return self._border_size

    @border_size.setter
    def border_size(self, size=2):
        self._border_size = size

    @property
    def multi_connection(self):
        return self._multi_connection

    @multi_connection.setter
    def multi_connection(self, mode=False):
        self._multi_connection = mode

    @property
    def port_type(self):
        return self._type

    @port_type.setter
    def port_type(self, port_type):
        self._type = port_type

    def delete(self):
        for pipe in self.connected_pipes:
            pipe.delete()
        if self.scene():
            self.scene().removeItem(self)
