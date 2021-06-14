#!/usr/bin/python
from Qt import QtCore, QtGui, QtWidgets

from NodeGraphQt.constants import (NODE_SEL_BORDER_COLOR)
from NodeGraphQt.qgraphics.node_base import NodeItem


class GroupPortNodeItem(NodeItem):
    """
    Group Port Node item.

    Args:
        name (str): name displayed on the node.
        parent (QtWidgets.QGraphicsItem): parent item.
    """

    def __init__(self, name='group port', parent=None):
        super(GroupPortNodeItem, self).__init__(name, parent)
        self._x_item.text = 'Port Locked'
        self._icon_item.setVisible(False)

    def _set_base_size(self, add_w=0.0, add_h=0.0):
        self._width = 160 + add_h
        self._height = 60 + add_w

    def paint(self, painter, option, widget):
        """
        Draws the node base not the ports or text.

        Args:
            painter (QtGui.QPainter): painter used for drawing the item.
            option (QtGui.QStyleOptionGraphicsItem):
                used to describe the parameters needed to draw.
            widget (QtWidgets.QWidget): not used.
        """
        self.auto_switch_mode()

        painter.save()
        painter.setBrush(QtCore.Qt.NoBrush)
        painter.setPen(QtCore.Qt.NoPen)

        # base background.
        height = 4.0
        margin = 2.0
        rect = self.boundingRect()
        rect = QtCore.QRectF(rect.left() + margin,
                             rect.top() + margin,
                             rect.width() - (margin * 2),
                             rect.height() - (margin * 2))

        painter.setBrush(QtGui.QColor(255, 255, 255, 30))
        painter.drawRoundedRect(
            QtCore.QRectF(rect.x(), rect.y() + 15,
                          rect.width(), rect.height() - 30),
            3.0, 3.0)

        if self.selected:
            painter.setBrush(QtGui.QColor(*NODE_SEL_BORDER_COLOR))

        width = rect.width() / 4
        if self.inputs:
            rect_1 = QtCore.QRectF(
                rect.left(), rect.top(), width, height)
            rect_2 = QtCore.QRectF(
                rect.left(), rect.bottom() - height, width, height)
            painter.drawRoundedRect(rect_1, 3.0, 3.0)
            painter.drawRoundedRect(rect_2, 3.0, 3.0)
        if self.outputs:
            rect_1 = QtCore.QRectF(
                rect.right() - width, rect.top(), width, height)
            rect_2 = QtCore.QRectF(
                rect.right() - width, rect.bottom() - height, width, height)
            painter.drawRoundedRect(rect_1, 3.0, 3.0)
            painter.drawRoundedRect(rect_2, 3.0, 3.0)

        painter.restore()

    def set_proxy_mode(self, mode):
        """
        Set whether to draw the node with proxy mode.
        (proxy mode toggles visibility for some qgraphic items in the node.)

        Args:
            mode (bool): true to enable proxy mode.
        """
        if mode is self._proxy_mode:
            return
        self._proxy_mode = mode

        visible = not mode

        # disable overlay item.
        self._x_item.proxy_mode = self._proxy_mode

        # node widget visibility.
        for w in self._widgets.values():
            w.widget().setVisible(visible)

        # input port text visibility.
        for port, text in self._input_items.items():
            if port.display_name:
                text.setVisible(visible)

        # output port text visibility.
        for port, text in self._output_items.items():
            if port.display_name:
                text.setVisible(visible)

        self._text_item.setVisible(visible)

    def align_label(self, h_offset=0.0, v_offset=0.0):
        """
        Center node label text to the top of the node.

        Args:
            v_offset (float): vertical offset.
            h_offset (float): horizontal offset.
        """
        rect = self.boundingRect()
        text_rect = self._text_item.boundingRect()
        x = rect.center().x() - (text_rect.width() / 2)
        y = rect.center().y() - (text_rect.height() / 2)
        self._text_item.setPos(x + h_offset, y + v_offset)

    def align_ports(self, v_offset=0.0):
        """
        Align input, output ports in the node layout.
        """
        v_offset = self.boundingRect().height() / 2
        if self.inputs or self.outputs:
            for ports in [self.inputs, self.outputs]:
                if ports:
                    v_offset -= ports[0].boundingRect().height() / 2
                    break
        super(GroupPortNodeItem, self).align_ports(v_offset=v_offset)

    def draw_node(self):
        """
        Re-draw the node item in the scene.
        (re-implemented for vertical layout design)
        """
        height = self._text_item.boundingRect().height()

        # setup initial base size.
        self._set_base_size()
        # set text color when node is initialized.
        self._set_text_color(self.text_color)
        # set the tooltip
        self._tooltip_disable(self.disabled)

        # --- set the initial node layout ---
        # (do all the graphic item layout offsets here)

        # align label text
        self.align_label()
        # arrange icon
        self.align_icon()
        # arrange input and output ports.
        self.align_ports()
        # arrange node widgets
        self.align_widgets()

        self.update()

    def add_input(self, name='input', multi_port=False, display_name=True,
                  locked=False, painter_func=None):
        """
        Adds a port qgraphics item into the node with the "port_type" set as
        IN_PORT

        Args:
            name (str): name for the port.
            multi_port (bool): allow multiple connections.
            display_name (bool): (not used).
            locked (bool): locked state.
            painter_func (function): custom paint function.

        Returns:
            PortItem: port qgraphics item.
        """
        return super(GroupPortNodeItem, self).add_input(
            name, multi_port, False, locked, painter_func)

    def add_output(self, name='output', multi_port=False, display_name=True,
                   locked=False, painter_func=None):
        """
        Adds a port qgraphics item into the node with the "port_type" set as
        OUT_PORT

        Args:
            name (str): name for the port.
            multi_port (bool): allow multiple connections.
            display_name (bool): (not used).
            locked (bool): locked state.
            painter_func (function): custom paint function.

        Returns:
            PortItem: port qgraphics item.
        """
        return super(GroupPortNodeItem, self).add_output(
            name, multi_port, False, locked, painter_func)


class GroupPortNodeVerticalItem(GroupPortNodeItem):

    def paint(self, painter, option, widget):
        """
        Draws the node base not the ports or text.

        Args:
            painter (QtGui.QPainter): painter used for drawing the item.
            option (QtGui.QStyleOptionGraphicsItem):
                used to describe the parameters needed to draw.
            widget (QtWidgets.QWidget): not used.
        """
        self.auto_switch_mode()

        painter.save()
        painter.setBrush(QtCore.Qt.NoBrush)
        painter.setPen(QtCore.Qt.NoPen)

        # base background.
        height = 6.0
        margin = 2.0
        rect = self.boundingRect()
        rect = QtCore.QRectF(rect.left() + margin,
                             rect.top() + margin,
                             rect.width() - (margin * 2),
                             rect.height() - (margin * 2))

        painter.setBrush(QtGui.QColor(255, 255, 255, 30))
        painter.drawRoundedRect(
            QtCore.QRectF(rect.x(), rect.y() + 15,
                          rect.width(), rect.height() - 30),
            3.0, 3.0)

        if self.selected:
            painter.setBrush(QtGui.QColor(*NODE_SEL_BORDER_COLOR))

        spacer = 14
        width = rect.width() / 2 - spacer
        port_y_pos = [
            [bool(self.inputs), rect.top()],
            [bool(self.outputs), rect.bottom() - height]
        ]
        for draw, ypos in port_y_pos:
            if draw:
                rect_l = QtCore.QRectF(rect.left(), ypos, width, height)
                rect_r = QtCore.QRectF(rect.left() + width + (spacer * 2),
                                       ypos, width, height)
                painter.drawRoundedRect(rect_l, 3.0, 3.0)
                painter.drawRoundedRect(rect_r, 3.0, 3.0)

        painter.restore()

    def align_ports(self, v_offset=0.0):
        """
        Align input, output ports in the node layout.
        """

        # adjust input position
        inputs = [p for p in self.inputs if p.isVisible()]
        if inputs:
            port_width = inputs[0].boundingRect().width()
            port_height = inputs[0].boundingRect().height()
            half_width = port_width / 2
            delta = self._width / (len(inputs) + 1)
            port_x = delta
            port_y = (port_height / 3) * -1
            for port in inputs:
                port.setPos(port_x - half_width, port_y)
                port_x += delta

        # adjust output position
        outputs = [p for p in self.outputs if p.isVisible()]
        if outputs:
            port_width = outputs[0].boundingRect().width()
            port_height = outputs[0].boundingRect().height()
            half_width = port_width / 2
            delta = self._width / (len(outputs) + 1)
            port_x = delta
            port_y = self._height - port_height + (port_height / 3)
            for port in outputs:
                port.setPos(port_x - half_width, port_y)
                port_x += delta