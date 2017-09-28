#!/usr/bin/python
import math

from PySide import QtGui, QtCore

from .constants import (
    PIPE_DEFAULT_COLOR, PIPE_ACTIVE_COLOR, PIPE_HIGHLIGHT_COLOR,
    PIPE_STYLE_DASHED, PIPE_STYLE_DEFAULT, PIPE_STYLE_DOTTED,
    PIPE_LAYOUT_STRAIGHT, IN_PORT, OUT_PORT, Z_VAL_PIPE
)
from .port import PortItem

PIPE_STYLES = {
    PIPE_STYLE_DEFAULT: QtCore.Qt.PenStyle.SolidLine,
    PIPE_STYLE_DASHED: QtCore.Qt.PenStyle.DashDotDotLine,
    PIPE_STYLE_DOTTED: QtCore.Qt.PenStyle.DotLine
}


class Pipe(QtGui.QGraphicsPathItem):
    """
    Base Pipe item.
    """

    def __init__(self, input_port=None, output_port=None):
        super(Pipe, self).__init__()
        self.setZValue(Z_VAL_PIPE)
        self._color = PIPE_DEFAULT_COLOR
        self._style = PIPE_STYLE_DEFAULT
        self._active = False
        self._highlight = False
        self._input_port = input_port
        self._output_port = output_port

    def __str__(self):
        input_name = self._input_port.name if self._input_port else 'None'
        input_node = self._input_port.node.name if self._input_port else 'None'
        output_name = self._output_port.name if self._output_port else 'None'
        output_node = self._output_port.node.name if self._output_port else 'None'
        return 'Pipe(in={}:{}, out={}:{})'.format(
            input_node, input_name, output_node, output_name
        )

    # pipe selection is done through the viewer.
    # def mousePressEvent(self, event):
    #     super(Pipe, self).mousePressEvent(event)
    #     self.viewer_start_connection(event.scenePos())

    def paint(self, painter, option, widget):
        color = self._color
        pen_style = PIPE_STYLES.get(self.style)
        pen_width = 2
        if self._active:
            color = PIPE_ACTIVE_COLOR
        elif self._highlight:
            color = PIPE_HIGHLIGHT_COLOR
            pen_style = PIPE_STYLES.get(PIPE_STYLE_DEFAULT)

        pen = QtGui.QPen(
            QtGui.QColor(color[0], color[1], color[2], color[3]), pen_width
        )
        pen.setStyle(pen_style)
        painter.setPen(pen)
        painter.setRenderHint(painter.Antialiasing, True)
        painter.drawPath(self.path())

    def draw_path(self, start_port, end_port, cursor_pos=None):
        if not start_port:
            return
        offset = (start_port.boundingRect().width() / 2)
        pos1 = start_port.scenePos()
        pos1.setX(pos1.x() + offset)
        pos1.setY(pos1.y() + offset)
        if cursor_pos:
            pos2 = cursor_pos
        elif end_port:
            offset = start_port.boundingRect().width() / 2
            pos2 = end_port.scenePos()
            pos2.setX(pos2.x() + offset)
            pos2.setY(pos2.y() + offset)
        else:
            return

        line = QtCore.QLineF(pos1, pos2)
        path = QtGui.QPainterPath()
        path.moveTo(line.x1(), line.y1())

        if self.viewer_pipe_layout() == PIPE_LAYOUT_STRAIGHT:
            path.lineTo(pos2)
            self.setPath(path)
            return

        ctr_offset_x1, ctr_offset_x2 = pos1.x(), pos2.x()
        tangent = ctr_offset_x1 - ctr_offset_x2
        tangent = (tangent * -1) if tangent < 0 else tangent

        max_width = start_port.node.boundingRect().width() / 2
        tangent = max_width if tangent > max_width else tangent

        if start_port.port_type == IN_PORT:
            ctr_offset_x1 -= tangent
            ctr_offset_x2 += tangent
        elif start_port.port_type == OUT_PORT:
            ctr_offset_x1 += tangent
            ctr_offset_x2 -= tangent

        ctr_point1 = QtCore.QPointF(ctr_offset_x1, pos1.y())
        ctr_point2 = QtCore.QPointF(ctr_offset_x2, pos2.y())
        path.cubicTo(ctr_point1, ctr_point2, pos2)
        self.setPath(path)

    def calc_distance(self, p1, p2):
        x = math.pow((p2.x() - p1.x()), 2)
        y = math.pow((p2.y() - p1.y()), 2)
        return math.sqrt(x + y)

    def port_from_pos(self, pos, reverse=False):
        inport_pos = self.input_port.scenePos()
        outport_pos = self.output_port.scenePos()
        input_dist = self.calc_distance(inport_pos, pos)
        output_dist = self.calc_distance(outport_pos, pos)
        if input_dist < output_dist:
            port = self.output_port if reverse else self.input_port
        else:
            port = self.input_port if reverse else self.output_port
        return port

    # disabled as pipe selection is done in the viewer.
    # def viewer_start_connection(self, pos):
    #     if not self.scene():
    #         return
    #     start_port = self.port_from_pos(pos, True)
    #     viewer = self.scene().viewer()
    #     viewer.start_connection(start_port)

    def viewer_pipe_layout(self):
        if self.scene():
            viewer = self.scene().viewer()
            return viewer.get_pipe_layout()

    def activate(self):
        self._active = True
        pen = QtGui.QPen(
            QtGui.QColor(
                PIPE_ACTIVE_COLOR[0], PIPE_ACTIVE_COLOR[1],
                PIPE_ACTIVE_COLOR[2], PIPE_ACTIVE_COLOR[3]), 2
        )
        pen.setStyle(PIPE_STYLES.get(PIPE_STYLE_DEFAULT))
        self.setPen(pen)

    def active(self):
        return self._active

    def highlight(self):
        self._highlight = True
        pen = QtGui.QPen(
            QtGui.QColor(
                PIPE_HIGHLIGHT_COLOR[0], PIPE_HIGHLIGHT_COLOR[1],
                PIPE_HIGHLIGHT_COLOR[2], PIPE_HIGHLIGHT_COLOR[3]), 2
        )
        pen.setStyle(PIPE_STYLES.get(PIPE_STYLE_DEFAULT))
        self.setPen(pen)

    def highlighted(self):
        return self._highlight

    def reset(self):
        self._active = False
        self._highlight = False
        pen = QtGui.QPen(
            QtGui.QColor(
                self.color[0], self.color[1], self.color[2], self.color[3]), 2
        )
        pen.setStyle(PIPE_STYLES.get(self.style))
        self.setPen(pen)

    @property
    def input_port(self):
        return self._input_port

    @input_port.setter
    def input_port(self, port):
        if isinstance(port, PortItem) or not port:
            self._input_port = port
        else:
            self._input_port = None

    @property
    def output_port(self):
        return self._output_port

    @output_port.setter
    def output_port(self, port):
        if isinstance(port, PortItem) or not port:
            self._output_port = port
        else:
            self._output_port = None

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, color):
        self._color = color

    @property
    def style(self):
        return self._style

    @style.setter
    def style(self, style):
        self._style = style

    def delete(self):
        if self.input_port and self.input_port.connected_pipes:
            self.input_port.remove_pipe(self)
        if self.output_port and self.output_port.connected_pipes:
            self.output_port.remove_pipe(self)
        if self.scene():
            self.scene().removeItem(self)
