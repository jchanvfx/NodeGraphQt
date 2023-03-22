#!/usr/bin/python
from Qt import QtCore, QtGui, QtWidgets

from NodeGraphQt.constants import NodeEnum, PortEnum
from NodeGraphQt.qgraphics.node_base import NodeItem


class CircleNodeItem(NodeItem):
    """
    Circle Node item.

    Args:
        name (str): name displayed on the node.
        parent (QtWidgets.QGraphicsItem): parent item.
    """

    def __init__(self, name='circle', parent=None):
        super(CircleNodeItem, self).__init__(name, parent)

    def _align_ports_horizontal(self, v_offset):
        width = self._width
        txt_offset = PortEnum.CLICK_FALLOFF.value - 2
        spacing = 1

        # adjust input position
        inputs = [p for p in self.inputs if p.isVisible()]
        if inputs:
            port_width = inputs[0].boundingRect().width()
            port_height = inputs[0].boundingRect().height()
            port_x = (port_width / 2) * -1
            port_y = v_offset
            for port in inputs:
                port.setPos(port_x, port_y)
                port_y += port_height + spacing
        # adjust input text position
        for port, text in self._input_items.items():
            if port.isVisible():
                txt_x = port.boundingRect().width() / 2 - txt_offset
                text.setPos(txt_x, port.y() - 1.5)

        # adjust output position
        outputs = [p for p in self.outputs if p.isVisible()]
        if outputs:
            port_width = outputs[0].boundingRect().width()
            port_height = outputs[0].boundingRect().height()
            port_x = width - (port_width / 2)
            port_y = v_offset
            for port in outputs:
                port.setPos(port_x, port_y)
                port_y += port_height + spacing
        # adjust output text position
        for port, text in self._output_items.items():
            if port.isVisible():
                txt_width = text.boundingRect().width() - txt_offset
                txt_x = port.x() - txt_width
                text.setPos(txt_x, port.y() - 1.5)

    def _align_ports_vertical(self, v_offset):
        # adjust input position
        inputs = [p for p in self.inputs if p.isVisible()]
        if inputs:
            port_width = inputs[0].boundingRect().width()
            port_height = inputs[0].boundingRect().height()
            half_width = port_width / 2
            delta = self._width / (len(inputs) + 1)
            port_x = delta
            port_y = (port_height / 2) * -1
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
            port_y = self._height - (port_height / 2)
            for port in outputs:
                port.setPos(port_x - half_width, port_y)
                port_x += delta

    def _paint_horizontal(self, painter, option, widget):
        painter.save()

        text_rect = self._text_item.boundingRect()
        text_width = text_rect.width()
        if text_width < 20.0:
            text_width = 20.0

        text_rect = QtCore.QRectF(
            self.boundingRect().center().x() - (text_width / 2),
            self.boundingRect().center().y() - (text_rect.height() / 2),
            text_rect.width(),
            text_rect.height()
        )

        padding = 10.0
        rect = QtCore.QRectF(
            text_rect.center().x() - (text_rect.width() / 2) - (padding / 2),
            text_rect.center().y() - (text_rect.width() / 2) - (padding / 2),
            text_rect.width() + padding,
            text_rect.width() + padding
        )

        # draw port lines.
        pen_color = QtGui.QColor(*self.border_color)
        pen_color.setAlpha(120)
        pen = QtGui.QPen(pen_color, 1.5)
        pen.setCapStyle(QtCore.Qt.RoundCap)
        painter.setPen(pen)
        painter.setBrush(QtCore.Qt.NoBrush)
        for p in self.inputs:
            if p.isVisible():
                p_text = self.get_input_text_item(p)
                if p_text.isVisible():
                    pt_width = p_text.boundingRect().width() * 1.2
                else:
                    pt_width = p.boundingRect().width() / 4
                pt1 = QtCore.QPointF(
                    p.pos().x() + (p.boundingRect().width() / 2) + pt_width,
                    p.pos().y() + (p.boundingRect().height() / 2)
                )
                path = QtGui.QPainterPath()
                path.moveTo(pt1)
                path.lineTo(QtCore.QPointF(pt1.x() + 4.0, pt1.y()))
                path.lineTo(rect.center())
                painter.drawPath(path)

        for p in self.outputs:
            if p.isVisible():
                p_text = self.get_output_text_item(p)
                if p_text.isVisible():
                    pt_width = p_text.boundingRect().width() * 1.2
                else:
                    pt_width = p.boundingRect().width() / 4
                pt1 = QtCore.QPointF(
                    p.pos().x() + (p.boundingRect().width() / 2) - pt_width,
                    p.pos().y() + (p.boundingRect().height() / 2)
                )
                path = QtGui.QPainterPath()
                path.moveTo(pt1)
                path.lineTo(QtCore.QPointF(pt1.x() - 2.0, pt1.y()))
                path.lineTo(rect.center())
                painter.drawPath(path)

        # draw the base color.
        painter.setBrush(QtGui.QColor(*self.color))
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawEllipse(rect)

        # draw outline.
        if self.selected:
            # light overlay on background when selected.
            painter.setBrush(QtGui.QColor(*NodeEnum.SELECTED_COLOR.value))
            painter.drawEllipse(rect)

            border_width = 1.2
            border_color = QtGui.QColor(
                *NodeEnum.SELECTED_BORDER_COLOR.value
            )
        else:
            border_width = 0.8
            border_color = QtGui.QColor(*self.border_color)

        # draw the outlines.
        painter.setBrush(QtCore.Qt.NoBrush)
        painter.setPen(QtGui.QPen(border_color, border_width))
        painter.drawEllipse(rect)

        # node name background.
        text_rect = self._text_item.boundingRect()
        text_rect = QtCore.QRectF(
            rect.center().x() - (text_rect.width() / 2),
            rect.center().y() - (text_rect.height() / 2),
            text_rect.width(),
            text_rect.height()
        )
        if self.selected:
            painter.setBrush(QtGui.QColor(*NodeEnum.SELECTED_COLOR.value))
        else:
            painter.setBrush(QtGui.QColor(0, 0, 0, 80))
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawRoundedRect(text_rect, 8.0, 8.0)

        painter.restore()

    def _paint_vertical(self, painter, option, widget):
        painter.save()
        rect = self.boundingRect()
        width = min(rect.width(), rect.height()) / 1.8
        rect = QtCore.QRectF(
            rect.center().x() - (width / 2),
            rect.center().y() - (width / 2),
            width, width
        )

        # draw port lines.
        pen_color = QtGui.QColor(*self.border_color)
        pen_color.setAlpha(120)
        pen = QtGui.QPen(pen_color, 1.5)
        pen.setCapStyle(QtCore.Qt.RoundCap)
        painter.setPen(pen)
        painter.setBrush(QtCore.Qt.NoBrush)
        for p in self.inputs:
            if p.isVisible():
                pt1 = QtCore.QPointF(
                    p.pos().x() + (p.boundingRect().width() / 2),
                    p.pos().y() + (p.boundingRect().height() / 2)
                )
                path = QtGui.QPainterPath()
                path.moveTo(pt1)
                path.moveTo(QtCore.QPointF(pt1.x(), pt1.y()))
                path.lineTo(rect.center())
                painter.drawPath(path)

        for p in self.outputs:
            if p.isVisible():
                pt1 = QtCore.QPointF(
                    p.pos().x() + (p.boundingRect().width() / 2),
                    p.pos().y() + (p.boundingRect().height() / 2)
                )
                path = QtGui.QPainterPath()
                path.moveTo(pt1)
                path.lineTo(QtCore.QPointF(pt1.x(), pt1.y()))
                path.lineTo(rect.center())
                painter.drawPath(path)

        # draw the base color.
        painter.setBrush(QtGui.QColor(*self.color))
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawEllipse(rect)

        # draw outline.
        if self.selected:
            # light overlay on background when selected.
            painter.setBrush(QtGui.QColor(*NodeEnum.SELECTED_COLOR.value))
            painter.drawEllipse(rect)

            border_width = 1.2
            border_color = QtGui.QColor(
                *NodeEnum.SELECTED_BORDER_COLOR.value
            )
        else:
            border_width = 0.8
            border_color = QtGui.QColor(*self.border_color)

        # draw the outlines.
        painter.setBrush(QtCore.Qt.NoBrush)
        painter.setPen(QtGui.QPen(border_color, border_width))
        painter.drawEllipse(rect)

        painter.restore()
        
    def _align_icon_horizontal(self, h_offset, v_offset):
        icon_rect = self._icon_item.boundingRect()
        x = self.boundingRect().center().x() - (icon_rect.width() / 2)
        y = self.boundingRect().top()
        self._icon_item.setPos(x + h_offset, y + v_offset)

    def _align_icon_vertical(self, h_offset, v_offset):
        rect = self.boundingRect()
        icon_rect = self._icon_item.boundingRect()
        x = rect.left() - icon_rect.width() + (rect.width() / 4)
        y = rect.center().y() - (icon_rect.height() / 2)
        self._icon_item.setPos(x + h_offset, y + v_offset)

    def _align_widgets_horizontal(self, v_offset):
        if not self._widgets:
            return
        rect = self.boundingRect()
        y = rect.bottom() + v_offset
        inputs = [p for p in self.inputs if p.isVisible()]
        outputs = [p for p in self.outputs if p.isVisible()]
        for widget in self._widgets.values():
            widget_rect = widget.boundingRect()
            if not inputs:
                x = rect.left() + 10
                widget.widget().setTitleAlign('left')
            elif not outputs:
                x = rect.right() - widget_rect.width() - 10
                widget.widget().setTitleAlign('right')
            else:
                x = rect.center().x() - (widget_rect.width() / 2)
                widget.widget().setTitleAlign('center')
            widget.setPos(x, y)
            y += widget_rect.height()

    def _align_widgets_vertical(self, v_offset):
        if not self._widgets:
            return
        rect = self.boundingRect()
        y = rect.center().y() + v_offset
        widget_height = 0.0
        for widget in self._widgets.values():
            widget_rect = widget.boundingRect()
            widget_height += widget_rect.height()
        y -= widget_height / 2

        for widget in self._widgets.values():
            widget_rect = widget.boundingRect()
            x = rect.center().x() - (widget_rect.width() / 2)
            widget.widget().setTitleAlign('center')
            widget.setPos(x, y)
            y += widget_rect.height()

    def _align_label_horizontal(self, h_offset, v_offset):
        rect = self.boundingRect()
        text_rect = self._text_item.boundingRect()
        x = rect.center().x() - (text_rect.width() / 2)
        y = rect.center().y() - (text_rect.height() / 2)
        self._text_item.setPos(x + h_offset, y + v_offset)

    def _align_label_vertical(self, h_offset, v_offset):
        rect = self.boundingRect()
        text_rect = self._text_item.boundingRect()
        x = rect.right() - (rect.width() / 3)
        y = rect.center().y() - (text_rect.height() / 2)
        self._text_item.setPos(x + h_offset, y + v_offset)

    def _draw_node_horizontal(self):
        add_width = self.text_item.boundingRect().width() * 1.5
        add_height = self.text_item.boundingRect().width() / 2

        # update port text items in visibility.
        for port, text in self._input_items.items():
            text.setVisible(port.display_name)
        for port, text in self._output_items.items():
            text.setVisible(port.display_name)

        # setup initial base size.
        self._set_base_size(add_w=add_width, add_h=add_height)
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
        self.align_ports(v_offset=add_height / 2)
        # arrange node widgets
        self.align_widgets(v_offset=0.0)

        self.update()

    def _draw_node_vertical(self):
        # hide the port text items in vertical layout.
        for port, text in self._input_items.items():
            text.setVisible(False)
        for port, text in self._output_items.items():
            text.setVisible(False)

        # setup initial base size.
        self._set_base_size(add_w=50, add_h=50)
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
        self.align_widgets(v_offset=0.0)

        self.update()
