#!/usr/bin/python
from PySide2 import QtGui, QtCore
from PySide2.QtWidgets import (QGraphicsItem,
                               QGraphicsPixmapItem,
                               QGraphicsTextItem)

from NodeGraphQt.widgets.constants import (IN_PORT, OUT_PORT,
                                           NODE_ICON_SIZE, ICON_NODE_BASE,
                                           NODE_SEL_COLOR, NODE_SEL_BORDER_COLOR,
                                           Z_VAL_NODE, Z_VAL_NODE_WIDGET)

from NodeGraphQt.widgets.graphics_widgets import (NodeBaseWidget,
                                                  NodeComboBox,
                                                  NodeLineEdit,
                                                  NodeCheckBox)
from NodeGraphQt.widgets.node_abstract import AbstractNodeItem
from NodeGraphQt.widgets.port import PortItem


class XDisabledItem(QGraphicsItem):

    def __init__(self, parent=None, text=None):
        super(XDisabledItem, self).__init__(parent)
        self.setZValue(Z_VAL_NODE_WIDGET + 2)
        self.setVisible(False)
        self.color = (0, 0, 0, 255)
        self.text = text

    def boundingRect(self):
        return self.parentItem().boundingRect()

    def paint(self, painter, option, widget):
        painter.save()

        margin = 20
        rect = self.boundingRect()
        dis_rect = QtCore.QRectF(rect.left() - (margin / 2),
                                 rect.top() - (margin / 2),
                                 rect.width() + margin,
                                 rect.height() + margin)
        pen = QtGui.QPen(QtGui.QColor(*self.color), 8)
        pen.setCapStyle(QtCore.Qt.RoundCap)
        painter.setPen(pen)
        painter.drawLine(dis_rect.topLeft(), dis_rect.bottomRight())
        painter.drawLine(dis_rect.topRight(), dis_rect.bottomLeft())

        bg_color = QtGui.QColor(*self.color)
        bg_color.setAlpha(100)
        bg_margin = -0.5
        bg_rect = QtCore.QRectF(dis_rect.left() - (bg_margin / 2),
                                dis_rect.top() - (bg_margin / 2),
                                dis_rect.width() + bg_margin,
                                dis_rect.height() + bg_margin)
        painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0, 0)))
        painter.setBrush(bg_color)
        painter.drawRoundedRect(bg_rect, 5, 5)

        pen = QtGui.QPen(QtGui.QColor(155, 0, 0, 255), 0.7)
        painter.setPen(pen)
        painter.drawLine(dis_rect.topLeft(), dis_rect.bottomRight())
        painter.drawLine(dis_rect.topRight(), dis_rect.bottomLeft())

        point_size = 4.0
        point_pos = (dis_rect.topLeft(), dis_rect.topRight(),
                     dis_rect.bottomLeft(), dis_rect.bottomRight())
        painter.setBrush(QtGui.QColor(255, 0, 0, 255))
        for p in point_pos:
            p.setX(p.x() - (point_size / 2))
            p.setY(p.y() - (point_size / 2))
            point_rect = QtCore.QRectF(
                p, QtCore.QSizeF(point_size, point_size))
            painter.drawEllipse(point_rect)

        if self.text:
            font = painter.font()
            font.setPointSize(10)

            painter.setFont(font)
            font_metrics = QtGui.QFontMetrics(font)
            font_width = font_metrics.width(self.text)
            font_height = font_metrics.height()
            txt_w = font_width * 1.25
            txt_h = font_height * 2.25
            text_bg_rect = QtCore.QRectF((rect.width() / 2) - (txt_w / 2),
                                         (rect.height() / 2) - (txt_h / 2),
                                         txt_w, txt_h)
            painter.setPen(QtGui.QPen(QtGui.QColor(255, 0, 0), 0.5))
            painter.setBrush(QtGui.QColor(*self.color))
            painter.drawRoundedRect(text_bg_rect, 2, 2)

            text_rect = QtCore.QRectF((rect.width() / 2) - (font_width / 2),
                                      (rect.height() / 2) - (font_height / 2),
                                      txt_w * 2, font_height * 2)

            painter.setPen(QtGui.QPen(QtGui.QColor(255, 0, 0), 1))
            painter.drawText(text_rect, self.text)

        painter.restore()


class NodeItem(AbstractNodeItem):
    """
    Base Node item.
    """

    def __init__(self, name='node', parent=None):
        super(NodeItem, self).__init__(name, parent)
        pixmap = QtGui.QPixmap(ICON_NODE_BASE)
        pixmap = pixmap.scaledToHeight(NODE_ICON_SIZE,
                                       QtCore.Qt.SmoothTransformation)
        self._properties['icon'] = ICON_NODE_BASE
        self._icon_item = QGraphicsPixmapItem(pixmap, self)
        self._text_item = QGraphicsTextItem(self.name, self)
        self._x_item = XDisabledItem(self, 'node disabled')
        self._input_items = {}
        self._output_items = {}
        self._widgets = {}

    def paint(self, painter, option, widget):
        painter.save()

        bg_border = 1.0
        rect = QtCore.QRectF(0.5 - (bg_border / 2),
                             0.5 - (bg_border / 2),
                             self._width + bg_border,
                             self._height + bg_border)
        radius_x = 5
        radius_y = 5
        path = QtGui.QPainterPath()
        path.addRoundedRect(rect, radius_x, radius_y)
        painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0, 255), 1.5))
        painter.drawPath(path)

        rect = self.boundingRect()
        bg_color = QtGui.QColor(*self.color)
        painter.setBrush(bg_color)
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawRoundRect(rect, radius_x, radius_y)

        if self.selected and NODE_SEL_COLOR:
            painter.setBrush(QtGui.QColor(*NODE_SEL_COLOR))
            painter.drawRoundRect(rect, radius_x, radius_y)

        label_rect = QtCore.QRectF(rect.left() + (radius_x / 2),
                                   rect.top() + (radius_x / 2),
                                   self._width - (radius_x / 1.25),
                                   28)
        path = QtGui.QPainterPath()
        path.addRoundedRect(label_rect, radius_x / 1.5, radius_y / 1.5)
        painter.setBrush(QtGui.QColor(0, 0, 0, 50))
        painter.fillPath(path, painter.brush())

        border_width = 0.8
        border_color = QtGui.QColor(*self.border_color)
        if self.selected and NODE_SEL_BORDER_COLOR:
            border_width = 1.2
            border_color = QtGui.QColor(*NODE_SEL_BORDER_COLOR)
        border_rect = QtCore.QRectF(rect.left() - (border_width / 2),
                                    rect.top() - (border_width / 2),
                                    rect.width() + border_width,
                                    rect.height() + border_width)
        path = QtGui.QPainterPath()
        path.addRoundedRect(border_rect, radius_x, radius_y)
        painter.setBrush(QtCore.Qt.NoBrush)
        painter.setPen(QtGui.QPen(border_color, border_width))
        painter.drawPath(path)

        painter.restore()

    def mousePressEvent(self, event):
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
            self.reset_pipes()
            if value:
                self.hightlight_pipes()
            self.setZValue(Z_VAL_NODE)
            if not self.selected:
                self.setZValue(Z_VAL_NODE + 1)

        return super(NodeItem, self).itemChange(change, value)

    def _tooltip_disable(self, state):
        tooltip = '<b>{}</b>'.format(self._properties['name'])
        if state:
            tooltip += ' <font color="red"><b>(DISABLED)</b></font>'
        tooltip += '<br/>{}<br/>'.format(self._properties['type'])
        self.setToolTip(tooltip)

    def _set_base_size(self):
        """
        setup initial base size.
        """
        width, height = self.calc_size()
        if width > self._width:
            self._width = width
        if height > self._height:
            self._height = height

    def _set_text_color(self, color):
        """
        set text color.

        Args:
            color (tuple): color value in (r, g, b, a).
        """
        text_color = QtGui.QColor(*color)
        for port, text in self._input_items.items():
            text.setDefaultTextColor(text_color)
        for port, text in self._output_items.items():
            text.setDefaultTextColor(text_color)
        self._text_item.setDefaultTextColor(text_color)

    def activate_pipes(self):
        """
        active pipe color.
        """
        ports = self.inputs + self.outputs
        for port in ports:
            for pipe in port.connected_pipes:
                pipe.activate()

    def hightlight_pipes(self):
        """
        highlight pipe color.
        """
        ports = self.inputs + self.outputs
        for port in ports:
            for pipe in port.connected_pipes:
                pipe.highlight()

    def reset_pipes(self):
        """
        reset the pipe color.
        """
        ports = self.inputs + self.outputs
        for port in ports:
            for pipe in port.connected_pipes:
                pipe.reset()

    def calc_size(self):
        """
        calculate minimum node size.
        """
        width = 0.0
        if self._widgets:
            widget_widths = [
                w.boundingRect().width() for w in self._widgets.values()]
            width = max(widget_widths)
        if self._text_item.boundingRect().width() > width:
            width = self._text_item.boundingRect().width()

        port_height = 0.0
        if self._input_items:
            input_widths = []
            for port, text in self._input_items.items():
                input_width = port.boundingRect().width() * 2
                if text.isVisible():
                    input_width += text.boundingRect().width()
                input_widths.append(input_width)
            width += max(input_widths)
            port = list(self._input_items.keys())[0]
            port_height = port.boundingRect().height() * 2
        if self._output_items:
            output_widths = []
            for port, text in self._output_items.items():
                output_width = port.boundingRect().width() * 2
                if text.isVisible():
                    output_width += text.boundingRect().width()
                output_widths.append(output_width)
            width += max(output_widths)
            port = list(self._output_items.keys())[0]
            port_height = port.boundingRect().height() * 2

        height = port_height * (max([len(self.inputs), len(self.outputs)]) + 2)
        if self._widgets:
            wid_height = sum(
                [w.boundingRect().height() for w in self._widgets.values()])
            if wid_height > height:
                height = wid_height + (wid_height / len(self._widgets))

        height += 10

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
        Arrange input, output ports in the node layout.
    
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
        for port, text in self._input_items.items():
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
        for port, text in self._output_items.items():
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
        offset the ports in the node layout.

        Args:
            x (float): horizontal x offset
            y (float): vertical y offset
        """
        for port, text in self._input_items.items():
            port_x, port_y = port.pos().x(), port.pos().y()
            text_x, text_y = text.pos().x(), text.pos().y()
            port.setPos(port_x + x, port_y + y)
            text.setPos(text_x + x, text_y + y)
        for port, text in self._output_items.items():
            port_x, port_y = port.pos().x(), port.pos().y()
            text_x, text_y = text.pos().x(), text.pos().y()
            port.setPos(port_x + x, port_y + y)
            text.setPos(text_x + x, text_y + y)

    def post_init(self, viewer=None, pos=None):
        """
        Called after node has been added into the scene.
        Adjust the node layout and form after the node has been added.

        Args:
            viewer (NodeGraphQt.widgets.viewer.NodeViewer): not used
            pos (tuple): cursor position.
        """
        # set initial node position.
        if pos:
            self.setPos(pos[0], pos[1])

        # setup initial base size.
        self._set_base_size()
        # set text color when node is initialized.
        self._set_text_color(self.text_color)
        # set the tooltip
        self._tooltip_disable(self.disabled)

        # setup node layout
        # =================

        # arrange label text
        self.arrange_label()
        self.offset_label(0.0, 5.0)

        # arrange icon
        self.arrange_icon()
        self.offset_icon(5.0, 2.0)

        # arrange node widgets
        self.arrange_widgets()
        self.offset_widgets(0.0, 10.0)

        # arrange input and output ports.
        self.arrange_ports(padding_y=35.0)
        self.offset_ports(0.0, 15.0)

    @property
    def icon(self):
        return self._properties['icon']

    @icon.setter
    def icon(self, path=None):
        self._properties['icon'] = path
        path = path or ICON_NODE_BASE
        pixmap = QtGui.QPixmap(path)
        pixmap = pixmap.scaledToHeight(NODE_ICON_SIZE,
                                       QtCore.Qt.SmoothTransformation)
        self._icon_item.setPixmap(pixmap)
        if self.scene():
            self.post_init()

    @AbstractNodeItem.width.setter
    def width(self, width=0.0):
        w, h = self.calc_size()
        # self._width = width if width > w else w
        width = width if width > w else w
        AbstractNodeItem.width.fset(self, width)

    @AbstractNodeItem.height.setter
    def height(self, height=0.0):
        w, h = self.calc_size()
        h = 70 if h < 70 else h
        # self._height = height if height > h else h
        height = height if height > h else h
        AbstractNodeItem.height.fset(self, height)

    @AbstractNodeItem.disabled.setter
    def disabled(self, state=False):
        AbstractNodeItem.disabled.fset(self, state)
        for n, w in self._widgets.items():
            w.widget.setDisabled(state)
        self._tooltip_disable(state)
        self._x_item.setVisible(state)

    @AbstractNodeItem.selected.setter
    def selected(self, selected=False):
        AbstractNodeItem.selected.fset(self, selected)
        if selected:
            self.hightlight_pipes()

    @AbstractNodeItem.name.setter
    def name(self, name=''):
        AbstractNodeItem.name.fset(self, name)
        self._text_item.setPlainText(name)
        if self.scene():
            self.post_init()

    @property
    def inputs(self):
        return list(self._input_items.keys())

    @property
    def outputs(self):
        return list(self._output_items.keys())

    def add_input(self, name='input', multi_port=False, display_name=True):
        """
        Args:
            name (str): name for the port.
            multi_port (bool): allow multiple connections.
            display_name (bool): display the port name. 

        Returns:
            PortItem: input item widget
        """
        port = PortItem(self)
        port.name = name
        port.port_type = IN_PORT
        port.multi_connection = multi_port
        port.display_name = display_name
        text = QGraphicsTextItem(port.name, self)
        text.font().setPointSize(8)
        text.setFont(text.font())
        text.setVisible(display_name)
        self._input_items[port] = text
        if self.scene():
            self.post_init()
        return port

    def add_output(self, name='output', multi_port=False, display_name=True):
        """
        Args:
            name (str): name for the port.
            multi_port (bool): allow multiple connections.
            display_name (bool): display the port name. 

        Returns:
            PortItem: output item widget
        """
        port = PortItem(self)
        port.name = name
        port.port_type = OUT_PORT
        port.multi_connection = multi_port
        port.display_name = display_name
        text = QGraphicsTextItem(port.name, self)
        text.font().setPointSize(8)
        text.setFont(text.font())
        text.setVisible(display_name)
        self._output_items[port] = text
        if self.scene():
            self.post_init()
        return port

    @property
    def widgets(self):
        return dict(self._widgets)

    def add_combo_menu(self, name='', label='', items=None, tooltip=''):
        items = items or []
        widget = NodeComboBox(self, name, label, items)
        widget.setToolTip(tooltip)
        self.add_widget(widget)
        return widget

    def add_text_input(self, name='', label='', text='', tooltip=''):
        widget = NodeLineEdit(self, name, label, text)
        widget.setToolTip(tooltip)
        self.add_widget(widget)
        return widget

    def add_checkbox(self, name='', label='', text='', state=False, tooltip=''):
        widget = NodeCheckBox(self, name, label, text, state)
        widget.setToolTip(tooltip)
        self.add_widget(widget)
        return widget

    def add_widget(self, widget):
        if isinstance(widget, NodeBaseWidget):
            self._widgets[widget.name] = widget
        else:
            raise TypeError('{} is not an instance of a node widget.')

    def get_widget(self, name):
        widget = self._widgets.get(name)
        if widget:
            return widget
        raise KeyError('node has no widget "{}"'.format(name))

    def delete(self):
        for port, text in self._input_items.items():
            port.delete()
        for port, text in self._output_items.items():
            port.delete()
        super(NodeItem, self).delete()

    def from_dict(self, node_dict):
        super(NodeItem, self).from_dict(node_dict)
        widgets = node_dict.pop('widgets', {})
        for name, value in widgets.items():
            if self._widgets.get(name):
                self._widgets[name].value = value
