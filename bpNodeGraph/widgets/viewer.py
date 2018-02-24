#!/usr/bin/python
import re

from PySide import QtGui, QtCore

from .commands import *
from .constants import (IN_PORT, OUT_PORT,
                        PIPE_LAYOUT_CURVED,
                        PIPE_LAYOUT_STRAIGHT,
                        PIPE_STYLE_DASHED,
                        FILE_IO_EXT)
from .node import NodeItem
from .pipe import Pipe
from .port import PortItem
from ..utils.serializer import SessionSerializer, SessionLoader


class NodeViewer(QtGui.QGraphicsView):

    def __init__(self, parent=None, scene=None):
        super(NodeViewer, self).__init__(scene, parent)
        self.setRenderHint(QtGui.QPainter.Antialiasing, True)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setViewportUpdateMode(QtGui.QGraphicsView.FullViewportUpdate)
        scene_area = 8000.0
        scene_pos = (scene_area / 2) * -1
        self.setSceneRect(scene_pos, scene_pos, scene_area, scene_area)
        self._zoom = 0
        self._file_format = FILE_IO_EXT
        self._pipe_layout = PIPE_LAYOUT_CURVED
        self._live_pipe = None
        self._detached_port = None
        self._active_pipe = None
        self._start_port = None
        self._origin_pos = None
        self._previous_pos = None
        self._prev_selection = []
        self._rubber_band = QtGui.QRubberBand(QtGui.QRubberBand.Rectangle, self)
        self._undo_stack = QtGui.QUndoStack(self)
        self.LMB_state = False
        self.RMB_state = False
        self.MMB_state = False

        self._setup_shortcuts()

    def __str__(self):
        return '{}.{}'.format(
            self.__module__, self.__class__.__name__)

    def __repr__(self):
        return '{}.{}'.format(
            self.__module__, self.__class__.__name__)

    def _set_viewer_zoom(self, value):
        max_zoom = 12
        min_zoom = max_zoom * -1
        if value > 0.0:
            if self._zoom <= max_zoom:
                self._zoom += 1
        else:
            if self._zoom >= min_zoom:
                self._zoom -= 1
        if self._zoom == 0:
            self.fitInView()
            return
        if self._zoom >= max_zoom:
            return
        if self._zoom <= min_zoom:
            return
        scale = 1.0 + value
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
        rect = QtCore.QRect(x, y, width, height)
        items = []
        for item in self.scene().items(rect):
            if not item_type or isinstance(item, item_type):
                items.append(item)
        return items

    def _setup_shortcuts(self):
        undo_actn = self._undo_stack.createUndoAction(self, '&Undo')
        undo_actn.setShortcuts(QtGui.QKeySequence.Undo)
        redo_actn = self._undo_stack.createRedoAction(self, '&Redo')
        redo_actn.setShortcuts(QtGui.QKeySequence.Redo)

        open_actn = QtGui.QAction('Open Session Layout', self)
        open_actn.setShortcut('Ctrl+o')
        open_actn.triggered.connect(self.load_dialog)
        save_actn = QtGui.QAction('Save Session Layout', self)
        save_actn.setShortcut('Ctrl+s')
        save_actn.triggered.connect(self.save_dialog)
        fit_zoom_actn = QtGui.QAction('Reset Zoom', self)
        fit_zoom_actn.setShortcut('f')
        fit_zoom_actn.triggered.connect(self.set_zoom)
        fit_zoom_actn.triggered.connect(self.center_selection)
        sel_all_actn = QtGui.QAction('Select All', self)
        sel_all_actn.setShortcut('Ctrl+A')
        sel_all_actn.triggered.connect(self.select_all_nodes)
        del_node_actn = QtGui.QAction('Delete Selection', self)
        del_node_actn.setShortcuts(['Del', 'Backspace'])
        del_node_actn.triggered.connect(self.delete_selected_nodes)

        node_duplicate = QtGui.QAction('Duplicate Nodes', self)
        node_duplicate.setShortcut('Alt+c')
        node_duplicate.triggered.connect(self.duplicate_nodes)
        node_copy = QtGui.QAction('Copy', self)
        node_copy.setShortcut(QtGui.QKeySequence.Copy)
        node_copy.triggered.connect(self.copy_to_clipboard)
        node_paste = QtGui.QAction('Paste', self)
        node_paste.setShortcut(QtGui.QKeySequence.Paste)
        node_paste.triggered.connect(self.paste_from_clipboard)

        self.addAction(undo_actn)
        self.addAction(redo_actn)
        self.addAction(open_actn)
        self.addAction(save_actn)
        self.addAction(fit_zoom_actn)
        self.addAction(sel_all_actn)
        self.addAction(del_node_actn)
        self.addAction(node_duplicate)
        self.addAction(node_copy)
        self.addAction(node_paste)

    def resizeEvent(self, event):
        super(NodeViewer, self).resizeEvent(event)

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

        items = self._items_near(self.mapToScene(event.pos()), None, 20, 20)
        if shift_modifier:
            for item in items:
                if isinstance(item, NodeItem):
                    item.selected = not item.selected

        for n in self.selected_nodes():
            n.prev_pos = n.pos

        if (self.LMB_state and not alt_modifier) and not items:
            rect = QtCore.QRect(self._previous_pos, QtCore.QSize()).normalized()
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

        if self._rubber_band.isVisible():
            rect = self._rubber_band.rect()
            map_rect = self.mapToScene(rect).boundingRect()
            self._rubber_band.hide()
            self.scene().update(map_rect)

        # push undo move command.
        moved_nodes = []
        for node in self.selected_nodes():
            if node.pos != node.prev_pos:
                moved_nodes.append(node)
        if moved_nodes:
            undo_cmd = NodesMoveCmd(moved_nodes)
            self._undo_stack.push(undo_cmd)

        super(NodeViewer, self).mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        alt_modifier = event.modifiers() == QtCore.Qt.AltModifier
        shift_modifier = event.modifiers() == QtCore.Qt.ShiftModifier
        if self.MMB_state or (self.LMB_state and alt_modifier):
            pos_x = (event.x() - self._previous_pos.x())
            pos_y = (event.y() - self._previous_pos.y())
            self._set_viewer_pan(pos_x, pos_y)
        elif self.RMB_state:
            pos_x = (event.x() - self._previous_pos.x())
            zoom = 0.1 if pos_x > 0 else -0.1
            self._set_viewer_zoom(zoom)

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
                        node.setSelected(True)

        self._previous_pos = event.pos()
        super(NodeViewer, self).mouseMoveEvent(event)

    def wheelEvent(self, event):
        adjust = (event.delta() / 120) * 0.1
        self._set_viewer_zoom(adjust)

    def fitInView(self):
        unity = self.transform().mapRect(QtCore.QRectF(0, 0, 1, 1))
        self.scale(1 / unity.width(), 1 / unity.height())
        self._zoom = 0

    # def dropEvent(self, event):
    #     if event.mimeData().hasFormat('component/name'):
    #         drop_str = str(event.mimeData().data('component/name'))
    #         drop_pos = event.pos()

    # def dragEnterEvent(self, event):
    #     if event.mimeData().hasFormat('component/name'):
    #         event.accept()

    # def dragMoveEvent(self, event):
    #     if event.mimeData().hasFormat('component/name'):
    #         event.accept()

    def get_unique_node_name(self, name):
        regex = re.compile('([aA-zZ ]+)(?:(?: )*(\d+))')
        match = regex.match(name.strip())
        version = ''
        if match:
            name = match.group(1)
            version = match.group(2) or ''
        unique_name = '{}{}'.format(name, version).strip()
        regex = re.compile('[aA-zZ ]+(\d+)')
        names = []
        versions = []
        for node in self.all_nodes():
            names.append(node.name)
            match = regex.match(node.name)
            if match:
                versions.append(int(match.group(1)))
        if unique_name not in names:
            return unique_name
        if versions:
            for x in range(1, max(versions) + 2):
                unique_name = '{} {}'.format(name, x)
                if unique_name not in names:
                    break
        else:
            for x in range(1, len(names) + 2):
                unique_name = '{} {}'.format(name, x)
                if unique_name not in names:
                    break
        return unique_name

    def start_connection(self, selected_port):
        """
        create new pipe for the connection.
        """
        if not selected_port:
            return
        self._start_port = selected_port
        self._live_pipe = Pipe()
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
        """
        if self._live_pipe:
            self._live_pipe.delete()
            self._live_pipe = None
        self._start_port = None

    def validate_acyclic_connection(self, start_port, end_port):
        """
        validate the connection doesn't loop itself.
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

    def validate_connection(self, start_port, end_port):
        """
        validate "end_port" connection check.
        """
        if not end_port:
            return False
        if end_port == start_port:
            return False
        if end_port.port_type == start_port.port_type:
            return False
        if end_port.node == start_port.node:
            return False
        if start_port in end_port.connected_ports:
            return False
        if not self.validate_acyclic_connection(start_port, end_port):
            return False
        return True

    def make_pipe_connection(self, start_port, end_port):
        """
        establishes a pipe connection.
        """
        # remove existing pipes from "end_port" if multi connection is disabled.
        port = None
        if not end_port.multi_connection:
            for pipe in end_port.connected_pipes:
                port_funcs = {IN_PORT: 'output_port', OUT_PORT: 'input_port'}
                port = getattr(pipe, port_funcs[end_port.port_type])
                pipe.delete()

        # make new pipe connection.
        ports = {
            start_port.port_type: start_port,
            end_port.port_type: end_port
        }
        pipe = Pipe()
        self.scene().addItem(pipe)
        pipe.input_port = ports[IN_PORT]
        pipe.output_port = ports[OUT_PORT]
        ports[IN_PORT].add_pipe(pipe)
        ports[OUT_PORT].add_pipe(pipe)
        pipe.draw_path(ports[OUT_PORT], ports[IN_PORT])

        # return port that was connected to the existing pipe.
        return port

    def sceneMouseMoveEvent(self, event):
        """
        triggered mouse move event for the scene.
         - redraw the connection pipe.

        Args:
            event (QtGui.QGraphicsSceneMouseEvent): 
                The event handler from the QtGui.QGraphicsScene
        """
        if not self._live_pipe:
            return
        if not self._start_port:
            return
        pos = event.scenePos()
        self._live_pipe.draw_path(self._start_port, None, pos)

    def sceneMousePressEvent(self, event):
        """
        triggered mouse press event for the scene.
         - detect selected pipe and start connection.
         - remap Shift and Ctrl modifier.

        Args:
            event (QtGui.QGraphicsScenePressEvent):
                The event handler from the QtGui.QGraphicsScene
        """
        ctrl_modifier = event.modifiers() == QtCore.Qt.ControlModifier
        alt_modifier = event.modifiers() == QtCore.Qt.AltModifier
        shift_modifier = event.modifiers() == QtCore.Qt.ShiftModifier
        if shift_modifier:
            event.setModifiers(QtCore.Qt.ControlModifier)
        elif ctrl_modifier:
            event.setModifiers(QtCore.Qt.ShiftModifier)

        if not alt_modifier:
            pos = event.scenePos()
            port_items = self._items_near(pos, PortItem, 5, 5)
            if port_items:
                port = port_items[0]
                if not port.multi_connection and port.connected_ports:
                    self._detached_port = port.connected_ports[0]
                    [p.delete() for p in port.connected_pipes]
                return
            node_items = self._items_near(pos, NodeItem, 3, 3)
            if node_items:
                return
            pipe_items = self._items_near(pos, Pipe, 3, 3)
            if pipe_items:
                self._active_pipe = pipe_items[0]
                active_ports = [self._active_pipe.input_port,
                                self._active_pipe.output_port]
                port = self._active_pipe.port_from_pos(pos, True)
                active_ports.pop(active_ports.index(port))
                self._detached_port = active_ports[0]
                if not shift_modifier or not port.multi_connection:
                    self._active_pipe.delete()
                self.start_connection(port)
                self._live_pipe.draw_path(self._start_port, None, pos)

    def sceneMouseReleaseEvent(self, event):
        """
        triggered mouse release event for the scene.
         - verify to make a the connection Pipe().
        
        Args:
            event (QtGui.QGraphicsSceneMouseEvent): 
                The event handler from the QtGui.QGraphicsScene
        """
        if event.modifiers() == QtCore.Qt.ShiftModifier:
            event.setModifiers(QtCore.Qt.ControlModifier)

        if not self._live_pipe:
            return

        end_port = None
        dis_port = None

        # find the end port.
        for item in self.scene().items(event.scenePos()):
            if isinstance(item, PortItem):
                end_port = item
                break

        # validate connection check.
        if self.validate_connection(self._start_port, end_port):
            # make the connection.
            dis_port = self.make_pipe_connection(self._start_port, end_port)

        if self._detached_port == end_port:
            self.end_live_connection()
            if self._active_pipe and self._active_pipe.active():
                self._active_pipe.reset()
                self._active_pipe = None
            return

        # register undo command.
        if self._detached_port:
            if end_port is None:
                self._undo_stack.push(
                    NodeConnectionCmd(self._start_port,
                                      self._detached_port,
                                      'disconnect'))
            elif not end_port.multi_connection:  # single connection
                if dis_port:
                    self._undo_stack.push(
                        NodeConnectionSwitchedCmd(self._start_port,
                                                  end_port,
                                                  dis_port,
                                                  self._detached_port))
                else:
                    self._undo_stack.push(
                        NodeConnectionChangedCmd(self._start_port,
                                                 end_port,
                                                 self._detached_port))
            else:
                self._undo_stack.push(
                    NodeConnectionChangedCmd(self._start_port,
                                             end_port,
                                             self._detached_port))

            self._detached_port = None
        else:
            if not end_port.multi_connection:  # single connection
                if dis_port:
                    self._undo_stack.push(
                        NodeConnectionSwitchedCmd(self._start_port,
                                                  end_port,
                                                  dis_port))
                else:
                    self._undo_stack.push(NodeConnectionCmd(self._start_port,
                                                            end_port,
                                                            'connect'))
            else:
                self._undo_stack.push(NodeConnectionCmd(self._start_port,
                                                        end_port,
                                                        'connect'))

        # end the live connection.
        self.end_live_connection()

        if self._active_pipe and self._active_pipe.active():
            self._active_pipe.reset()
            self._active_pipe = None

    def all_pipes(self):
        pipes = []
        for item in self.scene().items():
            if isinstance(item, Pipe):
                pipes.append(item)
        return pipes

    def all_nodes(self):
        nodes = []
        for item in self.scene().items():
            if isinstance(item, NodeItem):
                nodes.append(item)
        return nodes

    def selected_nodes(self):
        nodes = []
        for item in self.scene().selectedItems():
            if isinstance(item, NodeItem):
                nodes.append(item)
        return nodes

    def add_node(self, node):
        unique_name = self.get_unique_node_name(node.name)
        node.name = unique_name
        self.scene().addItem(node)
        node.init_node()

    def delete_node(self, node):
        if isinstance(node, NodeItem):
            node.delete()

    def delete_selected_nodes(self):
        for node in self.selected_nodes():
            if isinstance(node, NodeItem):
                node.delete()

    def get_pipes_from_nodes(self, nodes=None):
        nodes = nodes or self.selected_nodes()
        if not nodes:
            return
        pipes = []
        for node in nodes:
            for port in node.inputs:
                for pipe in port.connected_pipes:
                    connected_node = pipe.output_port.node
                    if connected_node in nodes:
                        pipes.append(pipe)
            for port in node.outputs:
                for pipe in port.connected_pipes:
                    connected_node = pipe.input_port.node
                    if connected_node in nodes:
                        pipes.append(pipe)
        return pipes

    def copy_to_clipboard(self, nodes=None):
        nodes = nodes or self.selected_nodes()
        if not nodes:
            return
        pipes = self.get_pipes_from_nodes(nodes)
        serializer = SessionSerializer(nodes, pipes)
        clipboard = QtGui.QClipboard()
        clipboard.setText(serializer.serialize_to_str())

    def load_nodes_data(self, data):
        self.clear_selection()
        loader = SessionLoader(self)
        loaded_nodes = loader.load_str(data)
        if not loaded_nodes:
            return
        group = self.scene().createItemGroup(loaded_nodes)
        group_rect = group.boundingRect()
        prev_x, prev_y = self._previous_pos.x(), self._previous_pos.y()
        orig_x, orig_y = self._origin_pos.x(), self._origin_pos.y()
        if (prev_x, prev_y) != (orig_x, orig_y):
            pos = self.mapToScene(self._previous_pos)
            x = pos.x() - group_rect.center().x()
            y = pos.y() - group_rect.center().y()
        else:
            x, y = group.pos().x() + 50, group.pos().y() + 50
        group.setPos(x, y)
        self.scene().destroyItemGroup(group)
        self._origin_pos = self._previous_pos

    def paste_from_clipboard(self):
        clipboard = QtGui.QClipboard()
        data_string = clipboard.text()
        self.load_nodes_data(data_string)

    def duplicate_nodes(self, nodes=None):
        nodes = nodes or self.selected_nodes()
        if not nodes:
            return
        pipes = self.get_pipes_from_nodes(nodes)
        serializer = SessionSerializer(nodes, pipes)
        data = serializer.serialize_to_str()
        self.load_nodes_data(data)

    def select_all_nodes(self):
        for node in self.all_nodes():
            node.setSelected(True)

    def connect_ports(self, from_port, to_port):
        if not isinstance(from_port, PortItem):
            return
        if self.validate_connection(from_port, to_port):
            self.make_pipe_connection(from_port, to_port)
            self.end_live_connection()

    def save_dialog(self):
        file_dlg = QtGui.QFileDialog.getSaveFileName(
            self,
            caption='Save Session Setup',
            filter='Node Graph (*{})'.format(self._file_format))
        file_path = file_dlg[0]
        if not file_path:
            return
        self.write(file_path)

    def load_dialog(self):
        file_dlg = QtGui.QFileDialog.getOpenFileName(
            self,
            caption='Open Session Setup',
            filter='Node Graph (*{}) All Files (*)'.format(self._file_format))
        file_path = file_dlg[0]
        if not file_path:
            return
        self.load(file_path)

    def write(self, file_path):
        serializer = SessionSerializer(self.all_nodes(), self.all_pipes())
        serializer.write(file_path)

    def load(self, file_path):
        self.clear_scene()
        loader = SessionLoader(self)
        loader.load(file_path)

    def clear_scene(self):
        for node in self.all_nodes():
            node.delete()
        for item in self.scene().items():
            self.scene().removeItem(item)

    def clear_selection(self):
        for node in self.selected_nodes():
            node.selected = False
        # self.scene().clearSelection()

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

    def set_pipe_layout(self, layout=''):
        layout_types = {
            'curved': PIPE_LAYOUT_CURVED,
            'straight': PIPE_LAYOUT_STRAIGHT
        }
        self._pipe_layout = layout_types.get(layout, 'curved')
        for pipe in self.all_pipes():
            pipe.draw_path(pipe.input_port, pipe.output_port)

    def set_zoom(self, zoom=0):
        if zoom == 0:
            self.fitInView()
            return
        self._zoom = zoom
        if self._zoom > 10:
            self._zoom = 10
        elif self._zoom < -10:
            self._zoom = -10
        zoom_factor = self._zoom * 0.1
        self._set_viewer_zoom(zoom_factor)

    def get_zoom(self):
        return self._zoom
