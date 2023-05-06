#!/usr/bin/python
import math

from Qt import QtCore, QtGui, QtWidgets

from NodeGraphQt.constants import (
    LayoutDirectionEnum,
    PipeEnum,
    PipeLayoutEnum,
    PortTypeEnum,
    ITEM_CACHE_MODE,
    Z_VAL_PIPE,
    Z_VAL_NODE_WIDGET
)
from NodeGraphQt.qgraphics.port import PortItem

PIPE_STYLES = {
    PipeEnum.DRAW_TYPE_DEFAULT.value: QtCore.Qt.SolidLine,
    PipeEnum.DRAW_TYPE_DASHED.value: QtCore.Qt.DashLine,
    PipeEnum.DRAW_TYPE_DOTTED.value: QtCore.Qt.DotLine
}


class PipeItem(QtWidgets.QGraphicsPathItem):
    """
    Base Pipe item used for drawing node connections.
    """

    def __init__(self, input_port=None, output_port=None):
        super(PipeItem, self).__init__()
        self.setZValue(Z_VAL_PIPE)
        self.setAcceptHoverEvents(True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable)
        self._color = PipeEnum.COLOR.value
        self._style = PipeEnum.DRAW_TYPE_DEFAULT.value
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

        # only draw if a port or node is visible.
        is_visible = all([
            self._input_port.isVisible(),
            self._output_port.isVisible(),
            self._input_port.node.isVisible(),
            self._output_port.node.isVisible()
        ])
        if not is_visible:
            painter.save()
            painter.setBrush(QtCore.Qt.NoBrush)
            painter.setPen(QtCore.Qt.NoPen)
            painter.restore()
            return

        color = QtGui.QColor(*self._color)
        pen_style = PIPE_STYLES.get(self.style)
        pen_width = PipeEnum.WIDTH.value
        if self._active:
            color = QtGui.QColor(*PipeEnum.ACTIVE_COLOR.value)
            if pen_style == QtCore.Qt.DashDotDotLine:
                pen_width += 1
            else:
                pen_width += 0.35
        elif self._highlight:
            color = QtGui.QColor(*PipeEnum.HIGHLIGHT_COLOR.value)
            pen_style = PIPE_STYLES.get(PipeEnum.DRAW_TYPE_DEFAULT.value)

        if self.disabled():
            if not self._active:
                color = QtGui.QColor(*PipeEnum.DISABLED_COLOR.value)
            pen_width += 0.2
            pen_style = PIPE_STYLES.get(PipeEnum.DRAW_TYPE_DOTTED.value)

        pen = QtGui.QPen(color, pen_width, pen_style)
        pen.setCapStyle(QtCore.Qt.RoundCap)
        pen.setJoinStyle(QtCore.Qt.MiterJoin)

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

            pen = QtGui.QPen(color, pen_width)
            pen.setCapStyle(QtCore.Qt.RoundCap)
            pen.setJoinStyle(QtCore.Qt.MiterJoin)
            painter.setPen(pen)

            transform = QtGui.QTransform()
            transform.translate(cen_x, cen_y)
            radians = math.atan2(tgt_pt.y() - loc_pt.y(),
                                 tgt_pt.x() - loc_pt.x())
            degrees = math.degrees(radians) - 90
            transform.rotate(degrees)
            if dist < 1.0:
                transform.scale(dist, dist)
            painter.drawPolygon(transform.map(self._arrow))

        # QPaintDevice: Cannot destroy paint device that is being painted.
        painter.restore()

    def __draw_path_cycled_vertical(self, start_port, pos1, pos2, path):
        """
        Draw pipe vertically around node if connection is cyclic.

        Args:
            start_port (PortItem): port used to draw the starting point.
            pos1 (QPointF): start port position.
            pos2 (QPointF): end port position.
            path (QPainterPath): path to draw.
        """
        n_rect = start_port.node.boundingRect()
        ptype = start_port.port_type
        start_pos = pos1 if ptype == PortTypeEnum.IN.value else pos2
        end_pos = pos2 if ptype == PortTypeEnum.IN.value else pos1

        padding = 40
        top = start_pos.y() - padding
        bottom = end_pos.y() + padding
        path.moveTo(end_pos)
        path.lineTo(end_pos.x(), bottom)
        path.lineTo(end_pos.x() + n_rect.right(), bottom)
        path.lineTo(end_pos.x() + n_rect.right(), top)
        path.lineTo(start_pos.x(), top)
        path.lineTo(start_pos)
        self.setPath(path)

    def __draw_path_cycled_horizontal(self, start_port, pos1, pos2, path):
        """
        Draw pipe horizontally around node if connection is cyclic.

        Args:
            start_port (PortItem): port used to draw the starting point.
            pos1 (QPointF): start port position.
            pos2 (QPointF): end port position.
            path (QPainterPath): path to draw.
        """
        n_rect = start_port.node.boundingRect()
        ptype = start_port.port_type
        start_pos = pos1 if ptype == PortTypeEnum.IN.value else pos2
        end_pos = pos2 if ptype == PortTypeEnum.IN.value else pos1

        padding = 40
        left = end_pos.x() + padding
        right = start_pos.x() - padding
        path.moveTo(start_pos)
        path.lineTo(right, start_pos.y())
        path.lineTo(right, end_pos.y() + n_rect.bottom())
        path.lineTo(left, end_pos.y() + n_rect.bottom())
        path.lineTo(left, end_pos.y())
        path.lineTo(end_pos)
        self.setPath(path)

    def __draw_path_vertical(self, start_port, pos1, pos2, path):
        """
        Draws the vertical path between ports.

        Args:
            start_port (PortItem): port used to draw the starting point.
            pos1 (QPointF): start port position.
            pos2 (QPointF): end port position.
            path (QPainterPath): path to draw.
        """
        if self.viewer_pipe_layout() == PipeLayoutEnum.CURVED.value:
            ctr_offset_y1, ctr_offset_y2 = pos1.y(), pos2.y()
            tangent = abs(ctr_offset_y1 - ctr_offset_y2)

            max_height = start_port.node.boundingRect().height()
            tangent = min(tangent, max_height)
            if start_port.port_type == PortTypeEnum.IN.value:
                ctr_offset_y1 -= tangent
                ctr_offset_y2 += tangent
            else:
                ctr_offset_y1 += tangent
                ctr_offset_y2 -= tangent

            ctr_point1 = QtCore.QPointF(pos1.x(), ctr_offset_y1)
            ctr_point2 = QtCore.QPointF(pos2.x(), ctr_offset_y2)
            path.cubicTo(ctr_point1, ctr_point2, pos2)
            self.setPath(path)
        elif self.viewer_pipe_layout() == PipeLayoutEnum.ANGLE.value:
            ctr_offset_y1, ctr_offset_y2 = pos1.y(), pos2.y()
            distance = abs(ctr_offset_y1 - ctr_offset_y2)/2
            if start_port.port_type == PortTypeEnum.IN.value:
                ctr_offset_y1 -= distance
                ctr_offset_y2 += distance
            else:
                ctr_offset_y1 += distance
                ctr_offset_y2 -= distance

            ctr_point1 = QtCore.QPointF(pos1.x(), ctr_offset_y1)
            ctr_point2 = QtCore.QPointF(pos2.x(), ctr_offset_y2)
            path.lineTo(ctr_point1)
            path.lineTo(ctr_point2)
            path.lineTo(pos2)
            self.setPath(path)

    def __draw_path_horizontal(self, start_port, pos1, pos2, path):
        """
        Draws the horizontal path between ports.

        Args:
            start_port (PortItem): port used to draw the starting point.
            pos1 (QPointF): start port position.
            pos2 (QPointF): end port position.
            path (QPainterPath): path to draw.
        """
        if self.viewer_pipe_layout() == PipeLayoutEnum.CURVED.value:
            ctr_offset_x1, ctr_offset_x2 = pos1.x(), pos2.x()
            tangent = abs(ctr_offset_x1 - ctr_offset_x2)

            max_width = start_port.node.boundingRect().width()
            tangent = min(tangent, max_width)
            if start_port.port_type == PortTypeEnum.IN.value:
                ctr_offset_x1 -= tangent
                ctr_offset_x2 += tangent
            else:
                ctr_offset_x1 += tangent
                ctr_offset_x2 -= tangent

            ctr_point1 = QtCore.QPointF(ctr_offset_x1, pos1.y())
            ctr_point2 = QtCore.QPointF(ctr_offset_x2, pos2.y())
            path.cubicTo(ctr_point1, ctr_point2, pos2)
            self.setPath(path)
        elif self.viewer_pipe_layout() == PipeLayoutEnum.ANGLE.value:
            ctr_offset_x1, ctr_offset_x2 = pos1.x(), pos2.x()
            distance = abs(ctr_offset_x1 - ctr_offset_x2) / 2
            if start_port.port_type == PortTypeEnum.IN.value:
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

        direction = self.viewer_layout_direction()

        if end_port and not self.viewer().acyclic:
            if end_port.node == start_port.node:
                if direction is LayoutDirectionEnum.VERTICAL.value:
                    self.__draw_path_cycled_vertical(
                        start_port, pos1, pos2, path
                    )
                    return
                elif direction is LayoutDirectionEnum.HORIZONTAL.value:
                    self.__draw_path_cycled_horizontal(
                        start_port, pos1, pos2, path
                    )
                    return

        path.moveTo(line.x1(), line.y1())

        if self.viewer_pipe_layout() == PipeLayoutEnum.STRAIGHT.value:
            path.lineTo(pos2)
            self.setPath(path)
            return

        if direction is LayoutDirectionEnum.VERTICAL.value:
            self.__draw_path_vertical(start_port, pos1, pos2, path)
        elif direction is LayoutDirectionEnum.HORIZONTAL.value:
            self.__draw_path_horizontal(start_port, pos1, pos2, path)

    def reset_path(self):
        path = QtGui.QPainterPath(QtCore.QPointF(0.0, 0.0))
        self.setPath(path)

    @staticmethod
    def _calc_distance(p1, p2):
        x = math.pow((p2.x() - p1.x()), 2)
        y = math.pow((p2.y() - p1.y()), 2)
        return math.sqrt(x + y)

    def port_from_pos(self, pos, reverse=False):
        inport_pos = self.input_port.scenePos()
        outport_pos = self.output_port.scenePos()
        input_dist = self._calc_distance(inport_pos, pos)
        output_dist = self._calc_distance(outport_pos, pos)
        if input_dist < output_dist:
            port = self.output_port if reverse else self.input_port
        else:
            port = self.input_port if reverse else self.output_port
        return port

    def viewer(self):
        """
        Returns:
            NodeViewer: node graph viewer.
        """
        if self.scene():
            return self.scene().viewer()

    def viewer_pipe_layout(self):
        """
        Returns:
            int: pipe layout mode.
        """
        viewer = self.viewer()
        if viewer:
            return viewer.get_pipe_layout()

    def viewer_layout_direction(self):
        """
        Returns:
            int: graph layout mode.
        """
        viewer = self.viewer()
        if viewer:
            return viewer.get_layout_direction()

    def activate(self):
        self._active = True
        color = QtGui.QColor(*PipeEnum.ACTIVE_COLOR.value)
        pen = QtGui.QPen(
            color, 2.5, PIPE_STYLES.get(PipeEnum.DRAW_TYPE_DEFAULT.value)
        )
        self.setPen(pen)

    def active(self):
        return self._active

    def highlight(self):
        self._highlight = True
        color = QtGui.QColor(*PipeEnum.HIGHLIGHT_COLOR.value)
        pen = QtGui.QPen(
            color, 2, PIPE_STYLES.get(PipeEnum.DRAW_TYPE_DEFAULT.value)
        )
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
        self.input_port = ports[PortTypeEnum.IN.value]
        self.output_port = ports[PortTypeEnum.OUT.value]
        ports[PortTypeEnum.IN.value].add_pipe(self)
        ports[PortTypeEnum.OUT.value].add_pipe(self)

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
        return super(PipeItem, self).itemChange(change, value)

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


class LivePipeItem(PipeItem):
    """
    Live Pipe item used for drawing the live connection with the cursor.
    """

    def __init__(self):
        super(LivePipeItem, self).__init__()
        self.setZValue(Z_VAL_NODE_WIDGET + 1)
        self.shift_selected = False

        color = QtGui.QColor(*PipeEnum.ACTIVE_COLOR.value)
        pen = QtGui.QPen(color, PipeEnum.WIDTH.value + 0.35)
        pen.setJoinStyle(QtCore.Qt.MiterJoin)
        pen.setCapStyle(QtCore.Qt.RoundCap)

        self._idx_pointer = LivePipePolygonItem(self)
        self._idx_pointer.setPolygon(self._arrow)
        self._idx_pointer.setBrush(color.darker(300))
        self._idx_pointer.setPen(pen)

        color = QtGui.QColor(*PipeEnum.ACTIVE_COLOR.value)
        color.setAlpha(50)
        self._idx_text = QtWidgets.QGraphicsTextItem(self)
        self._idx_text.setDefaultTextColor(color)
        font = self._idx_text.font()
        font.setPointSize(7)
        self._idx_text.setFont(font)

    def paint(self, painter, option, widget):
        """
        Draws the connection line.

        Args:
            painter (QtGui.QPainter): painter used for drawing the item.
            option (QtGui.QStyleOptionGraphicsItem):
                used to describe the parameters needed to draw.
            widget (QtWidgets.QWidget): not used.
        """
        color = QtGui.QColor(*PipeEnum.ACTIVE_COLOR.value)
        pen_style = PIPE_STYLES.get(PipeEnum.DRAW_TYPE_DASHED.value)
        pen_width = PipeEnum.WIDTH.value + 0.35

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

        # draw middle circle
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

        painter.restore()

    def draw_path(self, start_port, end_port=None, cursor_pos=None,
                  color_mode=None):
        """
        re-implemented to also update the index pointer arrow position.

        Args:
            start_port (PortItem): port used to draw the starting point.
            end_port (PortItem): port used to draw the end point.
            cursor_pos (QtCore.QPointF): cursor position if specified this
                will be the draw end point.
            color_mode (str): arrow index pointer color mode
                              ('accept', 'reject' or None).
        """
        super(LivePipeItem, self).draw_path(start_port, end_port, cursor_pos)
        self.draw_index_pointer(start_port, cursor_pos, color_mode)

    def draw_index_pointer(self, start_port, cursor_pos, color_mode=None):
        """
        Update the index pointer arrow position and direction when the
        live pipe path is redrawn.

        Args:
            start_port (PortItem): start port item.
            cursor_pos (QtCore.QPoint): cursor scene position.
            color_mode (str): arrow index pointer color mode
                              ('accept', 'reject' or None).
        """
        text_rect = self._idx_text.boundingRect()

        transform = QtGui.QTransform()
        transform.translate(cursor_pos.x(), cursor_pos.y())
        if self.viewer_layout_direction() is LayoutDirectionEnum.VERTICAL.value:
            text_pos = (
                cursor_pos.x() + (text_rect.width() / 2.5),
                cursor_pos.y() - (text_rect.height() / 2)
            )
            if start_port.port_type == PortTypeEnum.OUT.value:
                transform.rotate(180)
        elif self.viewer_layout_direction() is LayoutDirectionEnum.HORIZONTAL.value:
            text_pos = (
                cursor_pos.x() - (text_rect.width() / 2),
                cursor_pos.y() - (text_rect.height() * 1.25)
            )
            if start_port.port_type == PortTypeEnum.IN.value:
                transform.rotate(-90)
            else:
                transform.rotate(90)
        self._idx_text.setPos(*text_pos)
        self._idx_text.setPlainText('{}'.format(start_port.name))

        self._idx_pointer.setPolygon(transform.map(self._arrow))

        if color_mode == 'accept':
            color = QtGui.QColor(*PipeEnum.HIGHLIGHT_COLOR.value)
        elif color_mode == 'reject':
            color = QtGui.QColor(*PipeEnum.DISABLED_COLOR.value)
        else:
            color = QtGui.QColor(*PipeEnum.ACTIVE_COLOR.value)

        pen = self._idx_pointer.pen()
        pen.setColor(color)
        self._idx_pointer.setBrush(color.darker(300))
        self._idx_pointer.setPen(pen)


class LivePipePolygonItem(QtWidgets.QGraphicsPolygonItem):
    """
    Custom live pipe polygon shape.
    """

    def __init__(self, parent):
        super(LivePipePolygonItem, self).__init__(parent)
        self.setFlag(self.ItemIsSelectable, True)

    def paint(self, painter, option, widget):
        """
        Args:
            painter (QtGui.QPainter): painter used for drawing the item.
            option (QtGui.QStyleOptionGraphicsItem):
                used to describe the parameters needed to draw.
            widget (QtWidgets.QWidget): not used.
        """
        painter.save()
        painter.setBrush(self.brush())
        painter.setPen(self.pen())
        painter.drawPolygon(self.polygon())
        painter.restore()
