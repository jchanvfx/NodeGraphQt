#!/usr/bin/python
# -*- coding: utf-8 -*-
import os

from NodeGraphQt import QtGui, QtCore, QtWidgets
from NodeGraphQt.constants import (IN_PORT, OUT_PORT,
                                   PIPE_LAYOUT_CURVED,
                                   PIPE_STYLE_DASHED,
                                   SCENE_AREA,
                                   Z_VAL_NODE_WIDGET)
from NodeGraphQt.qgraphics.node_abstract import AbstractNodeItem
from NodeGraphQt.qgraphics.node_backdrop import BackdropNodeItem
from NodeGraphQt.qgraphics.pipe import Pipe
from NodeGraphQt.qgraphics.port import PortItem
from NodeGraphQt.qgraphics.slicer import SlicerPipe
from NodeGraphQt.widgets.scene import NodeScene
from NodeGraphQt.widgets.stylesheet import STYLE_QMENU
from NodeGraphQt.widgets.tab_search import TabSearchWidget

ZOOM_MIN = -0.95
ZOOM_MAX = 2.0


class NodeViewer(QtWidgets.QGraphicsView):
    """
    node viewer is the widget used for displaying the scene and nodes

    functions in this class is used internally by the
    class:`NodeGraphQt.NodeGraph` class.
    """

    moved_nodes = QtCore.Signal(dict)
    search_triggered = QtCore.Signal(str, tuple)
    connection_sliced = QtCore.Signal(list)
    connection_changed = QtCore.Signal(list, list)

    # pass through signals
    node_selected = QtCore.Signal(str)
    node_double_clicked = QtCore.Signal(str)
    data_dropped = QtCore.Signal(QtCore.QMimeData, QtCore.QPoint)

    def __init__(self, parent=None):
        super(NodeViewer, self).__init__(parent)
        if parent is not None:
            self.setWindowFlags(QtCore.Qt.Window)

        scene_pos = (SCENE_AREA / 2) * -1
        self.setScene(NodeScene(self))
        self.setSceneRect(scene_pos, scene_pos, SCENE_AREA, SCENE_AREA)
        self.setRenderHint(QtGui.QPainter.Antialiasing, True)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setViewportUpdateMode(QtWidgets.QGraphicsView.FullViewportUpdate)
        self.setAcceptDrops(True)
        self.resize(1000, 800)

        self._pipe_layout = PIPE_LAYOUT_CURVED
        self._live_pipe = None
        self._detached_port = None
        self._start_port = None
        self._origin_pos = None
        self._previous_pos = QtCore.QPoint(self.width(), self.height())
        self._prev_selection = []
        self._node_positions = {}
        self._rubber_band = QtWidgets.QRubberBand(
            QtWidgets.QRubberBand.Rectangle, self
        )
        self._pipe_slicer = SlicerPipe()
        self._pipe_slicer.setVisible(False)
        self.scene().addItem(self._pipe_slicer)

        self._undo_stack = QtWidgets.QUndoStack(self)
        self._context_menu = QtWidgets.QMenu('main', self)
        self._context_menu.setStyleSheet(STYLE_QMENU)
        self._search_widget = TabSearchWidget(self)
        self._search_widget.search_submitted.connect(self._on_search_submitted)

        # workaround fix for shortcuts from the non-native menu actions
        # don't seem to trigger so we create a hidden menu bar.
        menu_bar = QtWidgets.QMenuBar(self)
        menu_bar.setNativeMenuBar(False)
        # shortcuts don't work with "setVisibility(False)".
        menu_bar.resize(0, 0)
        menu_bar.addMenu(self._context_menu)

        self.acyclic = True
        self.LMB_state = False
        self.RMB_state = False
        self.MMB_state = False

    def __repr__(self):
        return '{}.{}()'.format(
            self.__module__, self.__class__.__name__)

    # --- private ---

    def _set_viewer_zoom(self, value, sensitivity=0.0):
        if value == 0.0:
            return
        scale = (0.9 + sensitivity) if value < 0.0 else (1.1 - sensitivity)
        zoom = self.get_zoom()
        if ZOOM_MIN >= zoom:
            if scale == 0.9:
                return
        if ZOOM_MAX <= zoom:
            if scale == 1.1:
                return
        self.scale(scale, scale)

    def _set_viewer_pan(self, pos_x, pos_y):
        scroll_x = self.horizontalScrollBar()
        scroll_y = self.verticalScrollBar()
        scroll_x.setValue(scroll_x.value() - pos_x)
        scroll_y.setValue(scroll_y.value() - pos_y)

    def _combined_rect(self, nodes):
        group = self.scene().createItemGroup(nodes)
        rect = group.boundingRect()
        self.scene().destroyItemGroup(group)
        return rect

    def _items_near(self, pos, item_type=None, width=20, height=20):
        x, y = pos.x() - width, pos.y() - height
        rect = QtCore.QRectF(x, y, width, height)
        items = []
        for item in self.scene().items(rect):
            if not item_type or isinstance(item, item_type):
                items.append(item)
        return items

    def _on_search_submitted(self, node_type):
        pos = self.mapToScene(self._previous_pos)
        self.search_triggered.emit(node_type, (pos.x(), pos.y()))

    def _on_pipes_sliced(self, path):
        self.connection_sliced.emit([
            [i.input_port, i.output_port]
            for i in self.scene().items(path) if isinstance(i, Pipe)
        ])

    # --- reimplemented events ---

    def resizeEvent(self, event):
        super(NodeViewer, self).resizeEvent(event)

    def contextMenuEvent(self, event):
        self.RMB_state = False
        if self._context_menu.isEnabled():
            self._context_menu.exec_(event.globalPos())
        else:
            return super(NodeViewer, self).contextMenuEvent(event)

    def mousePressEvent(self, event):
        alt_modifier = event.modifiers() == QtCore.Qt.AltModifier
        shift_modifier = event.modifiers() == QtCore.Qt.ShiftModifier

        if event.button() == QtCore.Qt.LeftButton:
            self.LMB_state = True
        elif event.button() == QtCore.Qt.RightButton:
            self.RMB_state = True
        elif event.button() == QtCore.Qt.MiddleButton:
            self.MMB_state = True
        self._origin_pos = event.pos()
        self._previous_pos = event.pos()
        self._prev_selection = self.selected_nodes()

        # close tab search
        if self._search_widget.isVisible():
            self.tab_search_toggle()

        # cursor pos.
        map_pos = self.mapToScene(event.pos())

        # pipe slicer enabled.
        if event.modifiers() == (QtCore.Qt.AltModifier | QtCore.Qt.ShiftModifier):
            self._pipe_slicer.draw_path(map_pos, map_pos)
            self._pipe_slicer.setVisible(True)
            return

        if alt_modifier:
            return

        items = self._items_near(map_pos, None, 20, 20)
        nodes = [i for i in items if isinstance(i, AbstractNodeItem)]

        # toggle extend node selection.
        if shift_modifier:
            for node in nodes:
                node.selected = not node.selected

        # update the recorded node positions.
        self._node_positions.update(
            {n: n.xy_pos for n in self.selected_nodes()}
        )

        # show selection selection marquee
        if self.LMB_state and not items:
            rect = QtCore.QRect(self._previous_pos, QtCore.QSize())
            rect = rect.normalized()
            map_rect = self.mapToScene(rect).boundingRect()
            self.scene().update(map_rect)
            self._rubber_band.setGeometry(rect)
            self._rubber_band.show()

        if not shift_modifier:
            super(NodeViewer, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.LMB_state = False
        elif event.button() == QtCore.Qt.RightButton:
            self.RMB_state = False
        elif event.button() == QtCore.Qt.MiddleButton:
            self.MMB_state = False

        # hide pipe slicer.
        if self._pipe_slicer.isVisible():
            self._on_pipes_sliced(self._pipe_slicer.path())
            p = QtCore.QPointF(0.0, 0.0)
            self._pipe_slicer.draw_path(p, p)
            self._pipe_slicer.setVisible(False)

        # hide selection marquee
        if self._rubber_band.isVisible():
            rect = self._rubber_band.rect()
            map_rect = self.mapToScene(rect).boundingRect()
            self._rubber_band.hide()
            self.scene().update(map_rect)

        # find position changed nodes and emit signal.
        moved_nodes = {
            n: xy_pos for n, xy_pos in self._node_positions.items()
            if n.xy_pos != xy_pos
        }
        if moved_nodes:
            self.moved_nodes.emit(moved_nodes)

        # reset recorded positions.
        self._node_positions = {}

        super(NodeViewer, self).mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        alt_modifier = event.modifiers() == QtCore.Qt.AltModifier
        shift_modifier = event.modifiers() == QtCore.Qt.ShiftModifier
        if event.modifiers() == (QtCore.Qt.AltModifier | QtCore.Qt.ShiftModifier):
            if self.LMB_state:
                p1 = self._pipe_slicer.path().pointAtPercent(0)
                p2 = self.mapToScene(self._previous_pos)
                self._pipe_slicer.draw_path(p1, p2)
                self._previous_pos = event.pos()
                super(NodeViewer, self).mouseMoveEvent(event)
                return

        if self.MMB_state and alt_modifier:
            pos_x = (event.x() - self._previous_pos.x())
            zoom = 0.1 if pos_x > 0 else -0.1
            self._set_viewer_zoom(zoom, 0.05)
        elif self.MMB_state or (self.LMB_state and alt_modifier):
            pos_x = (event.x() - self._previous_pos.x())
            pos_y = (event.y() - self._previous_pos.y())
            self._set_viewer_pan(pos_x, pos_y)

        if self.LMB_state and self._rubber_band.isVisible():
            rect = QtCore.QRect(self._origin_pos, event.pos()).normalized()
            map_rect = self.mapToScene(rect).boundingRect()
            path = QtGui.QPainterPath()
            path.addRect(map_rect)
            self._rubber_band.setGeometry(rect)
            self.scene().setSelectionArea(path, QtCore.Qt.IntersectsItemShape)
            self.scene().update(map_rect)

            if shift_modifier and self._prev_selection:
                for node in self._prev_selection:
                    if node not in self.selected_nodes():
                        node.selected = True

        self._previous_pos = event.pos()
        super(NodeViewer, self).mouseMoveEvent(event)

    def wheelEvent(self, event):
        try:
            delta = event.delta()
        except AttributeError:
            # For PyQt5
            delta = event.angleDelta().y()

        adjust = (delta / 120) * 0.1
        self._set_viewer_zoom(adjust)

    def dropEvent(self, event):
        pos = self.mapToScene(event.pos())
        event.setDropAction(QtCore.Qt.MoveAction)
        self.data_dropped.emit(
            event.mimeData(), QtCore.QPoint(pos.x(), pos.y()))

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat('text/plain'):
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat('text/plain'):
            event.accept()
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        event.ignore()

    # --- scene events ---

    def sceneMouseMoveEvent(self, event):
        """
        triggered mouse move event for the scene.
         - redraw the connection pipe.

        Args:
            event (QtWidgets.QGraphicsSceneMouseEvent):
                The event handler from the QtWidgets.QGraphicsScene
        """
        if not self._live_pipe:
            return
        if not self._start_port:
            return

        pos = event.scenePos()
        items = self.scene().items(pos)
        if items and isinstance(items[0], PortItem):
            x = items[0].boundingRect().width() / 2
            y = items[0].boundingRect().height() / 2
            pos = items[0].scenePos()
            pos.setX(pos.x() + x)
            pos.setY(pos.y() + y)

        self._live_pipe.draw_path(self._start_port, None, pos)

    def sceneMousePressEvent(self, event):
        """
        triggered mouse press event for the scene (takes priority over viewer event).
         - detect selected pipe and start connection.
         - remap Shift and Ctrl modifier.

        Args:
            event (QtWidgets.QGraphicsScenePressEvent):
                The event handler from the QtWidgets.QGraphicsScene
        """
        # pipe slicer enabled.
        if event.modifiers() == (QtCore.Qt.AltModifier | QtCore.Qt.ShiftModifier):
            return
        # viewer pan mode.
        if event.modifiers() == QtCore.Qt.AltModifier:
            return

        pos = event.scenePos()
        port_items = self._items_near(pos, PortItem, 5, 5)
        if port_items:
            port = port_items[0]
            if not port.multi_connection and port.connected_ports:
                self._detached_port = port.connected_ports[0]
            self.start_live_connection(port)
            if not port.multi_connection:
                [p.delete() for p in port.connected_pipes]
            return

        node_items = self._items_near(pos, AbstractNodeItem, 3, 3)
        if node_items:
            node = node_items[0]

            # record the node positions at selection time.
            for n in node_items:
                self._node_positions[n] = n.xy_pos

            # emit selected node id with LMB.
            if event.button() == QtCore.Qt.LeftButton:
                self.node_selected.emit(node.id)

            if not isinstance(node, BackdropNodeItem):
                return

        pipe_items = self._items_near(pos, Pipe, 3, 3)
        if pipe_items:
            if not self.LMB_state:
                return
            pipe = pipe_items[0]
            attr = {IN_PORT: 'output_port', OUT_PORT: 'input_port'}
            from_port = pipe.port_from_pos(pos, True)
            from_port._hovered = True

            self._detached_port = getattr(pipe, attr[from_port.port_type])
            self.start_live_connection(from_port)
            self._live_pipe.draw_path(self._start_port, None, pos)
            pipe.delete()

    def sceneMouseReleaseEvent(self, event):
        """
        triggered mouse release event for the scene.
         - verify to make a the connection Pipe.

        Args:
            event (QtWidgets.QGraphicsSceneMouseEvent):
                The event handler from the QtWidgets.QGraphicsScene
        """
        if not self._live_pipe:
            return

        self._start_port._hovered = False

        # find the end port.
        end_port = None
        for item in self.scene().items(event.scenePos()):
            if isinstance(item, PortItem):
                end_port = item
                break

        connected = []
        disconnected = []

        # if port disconnected from existing pipe.
        if end_port is None:
            if self._detached_port:
                disconnected.append((self._start_port, self._detached_port))
                self.connection_changed.emit(disconnected, connected)

            self._detached_port = None
            self.end_live_connection()
            return

        # restore connection check.
        restore_connection = any([
            # if same port type.
            end_port.port_type == self._start_port.port_type,
            # if connection to itself.
            end_port.node == self._start_port.node,
            # if end port is the start port.
            end_port == self._start_port,
            # if detached port is the end port.
            self._detached_port == end_port
        ])
        if restore_connection:
            if self._detached_port:
                to_port = self._detached_port or end_port
                self.establish_connection(self._start_port, to_port)
                self._detached_port = None
            self.end_live_connection()
            return

        # register as disconnected if not acyclic.
        if self.acyclic and not self.acyclic_check(self._start_port, end_port):
            if self._detached_port:
                disconnected.append((self._start_port, self._detached_port))

            self.connection_changed.emit(disconnected, connected)

            self._detached_port = None
            self.end_live_connection()
            return

        # make connection.
        if not end_port.multi_connection and end_port.connected_ports:
            dettached_end = end_port.connected_ports[0]
            disconnected.append((end_port, dettached_end))

        if self._detached_port:
            disconnected.append((self._start_port, self._detached_port))

        connected.append((self._start_port, end_port))

        self.connection_changed.emit(disconnected, connected)

        self._detached_port = None
        self.end_live_connection()

    # --- port connections ---

    def start_live_connection(self, selected_port):
        """
        create new pipe for the connection.
        (draws the live pipe from the port following the cursor position)
        """
        if not selected_port:
            return
        self._start_port = selected_port
        self._live_pipe = Pipe()
        self._live_pipe.setZValue(Z_VAL_NODE_WIDGET)
        self._live_pipe.activate()
        self._live_pipe.style = PIPE_STYLE_DASHED
        if self._start_port.type == IN_PORT:
            self._live_pipe.input_port = self._start_port
        elif self._start_port == OUT_PORT:
            self._live_pipe.output_port = self._start_port
        self.scene().addItem(self._live_pipe)

    def end_live_connection(self):
        """
        delete live connection pipe and reset start port.
        (removes the pipe item used for drawing the live connection)
        """
        if self._live_pipe:
            self._live_pipe.delete()
            self._live_pipe = None
        self._start_port = None

    def establish_connection(self, start_port, end_port):
        """
        establish a new pipe connection.
        (adds a new pipe item to draw between 2 ports)
        """
        pipe = Pipe()
        self.scene().addItem(pipe)
        pipe.set_connections(start_port, end_port)
        pipe.draw_path(pipe.input_port, pipe.output_port)
        if start_port.node.selected or end_port.node.selected:
            pipe.highlight()

    def acyclic_check(self, start_port, end_port):
        """
        validate the connection so it doesn't loop itself.

        Returns:
            bool: True if port connection is valid.
        """
        start_node = start_port.node
        check_nodes = [end_port.node]
        io_types = {IN_PORT: 'outputs', OUT_PORT: 'inputs'}
        while check_nodes:
            check_node = check_nodes.pop(0)
            for check_port in getattr(check_node, io_types[end_port.port_type]):
                if check_port.connected_ports:
                    for port in check_port.connected_ports:
                        if port.node != start_node:
                            check_nodes.append(port.node)
                        else:
                            return False
        return True

    # --- viewer ---

    def tab_search_set_nodes(self, nodes):
        self._search_widget.set_nodes(nodes)

    def tab_search_toggle(self):
        pos = self._previous_pos
        state = not self._search_widget.isVisible()
        if state:
            rect = self._search_widget.rect()
            new_pos = QtCore.QPoint(pos.x() - rect.width() / 2,
                                    pos.y() - rect.height() / 2)
            self._search_widget.move(new_pos)
            self._search_widget.setVisible(state)
            rect = self.mapToScene(rect).boundingRect()
            self.scene().update(rect)
        else:
            self._search_widget.setVisible(state)
            self.clearFocus()

    def context_menu(self):
        return self._context_menu

    def question_dialog(self, text, title='Node Graph'):
        dlg = QtWidgets.QMessageBox.question(
            self, title, text,
            QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
        return dlg == QtWidgets.QMessageBox.Yes

    def message_dialog(self, text, title='Node Graph'):
        QtWidgets.QMessageBox.information(
            self, title, text, QtWidgets.QMessageBox.Ok)

    def load_dialog(self, current_dir=None, ext=None):
        current_dir = current_dir or os.path.expanduser('~')
        ext = '*{} '.format(ext) if ext else ''
        ext_filter = ';;'.join([
            'Node Graph ({}*json)'.format(ext), 'All Files (*)'
        ])
        file_dlg = QtWidgets.QFileDialog.getOpenFileName(
            self, 'Open Session Setup', current_dir, ext_filter)
        return file_dlg[0] or None

    def save_dialog(self, current_dir=None, ext=None):
        current_dir = current_dir or os.path.expanduser('~')
        ext_label = '*{} '.format(ext) if ext else ''
        ext_type = '.{}'.format(ext) if ext else '.json'
        ext_map = {'Node Graph ({}*json)'.format(ext_label): ext_type,
                   'All Files (*)': ''}
        file_dlg = QtWidgets.QFileDialog.getSaveFileName(
            self, 'Save Session', current_dir, ';;'.join(ext_map.keys()))
        file_path = file_dlg[0]
        if not file_path:
            return
        ext = ext_map[file_dlg[1]]
        if ext and not file_path.endswith(ext):
            file_path += ext
        return file_path

    def all_pipes(self):
        pipes = []
        for item in self.scene().items():
            if isinstance(item, Pipe):
                pipes.append(item)
        return pipes

    def all_nodes(self):
        nodes = []
        for item in self.scene().items():
            if isinstance(item, AbstractNodeItem):
                nodes.append(item)
        return nodes

    def selected_nodes(self):
        nodes = []
        for item in self.scene().selectedItems():
            if isinstance(item, AbstractNodeItem):
                nodes.append(item)
        return nodes

    def add_node(self, node, pos=None):
        pos = pos or (self._previous_pos.x(), self._previous_pos.y())
        node.pre_init(self, pos)
        self.scene().addItem(node)
        node.post_init(self, pos)

    def remove_node(self, node):
        if isinstance(node, AbstractNodeItem):
            node.delete()

    def move_nodes(self, nodes, pos=None, offset=None):
        group = self.scene().createItemGroup(nodes)
        group_rect = group.boundingRect()
        if pos:
            x, y = pos
        else:
            pos = self.mapToScene(self._previous_pos)
            x = pos.x() - group_rect.center().x()
            y = pos.y() - group_rect.center().y()
        if offset:
            x += offset[0]
            y += offset[1]
        group.setPos(x, y)
        self.scene().destroyItemGroup(group)

    def get_pipes_from_nodes(self, nodes=None):
        nodes = nodes or self.selected_nodes()
        if not nodes:
            return
        pipes = []
        for node in nodes:
            n_inputs = node.inputs if hasattr(node, 'inputs') else []
            n_outputs = node.outputs if hasattr(node, 'outputs') else []

            for port in n_inputs:
                for pipe in port.connected_pipes:
                    connected_node = pipe.output_port.node
                    if connected_node in nodes:
                        pipes.append(pipe)
            for port in n_outputs:
                for pipe in port.connected_pipes:
                    connected_node = pipe.input_port.node
                    if connected_node in nodes:
                        pipes.append(pipe)
        return pipes

    def center_selection(self, nodes=None):
        if not nodes:
            if self.selected_nodes():
                nodes = self.selected_nodes()
            elif self.all_nodes():
                nodes = self.all_nodes()
        if len(nodes) == 1:
            self.centerOn(nodes[0])
        else:
            rect = self._combined_rect(nodes)
            self.centerOn(rect.center().x(), rect.center().y())

    def get_pipe_layout(self):
        return self._pipe_layout

    def set_pipe_layout(self, layout):
        self._pipe_layout = layout
        for pipe in self.all_pipes():
            pipe.draw_path(pipe.input_port, pipe.output_port)

    def reset_zoom(self):
        self.scale(1.0, 1.0)
        self.resetTransform()

    def get_zoom(self):
        transform = self.transform()
        cur_scale = (transform.m11(), transform.m22())
        return float('{:0.2f}'.format(cur_scale[0] - 1.0))

    def set_zoom(self, value=0.0):
        if value == 0.0:
            self.reset_zoom()
            return
        zoom = self.get_zoom()
        if zoom < 0.0:
            if not (ZOOM_MIN <= zoom <= ZOOM_MAX):
                return
        else:
            if not (ZOOM_MIN <= value <= ZOOM_MAX):
                return
        value = value - zoom
        self._set_viewer_zoom(value)

    def zoom_to_nodes(self, nodes):
        rect = self._combined_rect(nodes)
        self.fitInView(rect, QtCore.Qt.KeepAspectRatio)
        if self.get_zoom() > 0.1:
            self.reset_zoom()
