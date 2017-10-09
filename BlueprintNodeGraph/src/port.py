#!/usr/bin/python
from PySide import QtGui, QtCore

from .constants import (
    IN_PORT, OUT_PORT,
    PORT_ACTIVE_COLOR,
    PORT_ACTIVE_BORDER_COLOR,
    Z_VAL_PORT)

PORT_DATA = {
    'name': 0,
    'color': 1,
    'border_color': 2,
    'border_size': 3,
    'type': 4,
    'multi_connection': 5,
    'display_name': 6
}


class PortItem(QtGui.QGraphicsItem):
    """
    Base Port item.
    """

    def __init__(self, parent=None):
        super(PortItem, self).__init__(parent)
        self.setAcceptHoverEvents(True)
        self.setFlag(self.ItemIsSelectable, False)
        self.setFlag(self.ItemSendsScenePositionChanges, True)
        self.setZValue(Z_VAL_PORT)
        self._pipes = []
        self._width = 10.0
        self._height = 10.0
        self.name = 'port'
        self.color = (49, 115, 100, 255)
        self.border_color = (29, 202, 151, 255)
        self.border_size = 1
        self.port_type = None
        self.multi_connection = False

    def __str__(self):
        return 'PortItem({})'.format(self.name)

    def boundingRect(self):
        return QtCore.QRectF(0.0, 0.0, self._width, self._height)

    def paint(self, painter, option, widget):
        if self.connected_pipes:
            r, g, b, a = PORT_ACTIVE_COLOR
            bdr_r, bdr_g, bdr_b, bdr_a = PORT_ACTIVE_BORDER_COLOR
        else:
            r, g, b, a = self.color
            bdr_r, bdr_g, bdr_b, bdr_a = self.border_color
        color = QtGui.QColor(r, g, b, a)
        border_color = QtGui.QColor(bdr_r, bdr_g, bdr_b, bdr_a)
        painter.setBrush(color)
        painter.setPen(QtGui.QPen(border_color, 1.5))
        painter.drawEllipse(self.boundingRect())

    def itemChange(self, change, value):
        if change == self.ItemScenePositionHasChanged:
            self.redraw_connected_pipes()
        return super(PortItem, self).itemChange(change, value)

    def mousePressEvent(self, event):
        if event.modifiers() != QtCore.Qt.AltModifier:
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
        port_types = {IN_PORT: 'output_port', OUT_PORT: 'input_port'}
        for pipe in self.connected_pipes:
            ports.append(getattr(pipe, port_types[self.port_type]))
        return ports

    @property
    def node(self):
        return self.parentItem()

    @property
    def name(self):
        return self.data(PORT_DATA['name'])

    @name.setter
    def name(self, name=''):
        self.setData(PORT_DATA['name'], name.strip())

    @property
    def display_name(self):
        return self.data(PORT_DATA['display_name'])

    @display_name.setter
    def display_name(self, display=True):
        self.setData(PORT_DATA['display_name'], display)

    @property
    def color(self):
        return self.data(PORT_DATA['color'])

    @color.setter
    def color(self, color=(0, 0, 0, 255)):
        self.setData(PORT_DATA['color'], color)

    @property
    def border_color(self):
        return self.data(PORT_DATA['border_color'])

    @border_color.setter
    def border_color(self, color=(0, 0, 0, 255)):
        self.setData(PORT_DATA['border_color'], color)

    @property
    def border_size(self):
        return self.data(PORT_DATA['border_size'])

    @border_size.setter
    def border_size(self, size=2):
        self.setData(PORT_DATA['border_size'], size)

    @property
    def multi_connection(self):
        return self.data(PORT_DATA['multi_connection'])

    @multi_connection.setter
    def multi_connection(self, mode=False):
        self.setData(PORT_DATA['multi_connection'], mode)

    @property
    def port_type(self):
        return self.data(PORT_DATA['type'])

    @port_type.setter
    def port_type(self, port_type):
        self.setData(PORT_DATA['type'], port_type)

    def delete(self):
        for pipe in self.connected_pipes:
            pipe.delete()
        if self.scene():
            self.scene().removeItem(self)
