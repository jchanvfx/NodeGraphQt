#!/usr/bin/python
import uuid

from PySide import QtGui, QtCore

from .constants import (IN_PORT, OUT_PORT,
                        NODE_ICON_SIZE,
                        NODE_SEL_COLOR,
                        NODE_SEL_BORDER_COLOR)
from .port import PortItem

NODE_DATA = {
    'id': 0,
    'icon': 1,
    'name': 2,
    'color': 3,
    'border_color': 4,
    'text_color': 5,
    'size': 6,
    'item_icon': 7,
    'item_text': 8
}


class NodeItem(QtGui.QGraphicsItem):
    """
    Base Node item.
    """

    def __init__(self, name='node', node_id=None, parent=None):
        super(NodeItem, self).__init__(parent)
        self.setFlags(self.ItemIsSelectable | self.ItemIsMovable)
        self.setZValue(1)
        self._id = node_id or str(uuid.uuid4())
        self._width = 100
        self._height = 60

        self._icon = ''
        name = name.strip()
        self._name = name.replace(' ', '_')
        self._text_color = QtGui.QColor(107, 119, 129, 255)
        self._color = QtGui.QColor(31, 33, 34, 255)
        self._border_color = QtGui.QColor(58, 65, 68, 255)

        self._icon_item = None
        self._text_item = QtGui.QGraphicsTextItem(self.name, self)
        self._input_text_items = {}
        self._output_text_items = {}
        self._input_items = []
        self._output_items = []

    def __str__(self):
        return '{}({})'.format(self.__class__.__name__, self.name)

    def boundingRect(self):
        return QtCore.QRectF(0.0, 0.0, self._width, self._height)

    def paint(self, painter, option, widget):
        if self.isSelected():
            r, g, b, a = NODE_SEL_COLOR
            bg_color = QtGui.QColor(r, g, b, a)
            r, g, b, a = NODE_SEL_BORDER_COLOR
            border_color = QtGui.QColor(r, g, b, a)
        else:
            bg_color = self._color
            border_color = self._border_color

        rect = self.boundingRect()
        radius_x = 5
        radius_y = 5
        painter.setBrush(bg_color)
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawRoundRect(rect, radius_x, radius_y)

        label_rect = QtCore.QRectF(0.0, 0.0, self._width, 22)
        path = QtGui.QPainterPath()
        path.addRoundedRect(label_rect, radius_x, radius_y)
        painter.setBrush(QtGui.QColor(0, 0, 0, 60))
        painter.fillPath(path, painter.brush())

        path = QtGui.QPainterPath()
        path.addRoundedRect(rect, radius_x, radius_y)
        painter.setPen(QtGui.QPen(border_color, 2))
        painter.drawPath(path)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            start = PortItem().boundingRect().width()
            end = self.boundingRect().width() - start
            x_pos = event.pos().x()
            if not start <= x_pos <= end:
                self.setFlag(self.ItemIsMovable, False)
        super(NodeItem, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            start = PortItem().boundingRect().width()
            end = self.boundingRect().width() - start
            x_pos = event.pos().x()
            if not start <= x_pos <= end:
                self.setFlag(self.ItemIsMovable, True)
        super(NodeItem, self).mouseReleaseEvent(event)

    def itemChange(self, change, value):
        if change == self.ItemSelectedChange and self.scene():
            if value:
                self._hightlight_pipes()
            else:
                self._reset_pipes()
        return super(NodeItem, self).itemChange(change, value)

    def _activate_pipes(self):
        ports = self.inputs + self.outputs
        for port in ports:
            for pipe in port.connected_pipes:
                pipe.activate()

    def _hightlight_pipes(self):
        ports = self.inputs + self.outputs
        for port in ports:
            for pipe in port.connected_pipes:
                pipe.highlight()

    def _reset_pipes(self):
        ports = self.inputs + self.outputs
        for port in ports:
            for pipe in port.connected_pipes:
                pipe.reset()

    def _set_text_color(self, color):
        """
        Set color of the text for node.
        Args:
            color (QtGui.QColor): color value in QtGui.QColor(r, g, b, a).
        """
        for port, text in self._input_text_items.items():
            text.setDefaultTextColor(color)
        for port, text in self._output_text_items.items():
            text.setDefaultTextColor(color)
        self._text_item.setDefaultTextColor(color)

    def arrange_ports(self, width, height):
        """
        Arrange all input and output ports in the node layout.
    
        Args:
            width (int): node width 
            height: (int): node height
        """
        # adjust input position
        if self.inputs:
            port_width = self.inputs[0].boundingRect().width()
            chunk = (height / len(self.inputs))
            port_x = (port_width / 2) * -1
            port_y = chunk / 2
            for port in self.inputs:
                port.setPos(port_x, port_y)
                port_y += chunk
        # adjust input text position
        for port, text in self._input_text_items.items():
            txt_height = text.boundingRect().height() - 8.0
            txt_x = port.x() + port.boundingRect().width()
            txt_y = port.y() - (txt_height / 2)
            text.setPos(txt_x + 3.0, txt_y)
        # adjust output position
        if self.outputs:
            port_width = self.outputs[0].boundingRect().width()
            chunk = height / len(self.outputs)
            port_x = width - (port_width / 2)
            port_y = chunk / 2
            for port in self.outputs:
                port.setPos(port_x, port_y)
                port_y += chunk
        # adjust output text position
        for port, text in self._output_text_items.items():
            txt_width = text.boundingRect().width()
            txt_height = text.boundingRect().height() - 8.0
            txt_x = width - txt_width - (port.boundingRect().width() / 2)
            txt_y = port.y() - (txt_height / 2)
            text.setPos(txt_x - 1.0, txt_y)

    def offset_ports(self, offset_x=0.0, offset_y=0.0):
        """
        offset the node ports in the node layout.
        Args:
            offset_x (float): horizontal offset 
            offset_y (float): vertical offset
        """
        for port, text in self._input_text_items.items():
            port_x, port_y = port.pos().x(), port.pos().y()
            text_x, text_y = text.pos().x(), text.pos().y()
            port.setPos(port_x + offset_x, port_y + offset_y)
            text.setPos(text_x + offset_x, text_y + offset_y)
        for port, text in self._output_text_items.items():
            port_x, port_y = port.pos().x(), port.pos().y()
            text_x, text_y = text.pos().x(), text.pos().y()
            port.setPos(port_x + offset_x, port_y + offset_y)
            text.setPos(text_x + offset_x, text_y + offset_y)

    def init_node(self):
        """
        initialize the node layout.
        """
        width, height = self.size
        height += 28
        width += 20

        if width < self._width:
            width = self._width
        else:
            self._width = width
        if height < self._height:
            height = self._height
        else:
            self._height = height

        padding = 20.0
        padding_y = padding / 2
        height -= padding

        # adjust text position
        text_x = (width / 2) - (self._text_item.boundingRect().width() / 2)
        text_y = (self._text_item.boundingRect().height() / 2) * -1
        text_y += 1
        self._text_item.setPos(text_x, text_y + padding_y)

        # arrange inputs and outputs
        self.arrange_ports(width, height)
        # offset inputs and outputs
        self.offset_ports(0.0, 15.0)

        # arrange icon
        if self.icon:
            pixmap = QtGui.QPixmap(self.icon)
            pixmap = pixmap.scaledToHeight(
                NODE_ICON_SIZE, QtCore.Qt.SmoothTransformation)
            self._icon_item = QtGui.QGraphicsPixmapItem(pixmap, self)
            icon_rect = self._icon_item.boundingRect()
            icon_x = (width / 2) - (icon_rect.width() / 2)
            icon_y = (height / 2) - (icon_rect.height() / 2)
            self._icon_item.setPos(icon_x, icon_y)

        self._set_text_color(self._text_color)

    @property
    def id(self):
        return self._id

    @property
    def size(self):
        width = self._text_item.boundingRect().width() * 2
        if self.inputs:
            inport_widths = [
                (p.boundingRect().width() * 2) for p in self.inputs]
            width += max(inport_widths) * 2
        if self.outputs:
            outport_widths = [
                (p.boundingRect().width() * 2) for p in self.outputs]
            width += max(outport_widths) * 2
        port_count = max([len(self.inputs), len(self.outputs)]) + 1
        height = (PortItem().boundingRect().height() * 2) * port_count
        return width, height

    @property
    def icon(self):
        return self._icon

    @icon.setter
    def icon(self, path=None):
        self._icon = path

    @property
    def color(self):
        return self._color.toTuple()

    @color.setter
    def color(self, color=(0, 0, 0, 255)):
        self._color = QtGui.QColor(
            color[0], color[1], color[2], color[3]
        )

    @property
    def text_color(self):
        return self._text_color.toTuple()

    @text_color.setter
    def text_color(self, color=(100, 100, 100, 255)):
        self._text_color = QtGui.QColor(
            color[0], color[1], color[2], color[3]
        )
        self._set_text_color(self._text_color)

    @property
    def border_color(self):
        return self._border_color.toTuple()

    @border_color.setter
    def border_color(self, color=(0, 0, 0, 255)):
        self._border_color = QtGui.QColor(
            color[0], color[1], color[2], color[3]
        )

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name='node'):
        name = name.strip()
        name = name.strip().replace(' ', '_')
        self._name = name
        self._text_item.setPlainText(name)
        self.init_node()

    def add_input(self, name='input', multi_port=False):
        port = PortItem(self)
        port.name = name
        port.port_type = IN_PORT
        port.multi_connection = multi_port
        text = QtGui.QGraphicsTextItem(port.name, self)
        text.font().setPointSize(8)
        text.setFont(text.font())
        self._input_text_items[port] = text
        self._input_items.append(port)
        return port

    def add_output(self, name='output', multi_port=False):
        port = PortItem(self)
        port.name = name
        port.port_type = OUT_PORT
        port.multi_connection = multi_port
        text = QtGui.QGraphicsTextItem(port.name, self)
        text.font().setPointSize(8)
        text.setFont(text.font())
        self._output_text_items[port] = text
        self._output_items.append(port)
        return port

    @property
    def inputs(self):
        return self._input_items

    @property
    def outputs(self):
        return self._output_items

    def delete(self):
        for port in self._input_items:
            port.delete()
        for port in self._output_items:
            port.delete()
        if self.scene():
            self.scene().removeItem(self)
