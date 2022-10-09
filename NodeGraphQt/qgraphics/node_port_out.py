#!/usr/bin/python
from Qt import QtCore, QtGui, QtWidgets

from NodeGraphQt.constants import NodeEnum
from NodeGraphQt.qgraphics.node_base import NodeItem


class PortOutputNodeItem(NodeItem):
    """
    Output Port Node item.

    Args:
        name (str): name displayed on the node.
        parent (QtWidgets.QGraphicsItem): parent item.
    """

    def __init__(self, name='group port', parent=None):
        super(PortOutputNodeItem, self).__init__(name, parent)
        self._icon_item.setVisible(False)
        self._text_item.set_locked(True)
        self._x_item.text = 'Port Locked'

    def _set_base_size(self, add_w=0.0, add_h=0.0):
        width, height = self.calc_size(add_w, add_h)
        self._width = width + 60
        self._height = height if height >= 60 else 60

    def _paint_horizontal(self, painter, option, widget):
        self.auto_switch_mode()

        painter.save()
        painter.setBrush(QtCore.Qt.NoBrush)
        painter.setPen(QtCore.Qt.NoPen)

        margin = 2.0
        rect = self.boundingRect()
        rect = QtCore.QRectF(rect.left() + margin,
                             rect.top() + margin,
                             rect.width() - (margin * 2),
                             rect.height() - (margin * 2))

        text_rect = self._text_item.boundingRect()
        text_rect = QtCore.QRectF(
            rect.center().x() - (text_rect.width() / 2) - 5,
            rect.center().y() - (text_rect.height() / 2),
            text_rect.width() + 10,
            text_rect.height()
        )

        painter.setBrush(QtGui.QColor(255, 255, 255, 20))
        painter.drawRoundedRect(rect, 20, 20)

        painter.setBrush(QtGui.QColor(0, 0, 0, 100))
        painter.drawRoundedRect(text_rect, 3, 3)

        size = int(rect.height() / 4)
        triangle = QtGui.QPolygonF()
        triangle.append(QtCore.QPointF(-size, size))
        triangle.append(QtCore.QPointF(0.0, 0.0))
        triangle.append(QtCore.QPointF(size, size))

        transform = QtGui.QTransform()
        transform.translate(rect.x() + (size / 3), rect.center().y())
        transform.rotate(-90)
        poly = transform.map(triangle)

        if self.selected:
            pen = QtGui.QPen(
                QtGui.QColor(*NodeEnum.SELECTED_BORDER_COLOR.value), 1.3
            )
            painter.setBrush(QtGui.QColor(*NodeEnum.SELECTED_COLOR.value))
        else:
            pen = QtGui.QPen(QtGui.QColor(*self.border_color), 1.2)
            painter.setBrush(QtGui.QColor(0, 0, 0, 50))

        pen.setJoinStyle(QtCore.Qt.MiterJoin)
        painter.setPen(pen)
        painter.drawPolygon(poly)

        edge_size = 30
        edge_rect = QtCore.QRectF(rect.x() + (size * 1.6),
                                  rect.center().y() - (edge_size / 2),
                                  4, edge_size)
        painter.drawRect(edge_rect)

        painter.restore()

    def _paint_vertical(self, painter, option, widget):
        self.auto_switch_mode()

        painter.save()
        painter.setBrush(QtCore.Qt.NoBrush)
        painter.setPen(QtCore.Qt.NoPen)

        margin = 2.0
        rect = self.boundingRect()
        rect = QtCore.QRectF(rect.left() + margin,
                             rect.top() + margin,
                             rect.width() - (margin * 2),
                             rect.height() - (margin * 2))

        text_rect = self._text_item.boundingRect()
        text_rect = QtCore.QRectF(
            rect.center().x() - (text_rect.width() / 2) - 5,
            rect.height() - text_rect.height(),
            text_rect.width() + 10,
            text_rect.height()
        )

        painter.setBrush(QtGui.QColor(255, 255, 255, 20))
        painter.drawRoundedRect(rect, 20, 20)

        painter.setBrush(QtGui.QColor(0, 0, 0, 100))
        painter.drawRoundedRect(text_rect, 3, 3)

        size = int(rect.height() / 4)
        triangle = QtGui.QPolygonF()
        triangle.append(QtCore.QPointF(-size, size))
        triangle.append(QtCore.QPointF(0.0, 0.0))
        triangle.append(QtCore.QPointF(size, size))

        transform = QtGui.QTransform()
        transform.translate(rect.center().x(), rect.y() + (size / 3))
        # transform.rotate(-90)
        poly = transform.map(triangle)

        if self.selected:
            pen = QtGui.QPen(
                QtGui.QColor(*NodeEnum.SELECTED_BORDER_COLOR.value), 1.3
            )
            painter.setBrush(QtGui.QColor(*NodeEnum.SELECTED_COLOR.value))
        else:
            pen = QtGui.QPen(QtGui.QColor(*self.border_color), 1.2)
            painter.setBrush(QtGui.QColor(0, 0, 0, 50))

        pen.setJoinStyle(QtCore.Qt.MiterJoin)
        painter.setPen(pen)
        painter.drawPolygon(poly)

        edge_size = 30
        edge_rect = QtCore.QRectF(rect.center().x() - (edge_size / 2),
                                  rect.y() + (size * 1.6),
                                  edge_size, 4)
        painter.drawRect(edge_rect)

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

    def _align_label_horizontal(self, h_offset, v_offset):
        rect = self.boundingRect()
        text_rect = self._text_item.boundingRect()
        x = rect.center().x() - (text_rect.width() / 2)
        y = rect.center().y() - (text_rect.height() / 2)
        self._text_item.setPos(x + h_offset, y + v_offset)

    def _align_label_vertical(self, h_offset, v_offset):
        rect = self.boundingRect()
        text_rect = self._text_item.boundingRect()
        x = rect.center().x() - (text_rect.width() / 1.5) - 2.0
        y = rect.height() - text_rect.height() - 4.0
        self._text_item.setPos(x + h_offset, y + v_offset)

    def _align_ports_horizontal(self, v_offset):
        """
        Align input, output ports in the node layout.
        """
        v_offset = self.boundingRect().height() / 2
        if self.inputs or self.outputs:
            for ports in [self.inputs, self.outputs]:
                if ports:
                    v_offset -= ports[0].boundingRect().height() / 2
                    break
        super(PortOutputNodeItem, self)._align_ports_horizontal(v_offset)

    def _align_ports_vertical(self, v_offset):
        super(PortOutputNodeItem, self)._align_ports_vertical(v_offset)

    def _draw_node_horizontal(self):
        """
        Re-draw the node item in the scene.
        (re-implemented for vertical layout design)
        """
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
        # align icon
        self.align_icon()
        # arrange input and output ports.
        self.align_ports()
        # arrange node widgets
        self.align_widgets()

        self.update()
