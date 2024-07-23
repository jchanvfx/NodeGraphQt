#!/usr/bin/python
from Qt import QtGui, QtCore, QtWidgets

from NodeGraphQt.constants import (
    PortTypeEnum, PortEnum,
    Z_VAL_PORT,
    ITEM_CACHE_MODE)


class PortItem(QtWidgets.QGraphicsItem):
    """
    Base Port Item.
    """

    def __init__(self, parent=None):
        super(PortItem, self).__init__(parent)
        self.setAcceptHoverEvents(True)
        self.setCacheMode(ITEM_CACHE_MODE)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, False)
        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsScenePositionChanges, True)
        self.setZValue(Z_VAL_PORT)
        self._pipes = []
        self._width = PortEnum.SIZE.value
        self._height = PortEnum.SIZE.value
        self._hovered = False
        self._name = 'port'
        self._display_name = True
        self._color = PortEnum.COLOR.value
        self._border_color = PortEnum.BORDER_COLOR.value
        self._border_size = 1
        self._port_type = None
        self._multi_connection = False
        self._locked = False

    def __str__(self):
        return '{}.PortItem("{}")'.format(self.__module__, self.name)

    def __repr__(self):
        return '{}.PortItem("{}")'.format(self.__module__, self.name)

    def boundingRect(self):
        return QtCore.QRectF(0.0, 0.0,
                             self._width + PortEnum.CLICK_FALLOFF.value,
                             self._height)

    def paint(self, painter, option, widget):
        """
        Draws the circular port.

        Args:
            painter (QtGui.QPainter): painter used for drawing the item.
            option (QtGui.QStyleOptionGraphicsItem):
                used to describe the parameters needed to draw.
            widget (QtWidgets.QWidget): not used.
        """
        painter.save()

        #  display falloff collision for debugging
        # ----------------------------------------------------------------------
        # pen = QtGui.QPen(QtGui.QColor(255, 255, 255, 80), 0.8)
        # pen.setStyle(QtCore.Qt.DotLine)
        # painter.setPen(pen)
        # painter.drawRect(self.boundingRect())
        # ----------------------------------------------------------------------

        rect_w = self._width / 1.8
        rect_h = self._height / 1.8
        rect_x = self.boundingRect().center().x() - (rect_w / 2)
        rect_y = self.boundingRect().center().y() - (rect_h / 2)
        port_rect = QtCore.QRectF(rect_x, rect_y, rect_w, rect_h)

        if self._hovered:
            color = QtGui.QColor(*PortEnum.HOVER_COLOR.value)
            border_color = QtGui.QColor(*PortEnum.HOVER_BORDER_COLOR.value)
        elif self.connected_pipes:
            color = QtGui.QColor(*PortEnum.ACTIVE_COLOR.value)
            border_color = QtGui.QColor(*PortEnum.ACTIVE_BORDER_COLOR.value)
        else:
            color = QtGui.QColor(*self.color)
            border_color = QtGui.QColor(*self.border_color)

        pen = QtGui.QPen(border_color, 1.8)
        painter.setPen(pen)
        painter.setBrush(color)
        painter.drawEllipse(port_rect)

        if self.connected_pipes and not self._hovered:
            painter.setBrush(border_color)
            w = port_rect.width() / 2.5
            h = port_rect.height() / 2.5
            rect = QtCore.QRectF(port_rect.center().x() - w / 2,
                                 port_rect.center().y() - h / 2,
                                 w, h)
            border_color = QtGui.QColor(*self.border_color)
            pen = QtGui.QPen(border_color, 1.6)
            painter.setPen(pen)
            painter.setBrush(border_color)
            painter.drawEllipse(rect)
        elif self._hovered:
            if self.multi_connection:
                pen = QtGui.QPen(border_color, 1.4)
                painter.setPen(pen)
                painter.setBrush(color)
                w = port_rect.width() / 1.8
                h = port_rect.height() / 1.8
            else:
                painter.setBrush(border_color)
                w = port_rect.width() / 3.5
                h = port_rect.height() / 3.5
            rect = QtCore.QRectF(port_rect.center().x() - w / 2,
                                 port_rect.center().y() - h / 2,
                                 w, h)
            painter.drawEllipse(rect)
        painter.restore()

    def itemChange(self, change, value):
        if change == QtWidgets.QGraphicsItem.ItemScenePositionHasChanged:
            self.redraw_connected_pipes()
        return super(PortItem, self).itemChange(change, value)

    def mousePressEvent(self, event):
        super(PortItem, self).mousePressEvent(event)
        
    def mouseReleaseEvent(self, event):
        super(PortItem, self).mouseReleaseEvent(event)

    def hoverEnterEvent(self, event):
        self._hovered = True
        super(PortItem, self).hoverEnterEvent(event)
        
    def hoverLeaveEvent(self, event):
        self._hovered = False
        super(PortItem, self).hoverLeaveEvent(event)

    def viewer_start_connection(self):
        viewer = self.scene().viewer()
        viewer.start_live_connection(self)

    def redraw_connected_pipes(self):
        if not self.connected_pipes:
            return
        for pipe in self.connected_pipes:
            if self.port_type == PortTypeEnum.IN.value:
                pipe.draw_path(self, pipe.output_port)
            elif self.port_type == PortTypeEnum.OUT.value:
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
        port_types = {
            PortTypeEnum.IN.value: 'output_port',
            PortTypeEnum.OUT.value: 'input_port'
        }
        for pipe in self.connected_pipes:
            ports.append(getattr(pipe, port_types[self.port_type]))
        return ports

    @property
    def hovered(self):
        return self._hovered

    @hovered.setter
    def hovered(self, value=False):
        self._hovered = value

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
    def display_name(self):
        return self._display_name

    @display_name.setter
    def display_name(self, display=True):
        self._display_name = display

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, color=(0, 0, 0, 255)):
        self._color = color
        self.update()

    @property
    def border_color(self):
        return self._border_color

    @border_color.setter
    def border_color(self, color=(0, 0, 0, 255)):
        self._border_color = color

    @property
    def border_size(self):
        return self._border_size

    @border_size.setter
    def border_size(self, size=2):
        self._border_size = size

    @property
    def locked(self):
        return self._locked

    @locked.setter
    def locked(self, value=False):
        self._locked = value
        conn_type = 'multi' if self.multi_connection else 'single'
        tooltip = '{}: ({})'.format(self.name, conn_type)
        if value:
            tooltip += ' (L)'
        self.setToolTip(tooltip)

    @property
    def multi_connection(self):
        return self._multi_connection

    @multi_connection.setter
    def multi_connection(self, mode=False):
        conn_type = 'multi' if mode else 'single'
        self.setToolTip('{}: ({})'.format(self.name, conn_type))
        self._multi_connection = mode

    @property
    def port_type(self):
        return self._port_type

    @port_type.setter
    def port_type(self, port_type):
        self._port_type = port_type

    def connect_to(self, port):
        if not port:
            for pipe in self.connected_pipes:
                pipe.delete()
            return
        if self.scene():
            viewer = self.scene().viewer()
            viewer.establish_connection(self, port)
        # redraw the ports.
        port.update()
        self.update()

    def disconnect_from(self, port):
        port_types = {
            PortTypeEnum.IN.value: 'output_port',
            PortTypeEnum.OUT.value: 'input_port'
        }
        for pipe in self.connected_pipes:
            connected_port = getattr(pipe, port_types[self.port_type])
            if connected_port == port:
                pipe.delete()
                break
        # redraw the ports.
        port.update()
        self.update()


class CustomPortItem(PortItem):
    """
    Custom port item for drawing custom shape port.
    """

    def __init__(self, parent=None, paint_func=None):
        super(CustomPortItem, self).__init__(parent)
        self._port_painter = paint_func

    def set_painter(self, func=None):
        """
        Set custom paint function for drawing.

        Args:
            func (function): paint function.
        """
        self._port_painter = func

    def paint(self, painter, option, widget):
        """
        Draws the port item.

        Args:
            painter (QtGui.QPainter): painter used for drawing the item.
            option (QtGui.QStyleOptionGraphicsItem):
                used to describe the parameters needed to draw.
            widget (QtWidgets.QWidget): not used.
        """
        if self._port_painter:
            rect_w = self._width / 1.8
            rect_h = self._height / 1.8
            rect_x = self.boundingRect().center().x() - (rect_w / 2)
            rect_y = self.boundingRect().center().y() - (rect_h / 2)
            port_rect = QtCore.QRectF(rect_x, rect_y, rect_w, rect_h)
            port_info = {
                'port_type': self.port_type,
                'color': self.color,
                'border_color': self.border_color,
                'multi_connection': self.multi_connection,
                'connected': bool(self.connected_pipes),
                'hovered': self.hovered,
                'locked': self.locked,
            }
            self._port_painter(painter, port_rect, port_info)
        else:
            super(CustomPortItem, self).paint(painter, option, widget)
