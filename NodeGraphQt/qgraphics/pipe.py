#!/usr/bin/python
import math

from .. import QtCore, QtGui, QtWidgets
from ..constants import (
    PIPE_DEFAULT_COLOR, PIPE_ACTIVE_COLOR,
    PIPE_HIGHLIGHT_COLOR, PIPE_DISABLED_COLOR,
    PIPE_STYLE_DASHED, PIPE_STYLE_DEFAULT, PIPE_STYLE_DOTTED,
    PIPE_LAYOUT_STRAIGHT, PIPE_WIDTH, IN_PORT, OUT_PORT, Z_VAL_PIPE,
    Z_VAL_NODE_WIDGET,
    PIPE_LAYOUT_ANGLE, PIPE_LAYOUT_CURVED,
    ITEM_CACHE_MODE)
from .port import PortItem

PIPE_STYLES = {
    PIPE_STYLE_DEFAULT: QtCore.Qt.SolidLine,
    PIPE_STYLE_DASHED: QtCore.Qt.DashLine,
    PIPE_STYLE_DOTTED: QtCore.Qt.DotLine
}


class Pipe(QtWidgets.QGraphicsPathItem):
    """
    Base Pipe item used for drawing node connections.
    """

    def __init__(self, input_port=None, output_port=None):
        super(Pipe, self).__init__()
        self.setZValue(Z_VAL_PIPE)
        self.setAcceptHoverEvents(True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable)
        self._color = PIPE_DEFAULT_COLOR
        self._style = PIPE_STYLE_DEFAULT
        self._active = False
        self._highlight = False
        self._input_port = input_port
        self._output_port = output_port
        size = 6.0
        self._arrow = QtGui.QPolygonF()
        self._arrow.append(QtCore.QPointF(-size, size))
        self._arrow.append(QtCore.QPointF(0.0, -size * 1.5))
        self._arrow.append(QtCore.QPointF(size, size))
        self.setCacheMode(ITEM_CACHE_MODE)

    def __repr__(self):
        in_name = self._input_port.name if self._input_port else ''
        out_name = self._output_port.name if self._output_port else ''
        return '{}.Pipe(\'{}\', \'{}\')'.format(
            self.__module__, in_name, out_name)

    def hoverEnterEvent(self, event):
        self.activate()

    def hoverLeaveEvent(self, event):
        self.reset()
        if self.input_port and self.output_port:
            if self.input_port.node.selected:
                self.highlight()
            elif self.output_port.node.selected:
                self.highlight()
        if self.isSelected():
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
            if pen_style == QtCore.Qt.DashDotDotLine:
                pen_width += 1
            else:
                pen_width += 0.35
        elif self._highlight:
            color = QtGui.QColor(*PIPE_HIGHLIGHT_COLOR)
            pen_style = PIPE_STYLES.get(PIPE_STYLE_DEFAULT)

        if self.disabled():
            if not self._active:
                color = QtGui.QColor(*PIPE_DISABLED_COLOR)
            pen_width += 0.2
            pen_style = PIPE_STYLES.get(PIPE_STYLE_DOTTED)

        pen = QtGui.QPen(color, pen_width)
        pen.setStyle(pen_style)
        pen.setCapStyle(QtCore.Qt.RoundCap)

        painter.save()
        painter.setPen(pen)
        painter.setRenderHint(painter.Antialiasing, True)
        painter.drawPath(self.path())

        # draw arrow
        if self.input_port and self.output_port:
            cen_x = self.path().pointAtPercent(0.5).x()
            cen_y = self.path().pointAtPercent(0.5).y()
            loc_pt = self.path().pointAtPercent(0.49)
            tgt_pt = self.path().pointAtPercent(0.51)

            dist = math.hypot(tgt_pt.x() - cen_x, tgt_pt.y() - cen_y)
            if dist < 0.5:
                painter.restore()
                return

            color.setAlpha(255)
            if self._highlight:
                painter.setBrush(QtGui.QBrush(color.lighter(150)))
            elif self._active or self.disabled():
                painter.setBrush(QtGui.QBrush(color.darker(200)))
            else:
                painter.setBrush(QtGui.QBrush(color.darker(130)))

            pen_width = 0.6
            if dist < 1.0:
                pen_width *= (1.0 + dist)
            painter.setPen(QtGui.QPen(color, pen_width))

            transform = QtGui.QTransform()
            transform.translate(cen_x, cen_y)
            radians = math.atan2(tgt_pt.y() - loc_pt.y(),
                                 tgt_pt.x() - loc_pt.x())
            degrees = math.degrees(radians) - 90
            transform.rotate(degrees)
            if dist < 1.0:
                transform.scale(dist, dist)
            painter.drawPolygon(transform.map(self._arrow))

        painter.restore()  # QPaintDevice: Cannot destroy paint device that is being painted

    def draw_path(self, start_port, end_port=None, cursor_pos=None):
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
        pos1 = start_port.scenePos()
        pos1.setX(pos1.x() + (start_port.boundingRect().width() / 2))
        pos1.setY(pos1.y() + (start_port.boundingRect().height() / 2))
        if cursor_pos:
            pos2 = cursor_pos
        elif end_port:
            pos2 = end_port.scenePos()
            pos2.setX(pos2.x() + (start_port.boundingRect().width() / 2))
            pos2.setY(pos2.y() + (start_port.boundingRect().height() / 2))
        else:
            return

        line = QtCore.QLineF(pos1, pos2)
        path = QtGui.QPainterPath()
        path.moveTo(line.x1(), line.y1())

        if self.viewer_pipe_layout() == PIPE_LAYOUT_STRAIGHT:
            path.lineTo(pos2)
            self.setPath(path)
            return
        elif self.viewer_pipe_layout() == PIPE_LAYOUT_CURVED:
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
        elif self.viewer_pipe_layout() == PIPE_LAYOUT_ANGLE:
            ctr_offset_x1, ctr_offset_x2 = pos1.x(), pos2.x()
            distance = ctr_offset_x1 - ctr_offset_x2
            distance = (distance * -1) if distance < 0 else distance
            distance /= 2
            if start_port.port_type == IN_PORT:
                ctr_offset_x1 -= distance
                ctr_offset_x2 += distance
            else:
                ctr_offset_x1 += distance
                ctr_offset_x2 -= distance

            ctr_point1 = QtCore.QPointF(ctr_offset_x1, pos1.y())
            ctr_point2 = QtCore.QPointF(ctr_offset_x2, pos2.y())
            path.lineTo(ctr_point1)
            path.lineTo(ctr_point2)
            path.lineTo(pos2)
            self.setPath(path)

    def reset_path(self):
        path = QtGui.QPainterPath(QtCore.QPointF(0.0, 0.0))
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

    def viewer_pipe_layout(self):
        if self.scene():
            viewer = self.scene().viewer()
            return viewer.get_pipe_layout()

    def activate(self):
        self._active = True
        color = QtGui.QColor(*PIPE_ACTIVE_COLOR)
        pen = QtGui.QPen(color, 2.5, PIPE_STYLES.get(PIPE_STYLE_DEFAULT))
        self.setPen(pen)

    def active(self):
        return self._active

    def highlight(self):
        self._highlight = True
        color = QtGui.QColor(*PIPE_HIGHLIGHT_COLOR)
        pen = QtGui.QPen(color, 2, PIPE_STYLES.get(PIPE_STYLE_DEFAULT))
        self.setPen(pen)

    def highlighted(self):
        return self._highlight


    def reset(self):
        self._active = False
        self._highlight = False
        color = QtGui.QColor(*self.color)
        pen = QtGui.QPen(color, 2, PIPE_STYLES.get(self.style))
        self.setPen(pen)

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

    def itemChange(self, change, value):
        if change == self.ItemSelectedChange and self.scene():
            self.reset()
            if value:
                self.highlight()
        return super(Pipe, self).itemChange(change, value)

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


class LivePipe(Pipe):

    def __init__(self):
        super(LivePipe, self).__init__()
        self.setZValue(Z_VAL_NODE_WIDGET + 1)
        self.shift_selected = False

    def paint(self, painter, option, widget):
        """
        Draws the connection line.

        Args:
            painter (QtGui.QPainter): painter used for drawing the item.
            option (QtGui.QStyleOptionGraphicsItem):
                used to describe the parameters needed to draw.
            widget (QtWidgets.QWidget): not used.
        """
        color = QtGui.QColor(*PIPE_ACTIVE_COLOR)
        pen_style = PIPE_STYLES.get(PIPE_STYLE_DASHED)
        pen_width = PIPE_WIDTH + 0.35

        pen = QtGui.QPen(color, pen_width)
        pen.setStyle(pen_style)
        pen.setCapStyle(QtCore.Qt.RoundCap)

        painter.save()
        painter.setPen(pen)
        painter.setRenderHint(painter.Antialiasing, True)
        painter.drawPath(self.path())

        cen_x = self.path().pointAtPercent(0.5).x()
        cen_y = self.path().pointAtPercent(0.5).y()
        loc_pt = self.path().pointAtPercent(0.9)
        tgt_pt = self.path().pointAtPercent(1.0)

        dist = math.hypot(tgt_pt.x() - cen_x, tgt_pt.y() - cen_y)
        if dist < 0.05:
            painter.restore()
            return

        # draw circle
        size = 10.0
        if dist < 50.0:
            size *= (dist / 50.0)
        rect = QtCore.QRectF(cen_x-(size/2), cen_y-(size/2), size, size)
        painter.setBrush(color)
        painter.setPen(QtGui.QPen(color.darker(130), pen_width))
        painter.drawEllipse(rect)

        # draw arrow
        color.setAlpha(255)
        painter.setBrush(color.darker(200))

        pen_width = 0.6
        if dist < 1.0:
            pen_width *= 1.0 + dist
        painter.setPen(QtGui.QPen(color, pen_width))

        transform = QtGui.QTransform()
        transform.translate(tgt_pt.x(), tgt_pt.y())

        radians = math.atan2(tgt_pt.y() - loc_pt.y(),
                             tgt_pt.x() - loc_pt.x())
        degrees = math.degrees(radians) + 90
        transform.rotate(degrees)

        scale = 1.0
        if dist < 20.0:
            scale = dist / 20.0
        transform.scale(scale, scale)
        painter.drawPolygon(transform.map(self._arrow))
        painter.restore()
