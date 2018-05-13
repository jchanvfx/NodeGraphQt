#!/usr/bin/python
import re
from collections import OrderedDict

from PySide2 import QtGui, QtCore, QtWidgets

from .commands import *
from .constants import (IN_PORT, OUT_PORT,
                        PIPE_LAYOUT_CURVED,
                        PIPE_LAYOUT_STRAIGHT,
                        PIPE_STYLE_DASHED)
from .node_abstract import AbstractNodeItem
from .node_backdrop import BackdropNodeItem
from .pipe import Pipe
from .port import PortItem
from .stylesheet import STYLE_QMENU
from .tab_search import TabSearchWidget
from .viewer_actions import setup_viewer_actions
from ..base.node_vendor import NodeVendor
from ..base.serializer import SessionSerializer, SessionLoader

ZOOM_LIMIT = 12


class NodeViewer(QtWidgets.QGraphicsView):

    search_triggered = QtCore.Signal(str, tuple)

    def __init__(self, parent=None, scene=None):
        super(NodeViewer, self).__init__(scene, parent)
        self.setRenderHint(QtGui.QPainter.Antialiasing, True)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setViewportUpdateMode(QtWidgets.QGraphicsView.FullViewportUpdate)
        scene_area = 8000.0
        scene_pos = (scene_area / 2) * -1
        self.setSceneRect(scene_pos, scene_pos, scene_area, scene_area)
        self._zoom = 0
        self._current_file = None
        self._pipe_layout = PIPE_LAYOUT_CURVED
        self._live_pipe = None
        self._detached_port = None
        self._start_port = None
        self._origin_pos = None
        self._previous_pos = QtCore.QPoint(self.width(), self.height())
        self._prev_selection = []
        self._rubber_band = QtWidgets.QRubberBand(
            QtWidgets.QRubberBand.Rectangle, self
        )
        self._undo_stack = QtWidgets.QUndoStack(self)
        self._context_menu = QtWidgets.QMenu(self, 'Node Graph')
        self._context_menu.setStyleSheet(STYLE_QMENU)
        self._sub_context_menus = OrderedDict()
        self._sub_context_menus['File'] = QtWidgets.QMenu(None, title='File')
        self._sub_context_menus['Edit'] = QtWidgets.QMenu(None, title='Edit')
        self._search_widget = TabSearchWidget(self, NodeVendor.names)
        self._search_widget.search_submitted.connect(self._on_search_submitted)

        self.acyclic = True
        self.LMB_state = False
        self.RMB_state = False
        self.MMB_state = False

        self._initialize_viewer()

    def __str__(self):
        return '{}.{}()'.format(
            self.__module__, self.__class__.__name__)

    def __repr__(self):
        return '{}.{}()'.format(
            self.__module__, self.__class__.__name__)

    def _acyclic_check(self, start_port, end_port):
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

    def _set_viewer_zoom(self, value):
        max_zoom = ZOOM_LIMIT
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

    def _toggle_tab_search(self):
        self._search_widget.set_nodes(NodeVendor.names)

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

    def _on_search_submitted(self, node_type):
        pos = self.mapToScene(self._previous_pos)
        self.search_triggered.emit(node_type, (pos.x(), pos.y()))

    def _initialize_viewer(self):
        # setup menus
        for menu in self._sub_context_menus.values():
            menu.setStyleSheet(STYLE_QMENU)
            self._context_menu.addMenu(menu)

        # populate context menu
        setup_viewer_actions(self)

        # add in the tab search.
        tab = QtWidgets.QAction('search nodes', self)
        tab.setShortcut('tab')
        tab.triggered.connect(self._toggle_tab_search)
        self.addAction(tab)

    def resizeEvent(self, event):
        super(NodeViewer, self).resizeEvent(event)

    def contextMenuEvent(self, event):
        self.RMB_state = False
        self._context_menu.exec_(event.globalPos())

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
            self._toggle_tab_search()

        if alt_modifier:
            return

        items = self._items_near(self.mapToScene(event.pos()), None, 20, 20)
        nodes = [i for i in items if isinstance(i, AbstractNodeItem)]

        # toggle extend node selection.
        if shift_modifier:
            for node in nodes:
                node.selected = not node.selected

        for n in self.selected_nodes():
            n.prev_pos = n.pos

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

        # hide selection selection marquee
        if self._rubber_band.isVisible():
            rect = self._rubber_band.rect()
            map_rect = self.mapToScene(rect).boundingRect()
            self._rubber_band.hide()
            self.scene().update(map_rect)

        # push undo move command.
        nodes_pos_changed = [
            n for n in self.selected_nodes() if n.pos != n.prev_pos
        ]
        if nodes_pos_changed:
            self._undo_stack.beginMacro('move nodes')
            for node in nodes_pos_changed:
                self._undo_stack.push(NodePositionChangedCmd(node))
            self._undo_stack.endMacro()

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
                        node.selected = True

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
        name = ' '.join(name.split())
        node_names = [n.name for n in self.all_nodes()]
        if name not in node_names:
            return name

        regex = re.compile('[\w ]+(?: )*(\d+)')
        search = regex.search(name)
        if not search:
            for x in range(1, len(node_names) + 1):
                new_name = '{} {}'.format(name, x)
                if new_name not in node_names:
                    return new_name

        version = search.group(1)
        name = name[:len(version) * -1].strip()
        for x in range(1, len(node_names) + 1):
            new_name = '{} {}'.format(name, x)
            if new_name not in node_names:
                return new_name

    def start_live_connection(self, selected_port):
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
        self._live_pipe.draw_path(self._start_port, None, pos)

    def sceneMousePressEvent(self, event):
        """
        triggered mouse press event for the scene.
         - detect selected pipe and start connection.
         - remap Shift and Ctrl modifier.

        Args:
            event (QtWidgets.QGraphicsScenePressEvent):
                The event handler from the QtWidgets.QGraphicsScene
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
                self.start_live_connection(port)
                if not port.multi_connection:
                    [p.delete() for p in port.connected_pipes]
                return

            node_items = self._items_near(pos, AbstractNodeItem, 3, 3)
            if node_items:
                if not isinstance(node_items[0], BackdropNodeItem):
                    return

            pipe_items = self._items_near(pos, Pipe, 3, 3)
            if pipe_items:
                pipe = pipe_items[0]
                attr = {IN_PORT: 'output_port', OUT_PORT: 'input_port'}
                from_port = pipe.port_from_pos(pos, True)
                to_port = getattr(pipe, attr[from_port.port_type])
                if not from_port.multi_connection and from_port.connected_ports:
                    self._detached_port = from_port.connected_ports[0]
                elif not to_port.multi_connection:
                    self._detached_port = to_port

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
        if event.modifiers() == QtCore.Qt.ShiftModifier:
            event.setModifiers(QtCore.Qt.ControlModifier)

        if not self._live_pipe:
            return

        # find the end port.
        end_port = None
        for item in self.scene().items(event.scenePos()):
            if isinstance(item, PortItem):
                end_port = item
                break

        if end_port is None:
            if self._detached_port:
                self._undo_stack.push(
                    NodeDisconnectedCmd(self._start_port, self._detached_port)
                )
            self._detached_port = None
            self.end_live_connection()
            return

        # restore connection check.
        restore_connection = [
            # if same port type.
            end_port.port_type == self._start_port.port_type,
            # if connection to itself.
            end_port.node == self._start_port.node,
            # if end port is the start port.
            end_port == self._start_port,
            # if detached port is the end port.
            self._detached_port == end_port
        ]
        if any(restore_connection):
            pipe = Pipe()
            self.scene().addItem(pipe)
            to_port = self._detached_port or end_port
            pipe.set_connections(self._start_port, to_port)
            pipe.draw_path(pipe.input_port, pipe.output_port)
            self._detached_port = None
            self.end_live_connection()
            return

        # register as disconnected if not acyclic.
        if self.acyclic and not self._acyclic_check(self._start_port, end_port):
            if self._detached_port:
                self._undo_stack.push(
                    NodeDisconnectedCmd(self._start_port, self._detached_port)
                )
            self._detached_port = None
            self.end_live_connection()
            return

        # make connection.
        cmds = []
        if not end_port.multi_connection and end_port.connected_ports:
            dettached_end = end_port.connected_ports[0]
            cmds.append(NodeDisconnectedCmd(end_port, dettached_end))
        if self._detached_port:
            cmds.append(
                NodeDisconnectedCmd(self._start_port, self._detached_port)
            )
        cmds.append(NodeConnectedCmd(self._start_port, end_port))

        self._undo_stack.beginMacro('connected node')
        [self._undo_stack.push(c) for c in cmds]
        self._undo_stack.endMacro()

        self._detached_port = None
        self.end_live_connection()

    def context_menu(self):
        return self._context_menu

    def add_menu(self, name, menu):
        menu.setStyleSheet(STYLE_QMENU)
        self._sub_context_menus[name] = menu
        self._context_menu.addMenu(self._sub_context_menus[name])
        return self._sub_context_menus[name]

    def get_menu(self, name):
        return self._sub_context_menus.get(name)

    def question_dialog(self, title, text):
        dlg = QtWidgets.QMessageBox.question(
            self, title, text,
            QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
        return dlg == QtWidgets.QMessageBox.Yes

    def message_dialog(self, text, title='node graph'):
        QtWidgets.QMessageBox.information(
            self, title, text, QtWidgets.QMessageBox.Ok)

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
        node.name = self.get_unique_node_name(node.name)
        node.pre_init(self, pos)
        self._undo_stack.push(NodeCreatedCommand(node, self.scene()))
        node.post_init(self, pos)

    def delete_node(self, node):
        if isinstance(node, AbstractNodeItem):
            self._undo_stack.push(NodeDeletedCmd(node, self.scene()))

    def delete_selected_nodes(self):
        self._undo_stack.beginMacro('delete selected node(s)')
        for node in self.selected_nodes():
            if isinstance(node, AbstractNodeItem):
                self._undo_stack.push(NodeDeletedCmd(node, self.scene()))
        self._undo_stack.endMacro()

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
        loaded_nodes = loader.load_string_data(data)
        if not loaded_nodes:
            return []

        # offset loaded nodes.
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
        return loaded_nodes

    def paste_from_clipboard(self):
        clipboard = QtGui.QClipboard()
        data_string = clipboard.text()
        self._undo_stack.beginMacro('pasted nodes')
        self.load_nodes_data(data_string)
        self._undo_stack.endMacro()

    def duplicate_nodes(self, nodes=None):
        nodes = nodes or self.selected_nodes()
        if not nodes:
            return []
        pipes = self.get_pipes_from_nodes(nodes)
        serializer = SessionSerializer(nodes, pipes)
        data = serializer.serialize_to_str()
        self._undo_stack.beginMacro('duplicated nodes')
        new_nodes = self.load_nodes_data(data)
        self._undo_stack.endMacro()
        return new_nodes

    def select_all_nodes(self):
        for node in self.all_nodes():
            node.selected = True

    def toggle_nodes_disability(self):
        nodes = self.selected_nodes()
        state = not nodes[0].disabled if nodes else False
        for node in nodes:
            node.disabled = state

        name = 'enable' if state else 'disable'
        self._undo_stack.beginMacro('{} node(s)'.format(name))
        for node in nodes:
            self._undo_stack.push(NodeDisabledCmd(node))
        self._undo_stack.endMacro()

    def connect_ports(self, from_port, to_port):
        if not isinstance(from_port, PortItem):
            return

        pre_conn_port = None
        if not from_port.multi_connection and from_port.connected_ports:
            pre_conn_port = from_port.connected_ports[0]

        if not to_port:
            if pre_conn_port:
                self._undo_stack.push(
                    NodeDisconnectedCmd(from_port, pre_conn_port)
                )
            return

        if self.acyclic and not self._acyclic_check(from_port, to_port):
            if pre_conn_port:
                self._undo_stack.push(
                    NodeDisconnectedCmd(self._start_port, pre_conn_port)
                )
                return

        cmds = []
        if not to_port.multi_connection and to_port.connected_ports:
            dettached_port = to_port.connected_ports[0]
            cmds.append(NodeDisconnectedCmd(to_port, dettached_port))
        if pre_conn_port:
            cmds.append(NodeDisconnectedCmd(from_port, pre_conn_port))
        cmds.append(NodeConnectedCmd(from_port, to_port))

        self._undo_stack.beginMacro('connected node')
        [self._undo_stack.push(c) for c in cmds]
        self._undo_stack.endMacro()

    def current_loaded_file(self):
        return self._current_file

    def save(self, path=None, load=True):
        try:
            serializer = SessionSerializer(self.all_nodes(), self.all_pipes())
            serializer.write(path)
            if load:
                self._current_file = path
        except Exception as e:
            print(e)

    def load(self, file_path):
        self.clear()
        loader = SessionLoader(self)
        loader.load(file_path)
        self._current_file = file_path

    def clear(self):
        for node in self.all_nodes():
            node.delete()
        for item in self.scene().items():
            self.scene().removeItem(item)
        self._current_file = None

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
        if zoom > 0 and zoom >= ZOOM_LIMIT:
            zoom = 12
        elif zoom <= (ZOOM_LIMIT * -1):
            zoom = -12
        zoom_factor = float(zoom) * 0.1
        self._set_viewer_zoom(zoom_factor)

    def get_zoom(self):
        return self._zoom

    def zoom_in(self):
        self.set_zoom(1)

    def zoom_out(self):
        self.set_zoom(-1)
