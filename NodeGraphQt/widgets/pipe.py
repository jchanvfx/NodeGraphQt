#!/usr/bin/python
import math

from NodeGraphQt import QtCore, QtGui, QtWidgets
from NodeGraphQt.constants import (
    PIPE_DEFAULT_COLOR, PIPE_ACTIVE_COLOR, PIPE_HIGHLIGHT_COLOR,
    PIPE_STYLE_DASHED, PIPE_STYLE_DEFAULT, PIPE_STYLE_DOTTED,
    PIPE_LAYOUT_STRAIGHT, PIPE_WIDTH, IN_PORT, OUT_PORT, Z_VAL_PIPE
)
from NodeGraphQt.widgets.port import PortItem

PIPE_STYLES = {
    PIPE_STYLE_DEFAULT: QtCore.Qt.SolidLine,
    PIPE_STYLE_DASHED: QtCore.Qt.DashDotDotLine,
    PIPE_STYLE_DOTTED: QtCore.Qt.DotLine
}


class PipeArrow(QtWidgets.QGraphicsPolygonItem):
    """
    Base pipe arrow item for indicating pipe direction.
    """

    def __init__(self, parent=None, size=5.0):
        super(PipeArrow, self).__init__(parent)
        self.set_size(size)

    def set_size(self, size=5.0):
        triangle = QtGui.QPolygonF()
        triangle.append(QtCore.QPointF(-size, size))
        triangle.append(QtCore.QPointF(0.0, -size*2))
        triangle.append(QtCore.QPointF(size, size))
        self.setPolygon(triangle)


class Pipe(QtWidgets.QGraphicsPathItem):
    """
    Base Pipe item used for drawing node connections.
    """

    def __init__(self, input_port=None, output_port=None):
        super(Pipe, self).__init__()
        self.setZValue(Z_VAL_PIPE)
        self.setAcceptHoverEvents(True)
        self._color = PIPE_DEFAULT_COLOR
        self._style = PIPE_STYLE_DEFAULT
        self._active = False
        self._highlight = False
        self._input_port = input_port
        self._output_port = output_port
        self.__arrow = PipeArrow(self)
        self.reset()

    def __str__(self):
        in_name = self._input_port.name if self._input_port else ''
        out_name = self._output_port.name if self._output_port else ''
        return '{}.Pipe(\'{}\', \'{}\')'.format(
            self.__module__, in_name, out_name)

    def __repr__(self):
        in_name = self._input_port.name if self._input_port else ''
        out_name = self._output_port.name if self._output_port else ''
        return '{}.Pipe(\'{}\', \'{}\')'.format(
            self.__module__, in_name, out_name)

    def hoverEnterEvent(self, event):
        self.activate()

    def hoverLeaveEvent(self, event):
        self.reset()
        if self.input_port.node.selected:
            self.highlight()
        elif self.output_port.node.selected:
            self.highlight()

    def paint(self, painter, option, widget):
        """
        Draws the connection line between nodes.

        Args:
            painter (QtGui.QPainter): painter used for drawing the item.
            option (QtGui.QStyleOptionGraphicsItem):
                used to describe the parameters needed to draw.
            widget (QtWidgets.QWidget): not used.
        """
        color = QtGui.QColor(*self._color)
        pen_style = PIPE_STYLES.get(self.style)
        pen_width = PIPE_WIDTH
        if self._active:
            color = QtGui.QColor(*PIPE_ACTIVE_COLOR)
        elif self._highlight:
            color = QtGui.QColor(*PIPE_HIGHLIGHT_COLOR)
            pen_style = PIPE_STYLES.get(PIPE_STYLE_DEFAULT)

        if self.disabled():
            color.setAlpha(200)
            pen_width += 0.2
            pen_style = PIPE_STYLES.get(PIPE_STYLE_DOTTED)

        pen = QtGui.QPen(color, pen_width)
        pen.setStyle(pen_style)
        pen.setCapStyle(QtCore.Qt.RoundCap)

        painter.save()
        painter.setPen(pen)
        painter.setRenderHint(painter.Antialiasing, True)
        painter.drawPath(self.path())

        painter.restore()  # QPaintDevice: Cannot destroy paint device that is being painted

    def draw_path(self, start_port, end_port, cursor_pos=None):
        """
        Draws the path between ports.

        Args:
            start_port (PortItem): port used to draw the starting point.
            end_port (PortItem): port used to draw the end point.
            cursor_pos (QtCore.QPointF): cursor position if specified this
                will be the draw end point.
        """
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
        else:
            ctr_offset_x1 += tangent
            ctr_offset_x2 -= tangent

        ctr_point1 = QtCore.QPointF(ctr_offset_x1, pos1.y())
        ctr_point2 = QtCore.QPointF(ctr_offset_x2, pos2.y())
        path.cubicTo(ctr_point1, ctr_point2, pos2)
        self.setPath(path)

        # draw arrow
        if start_port.port_type == IN_PORT:
            loc_pt = self.path().pointAtPercent(0.49)
            tgt_pt = self.path().pointAtPercent(0.51)
        else:
            loc_pt = self.path().pointAtPercent(0.51)
            tgt_pt = self.path().pointAtPercent(0.49)

        radians = math.atan2(tgt_pt.y() - loc_pt.y(), tgt_pt.x() - loc_pt.x())
        degrees = math.degrees(radians) - 90
        self.__arrow.setPos(self.path().pointAtPercent(0.5))
        self.__arrow.setRotation(degrees)

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

    def viewer_pipe_layout(self):
        if self.scene():
            viewer = self.scene().viewer()
            return viewer.get_pipe_layout()

    def activate(self):
        self._active = True
        color = QtGui.QColor(*PIPE_ACTIVE_COLOR)
        pen = QtGui.QPen(color, 2, PIPE_STYLES.get(PIPE_STYLE_DEFAULT))
        self.setPen(pen)
        self.__arrow.setBrush(QtGui.QBrush(color.darker(200)))
        self.__arrow.setPen(QtGui.QPen(color, 0.8))

    def active(self):
        return self._active

    def highlight(self):
        self._highlight = True
        color = QtGui.QColor(*PIPE_HIGHLIGHT_COLOR)
        pen = QtGui.QPen(color, 2, PIPE_STYLES.get(PIPE_STYLE_DEFAULT))
        self.setPen(pen)
        self.__arrow.setBrush(QtGui.QBrush(color.darker(200)))
        self.__arrow.setPen(QtGui.QPen(color, 0.8))

    def highlighted(self):
        return self._highlight

    def reset(self):
        self._active = False
        self._highlight = False
        color = QtGui.QColor(*self.color)
        pen = QtGui.QPen(color, 2, PIPE_STYLES.get(self.style))
        self.setPen(pen)
        self.__arrow.setBrush(QtGui.QBrush(color.darker(130)))
        self.__arrow.setPen(QtGui.QPen(color, 0.6))

    def set_connections(self, port1, port2):
        ports = {
            port1.port_type: port1,
            port2.port_type: port2
        }
        self.input_port = ports[IN_PORT]
        self.output_port = ports[OUT_PORT]
        ports[IN_PORT].add_pipe(self)
        ports[OUT_PORT].add_pipe(self)

    def disabled(self):
        if self.input_port and self.input_port.node.disabled:
            return True
        if self.output_port and self.output_port.node.disabled:
            return True
        return False

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
        # TODO: not sure if we need this...?
        del self

