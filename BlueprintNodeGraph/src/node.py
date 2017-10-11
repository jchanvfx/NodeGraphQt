#!/usr/bin/python
import uuid
from collections import OrderedDict

from PySide import QtGui, QtCore

from .constants import (IN_PORT, OUT_PORT,
                        NODE_ICON_SIZE, ICON_NODE_BASE,
                        NODE_SEL_COLOR, NODE_SEL_BORDER_COLOR,
                        Z_VAL_NODE)
from .port import PortItem
from .widgets import ComboNodeWidget, LineEditNodeWidget

NODE_DATA = {
    'id': 0,
    'icon': 1,
    'name': 2,
    'color': 3,
    'border_color': 4,
    'text_color': 5,
    'type': 6,
    'selected': 7
}


class NodeItem(QtGui.QGraphicsItem):
    """
    Base Node Item.
    """

    def __init__(self, name='node', parent=None):
        super(NodeItem, self).__init__(parent)
        self.setFlags(self.ItemIsSelectable | self.ItemIsMovable)
        self.setData(NODE_DATA['id'], str(uuid.uuid4()))
        self.setZValue(Z_VAL_NODE)
        self._width = 120
        self._height = 80

        self._name = name.strip().replace(' ', '_')
        self.setToolTip('node: {}'.format(self._name))
        pixmap = QtGui.QPixmap(ICON_NODE_BASE)
        pixmap = pixmap.scaledToHeight(
            NODE_ICON_SIZE, QtCore.Qt.SmoothTransformation)
        self._icon_item = QtGui.QGraphicsPixmapItem(pixmap, self)
        self._text_item = QtGui.QGraphicsTextItem(self.name, self)
        self._data_index = {}
        self._input_text_items = {}
        self._output_text_items = {}
        self._input_items = []
        self._output_items = []
        self._widgets = OrderedDict()

        self.text_color = (107, 119, 129, 255)
        self.color = (31, 33, 34, 255)
        self.border_color = (58, 65, 68, 255)

    def __str__(self):
        return '{}({})'.format(self.__class__.__name__, self.name)

    def boundingRect(self):
        return QtCore.QRectF(0.0, 0.0, self._width, self._height)

    def paint(self, painter, option, widget):
        r, g, b, a = self.color
        bdr_r, bdr_g, bdr_b, bdr_a = self.border_color
        if self.isSelected():
            if NODE_SEL_COLOR:
                r, g, b, a = NODE_SEL_COLOR
            if NODE_SEL_BORDER_COLOR:
                bdr_r, bdr_g, bdr_b, bdr_a = NODE_SEL_BORDER_COLOR

        bg_color = QtGui.QColor(r, g, b, a)
        border_color = QtGui.QColor(bdr_r, bdr_g, bdr_b, bdr_a)

        rect = self.boundingRect()
        radius_x = 5
        radius_y = 5
        painter.setBrush(bg_color)
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawRoundRect(rect, radius_x, radius_y)

        label_rect = QtCore.QRectF(0.0, 0.0, self._width, 28)
        path = QtGui.QPainterPath()
        path.addRoundedRect(label_rect, radius_x, radius_y)
        painter.setBrush(QtGui.QColor(0, 0, 0, 60))
        painter.fillPath(path, painter.brush())

        path = QtGui.QPainterPath()
        path.addRoundedRect(rect, radius_x, radius_y)
        painter.setPen(QtGui.QPen(border_color, 2))
        painter.drawPath(path)

    def mousePressEvent(self, event):
        if event.modifiers() == QtCore.Qt.AltModifier:
            event.ignore()
            return
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            start = PortItem().boundingRect().width()
            end = self.boundingRect().width() - start
            x_pos = event.pos().x()
            if not start <= x_pos <= end:
                event.ignore()
        super(NodeItem, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.modifiers() == QtCore.Qt.AltModifier:
            event.ignore()
            return
        super(NodeItem, self).mouseReleaseEvent(event)

    def itemChange(self, change, value):
        if change == self.ItemSelectedChange and self.scene():
            self._reset_pipes()
            if value:
                self._hightlight_pipes()
            self.setZValue(Z_VAL_NODE)
            if not self.selected:
                self.setZValue(Z_VAL_NODE + 1)

        return super(NodeItem, self).itemChange(change, value)

    def _activate_pipes(self):
        """
        active pipe color.
        """
        ports = self.inputs + self.outputs
        for port in ports:
            for pipe in port.connected_pipes:
                pipe.activate()

    def _hightlight_pipes(self):
        """
        highlight pipe color.
        """
        ports = self.inputs + self.outputs
        for port in ports:
            for pipe in port.connected_pipes:
                pipe.highlight()

    def _reset_pipes(self):
        """
        reset the pipe color.
        """
        ports = self.inputs + self.outputs
        for port in ports:
            for pipe in port.connected_pipes:
                pipe.reset()

    def _set_base_size(self):
        """
        setup the nodes initial base size.
        """
        width, height = self.calc_size()
        if width > self._width:
            self._width = width
        if height > self._height:
            self._height = height

    def _set_text_color(self, color):
        """
        set color of the text for node.

        Args:
            color (tuple): color value in (r, g, b, a).
        """
        r, g, b, a = color
        text_color = QtGui.QColor(r, g, b, a)
        for port, text in self._input_text_items.items():
            text.setDefaultTextColor(text_color)
        for port, text in self._output_text_items.items():
            text.setDefaultTextColor(text_color)
        self._text_item.setDefaultTextColor(text_color)

    def calc_size(self):
        """
        calculates the nodes minimum width and height.

        Returns:
            tuple: (width, height)
        """
        width = 0.0
        if self._widgets:
            widget_widths = [
                w.boundingRect().width() for w in self._widgets.values()]
            width = max(widget_widths)
        if self._text_item.boundingRect().width() > width:
            width = self._text_item.boundingRect().width()

        port_height = 0.0
        if self._input_text_items:
            input_widths = []
            for port, text in self._input_text_items.items():
                input_width = port.boundingRect().width() * 2
                if text.isVisible():
                    input_width += text.boundingRect().width()
                input_widths.append(input_width)
            width += max(input_widths)
            port = self._input_text_items.keys()[0]
            port_height = port.boundingRect().height() * 2
        if self._output_text_items:
            output_widths = []
            for port, text in self._output_text_items.items():
                output_width = port.boundingRect().width() * 2
                if text.isVisible():
                    output_width += text.boundingRect().width()
                output_widths.append(output_width)
            width += max(output_widths)
            port = self._output_text_items.keys()[0]
            port_height = port.boundingRect().height() * 2

        height = port_height * (max([len(self.inputs), len(self.outputs)]) + 2)
        if self._widgets:
            wid_height = sum(
                [w.boundingRect().height() for w in self._widgets.values()])
            if wid_height > height:
                height = wid_height + (wid_height / len(self._widgets))

        return width, height

    def arrange_icon(self):
        """
        Arrange node icon to the default top left of the node.
        """
        self._icon_item.setPos(2.0, 2.0)

    def arrange_label(self):
        """
        Arrange node label to the default top center of the node.
        """
        text_rect = self._text_item.boundingRect()
        text_x = (self._width / 2) - (text_rect.width() / 2)
        self._text_item.setPos(text_x, 1.0)

    def arrange_widgets(self):
        """
        Arrange node widgets to the default center of the node.
        """
        if not self._widgets:
            return
        wid_heights = sum(
            [w.boundingRect().height() for w in self._widgets.values()])
        pos_y = self._height / 2
        pos_y -= wid_heights / 2
        for name, widget in self._widgets.items():
            rect = widget.boundingRect()
            pos_x = (self._width / 2) - (rect.width() / 2)
            widget.setPos(pos_x, pos_y)
            pos_y += rect.height()

    def arrange_ports(self, padding_x=0.0, padding_y=0.0):
        """
        Arrange all input and output ports in the node layout.
    
        Args:
            padding_x (float): horizontal padding.
            padding_y: (float): vertical padding.
        """
        width = self._width - padding_x
        height = self._height - padding_y

        # adjust input position
        if self.inputs:
            port_width = self.inputs[0].boundingRect().width()
            port_height = self.inputs[0].boundingRect().height()
            chunk = (height / len(self.inputs))
            port_x = (port_width / 2) * -1
            port_y = (chunk / 2) - (port_height / 2)
            for port in self.inputs:
                port.setPos(port_x + padding_x, port_y + (padding_y / 2))
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
            port_height = self.outputs[0].boundingRect().height()
            chunk = height / len(self.outputs)
            port_x = width - (port_width / 2)
            port_y = (chunk / 2) - (port_height / 2)
            for port in self.outputs:
                port.setPos(port_x, port_y + (padding_y / 2))
                port_y += chunk
        # adjust output text position
        for port, text in self._output_text_items.items():
            txt_width = text.boundingRect().width()
            txt_height = text.boundingRect().height() - 8.0
            txt_x = width - txt_width - (port.boundingRect().width() / 2)
            txt_y = port.y() - (txt_height / 2)
            text.setPos(txt_x - 1.0, txt_y)

    def offset_icon(self, x=0.0, y=0.0):
        """
        offset the icon in the node layout.

        Args:
            x (float): horizontal x offset
            y (float): vertical y offset
        """
        if self._icon_item:
            icon_x = self._icon_item.pos().x() + x
            icon_y = self._icon_item.pos().y() + y
            self._icon_item.setPos(icon_x, icon_y)

    def offset_label(self, x=0.0, y=0.0):
        """
        offset the label in the node layout.

        Args:
            x (float): horizontal x offset
            y (float): vertical y offset
        """
        icon_x = self._text_item.pos().x() + x
        icon_y = self._text_item.pos().y() + y
        self._text_item.setPos(icon_x, icon_y)

    def offset_widgets(self, x=0.0, y=0.0):
        """
        offset the node widgets in the node layout.

        Args:
            x (float): horizontal x offset
            y (float): vertical y offset
        """
        for name, widget in self._widgets.items():
            pos_x = widget.pos().x()
            pos_y = widget.pos().y()
            widget.setPos(pos_x + x, pos_y + y)

    def offset_ports(self, x=0.0, y=0.0):
        """
        offset the node ports in the node layout.

        Args:
            x (float): horizontal x offset
            y (float): vertical y offset
        """
        for port, text in self._input_text_items.items():
            port_x, port_y = port.pos().x(), port.pos().y()
            text_x, text_y = text.pos().x(), text.pos().y()
            port.setPos(port_x + x, port_y + y)
            text.setPos(text_x + x, text_y + y)
        for port, text in self._output_text_items.items():
            port_x, port_y = port.pos().x(), port.pos().y()
            text_x, text_y = text.pos().x(), text.pos().y()
            port.setPos(port_x + x, port_y + y)
            text.setPos(text_x + x, text_y + y)

    def init_node(self):
        """
        initialize the node layout and form.
        """
        # setup initial base size.
        self._set_base_size()
        # set text color when node is initialized.
        self._set_text_color(self.text_color)
        # ----------------------------------------------------------------------

        # arrange label text
        self.arrange_label()
        self.offset_label(0.0, 3.0)
        # arrange icon
        self.arrange_icon()
        self.offset_icon(1.0, 0.0)
        # arrange node widgets
        self.arrange_widgets()
        self.offset_widgets(0.0, 10.0)
        # arrange input and output ports.
        self.arrange_ports(padding_x=0.0, padding_y=35.0)
        self.offset_ports(0.0, 15.0)

    @property
    def id(self):
        return self.data(NODE_DATA['id'])

    @id.setter
    def id(self, unique_id=''):
        return self.setData(NODE_DATA['id'], unique_id)

    @property
    def type(self):
        return self.data(NODE_DATA['type'])

    @type.setter
    def type(self, node_type='NODE'):
        self.setData(NODE_DATA['type'], node_type)

    @property
    def size(self):
        return self._width, self._height

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, width=0.0):
        w, h = self.calc_size()
        self._width = width if width > w else w

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, height):
        w, h = self.calc_size()
        h = 70 if h < 70 else h
        self._height = height if height > h else h

    @property
    def icon(self):
        return self.data(NODE_DATA['icon'])

    @icon.setter
    def icon(self, path=None):
        self.setData(NODE_DATA['icon'], path)
        path = path or ICON_NODE_BASE
        pixmap = QtGui.QPixmap(path)
        pixmap = pixmap.scaledToHeight(
            NODE_ICON_SIZE, QtCore.Qt.SmoothTransformation)
        self._icon_item.setPixmap(pixmap)
        if self.scene():
            self.init_node()

    @property
    def color(self):
        return self.data(NODE_DATA['color'])

    @color.setter
    def color(self, color=(0, 0, 0, 255)):
        self.setData(NODE_DATA['color'], color)

    @property
    def text_color(self):
        return self.data(NODE_DATA['text_color'])

    @text_color.setter
    def text_color(self, color=(100, 100, 100, 255)):
        self.setData(NODE_DATA['text_color'], color)
        self._set_text_color(color)

    @property
    def border_color(self):
        return self.data(NODE_DATA['border_color'])

    @border_color.setter
    def border_color(self, color=(0, 0, 0, 255)):
        self.setData(NODE_DATA['border_color'], color)

    @property
    def selected(self):
        return self.isSelected()

    @selected.setter
    def selected(self, selected=False):
        self.setSelected(selected)
        self.setData(NODE_DATA['selected'], selected)
        if selected:
            self._hightlight_pipes()

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name='node'):
        name = name.strip()
        name = name.replace(' ', '_')
        self._name = name
        self.setToolTip('node: {}'.format(self._name))
        self._text_item.setPlainText(name)
        if self.scene():
            self.init_node()

    @property
    def inputs(self):
        return self._input_items

    @property
    def outputs(self):
        return self._output_items

    def add_input(self, name='input', multi_port=False, display_name=True):
        port = PortItem(self)
        port.name = name
        port.port_type = IN_PORT
        port.multi_connection = multi_port
        port.display_name = display_name
        text = QtGui.QGraphicsTextItem(port.name, self)
        text.font().setPointSize(8)
        text.setFont(text.font())
        text.setVisible(display_name)
        self._input_text_items[port] = text
        self._input_items.append(port)
        if self.scene():
            self.init_node()
        return port

    def add_output(self, name='output', multi_port=False, display_name=True):
        port = PortItem(self)
        port.name = name
        port.port_type = OUT_PORT
        port.multi_connection = multi_port
        port.display_name = display_name
        text = QtGui.QGraphicsTextItem(port.name, self)
        text.font().setPointSize(8)
        text.setFont(text.font())
        text.setVisible(display_name)
        self._output_text_items[port] = text
        self._output_items.append(port)
        if self.scene():
            self.init_node()
        return port

    @property
    def widgets(self):
        return self._widgets

    def add_dropdown_menu(self, name='', label='', items=None):
        items = items or []
        data = str(items[0]) if items else ''
        self.set_knob_data(name, data)
        label = name if not label else label
        self._widgets[name] = ComboNodeWidget(self, name, label, items)
        self._widgets[name].setToolTip('knob: {}'.format(name))
        self._widgets[name].value_changed.connect(self.set_knob_data)

    def add_text_input(self, name='', label='', text=''):
        self.set_knob_data(name, text)
        label = name if not label else label
        self._widgets[name] = LineEditNodeWidget(self, name, label, text)
        self._widgets[name].setToolTip('knob: {}'.format(name))
        self._widgets[name].value_changed.connect(self.set_knob_data)

    def all_knob_data(self, include_default=True):
        data = {}
        for k, v in self._data_index.items():
            data[k] = self.data(v)
        if include_default:
            for k, v in NODE_DATA.items():
                data[k] = self.data(v)
        return data

    def get_knob_data(self, name):
        index = NODE_DATA.get(name)
        if not index:
            index = self._data_index.get(name)
        if not index:
            return None
        return self.data(index)

    def set_knob_data(self, name, data):
        if self._widgets.get(name):
            self._widgets.get(name).value = data
        if not NODE_DATA.get(name):
            index = max(self._data_index.values() + NODE_DATA.values()) + 1
            self._data_index[name] = index
            self.setData(index, data)
            return
        raise ValueError('knob name "{}" already exists.'.format(name))

    def delete(self):
        for port in self._input_items:
            port.delete()
        for port in self._output_items:
            port.delete()
        if self.scene():
            self.scene().removeItem(self)
