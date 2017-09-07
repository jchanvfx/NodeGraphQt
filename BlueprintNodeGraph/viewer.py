#!/usr/bin/python
from PySide import QtGui, QtCore

import helpers
from .constants import (IN_PORT, OUT_PORT,
                        PIPE_LAYOUT_CURVED, PIPE_LAYOUT_STRAIGHT)
from .node import NodeItem
from .pipe import Pipe
from .port import PortItem


class NodeViewer(QtGui.QGraphicsView):

    def __init__(self, parent=None, scene=None):
        super(NodeViewer, self).__init__(scene, parent)
        self.setRenderHint(QtGui.QPainter.Antialiasing, True)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setViewportUpdateMode(QtGui.QGraphicsView.FullViewportUpdate)
        scene_area = 6400.0
        scene_pos = (scene_area / 2) * -1
        self.setSceneRect(scene_pos, scene_pos, scene_area, scene_area)
        self._zoom = 0
        self._pipe_layout = PIPE_LAYOUT_CURVED
        self._connection_pipe = None
        self._active_pipe = None
        self._start_port = None
        self._origin_pos = None
        self._previous_pos = None
        self._rubber_band = QtGui.QRubberBand(QtGui.QRubberBand.Rectangle, self)
        self.LMB_state = False
        self.RMB_state = False
        self.MMB_state = False

        self._setup_shortcuts()

    def __str__(self):
        return '{}()'.format(self.__class__.__name__)

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

    def _items_near(self, pos, item_type=None, size=20):
        x, y = (pos.x() - (size / 2)), (pos.y() - (size / 2))
        rect = QtCore.QRect(x, y, size, size)
        items = []
        for item in self.scene().items(rect):
            if not item_type or isinstance(item, item_type):
                items.append(item)
        return items

    def _map_scene_rect(self, rect=None):
        map_pos = self.mapToScene(rect.x(), rect.y())
        map_rect = QtCore.QRect(
            map_pos.x(), map_pos.y(), rect.width(), rect.height()
        )
        return map_rect

    def _setup_shortcuts(self):
        open_actn = QtGui.QAction('Open Session Layout', self)
        open_actn.setShortcut('Ctrl+o')
        open_actn.triggered.connect(self.load_session)
        save_actn = QtGui.QAction('Save Session Layout', self)
        save_actn.setShortcut('Ctrl+s')
        save_actn.triggered.connect(self.save_session)
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
        self.addAction(open_actn)
        self.addAction(save_actn)
        self.addAction(fit_zoom_actn)
        self.addAction(sel_all_actn)
        self.addAction(del_node_actn)

    def resizeEvent(self, event):
        super(NodeViewer, self).resizeEvent(event)

    def mousePressEvent(self, event):
        modifiers = QtGui.QApplication.keyboardModifiers()
        alt_pressed = modifiers == QtCore.Qt.AltModifier
        if event.button() == QtCore.Qt.LeftButton:
            self.LMB_state = True
        elif event.button() == QtCore.Qt.RightButton:
            self.RMB_state = True
        elif event.button() == QtCore.Qt.MiddleButton:
            self.MMB_state = True
        self._origin_pos = event.pos()
        self._previous_pos = event.pos()

        items = self._items_near(self.mapToScene(event.pos()), None, 20)
        if (self.LMB_state and not alt_pressed) and not items:
            rect = QtCore.QRect(self._previous_pos, QtCore.QSize()).normalized()
            map_rect = self._map_scene_rect(self._rubber_band.rect())
            self.scene().update(map_rect)
            self._rubber_band.setGeometry(rect)
            self._rubber_band.show()
        super(NodeViewer, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.LMB_state = False
        elif event.button() == QtCore.Qt.RightButton:
            self.RMB_state = False
        elif event.button() == QtCore.Qt.MiddleButton:
            self.MMB_state = False

        if self._rubber_band.isVisible():
            map_rect = self._map_scene_rect(self._rubber_band.rect())
            self._rubber_band.hide()
            self.scene().update(map_rect)
        super(NodeViewer, self).mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        modifiers = QtGui.QApplication.keyboardModifiers()
        alt_pressed = modifiers == QtCore.Qt.AltModifier
        if self.MMB_state or (self.LMB_state and alt_pressed):
            pos_x = (event.x() - self._previous_pos.x())
            pos_y = (event.y() - self._previous_pos.y())
            self._set_viewer_pan(pos_x, pos_y)
        elif self.RMB_state:
            pos_x = (event.x() - self._previous_pos.x())
            zoom = 0.1 if pos_x > 0 else -0.1
            self._set_viewer_zoom(zoom)

        if self.LMB_state and self._rubber_band.isVisible():
            rect = QtCore.QRect(self._origin_pos, event.pos()).normalized()
            map_rect = self._map_scene_rect(rect)
            path = QtGui.QPainterPath()
            path.addRect(map_rect)
            self._rubber_band.setGeometry(rect)
            self.scene().setSelectionArea(path, QtCore.Qt.ContainsItemShape)
            self.scene().update(map_rect)

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

    def start_connection(self, selected_port):
        """
        create new pipe for the connection.
        """
        if not selected_port:
            return
        self._start_port = selected_port
        self._connection_pipe = Pipe()
        self._connection_pipe.activate()
        self._connection_pipe.style = 'dotted'
        if self._start_port.type == IN_PORT:
            self._connection_pipe.input_port = self._start_port
        elif self._start_port == OUT_PORT:
            self._connection_pipe.output_port = self._start_port
        self.scene().addItem(self._connection_pipe)

    def end_connection(self):
        """
        delete connection pipe and reset start port.
        """
        if self._connection_pipe:
            self._connection_pipe.delete()
            self._connection_pipe = None
        self._start_port = None

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
        return True

    def make_pipe_connection(self, start_port, end_port):
        """
        remove existing pipes from "end_port" if multi connection is disabled.
        """
        if not end_port.multi_connection:
            for pipe in end_port.connected_pipes:
                pipe.delete()
        # make new pipe connection.
        ports = {
            start_port.port_type: start_port, end_port.port_type: end_port
        }
        pipe = Pipe()
        self.scene().addItem(pipe)
        pipe.input_port = ports[IN_PORT]
        pipe.output_port = ports[OUT_PORT]
        ports[IN_PORT].add_pipe(pipe)
        ports[OUT_PORT].add_pipe(pipe)
        pipe.draw_path(ports[OUT_PORT], ports[IN_PORT])
        self.end_connection()

    def sceneMouseMoveEvent(self, event):
        """
        triggered mouse move event for the scene.
         - redraw the connection pipe.

        Args:
            event (QtGui.QGraphicsSceneMouseEvent): 
                The event handler from the QtGui.QGraphicsScene
        """
        if not self._connection_pipe:
            return
        if not self._start_port:
            return
        self._connection_pipe.draw_path(
            self._start_port, None, event.scenePos()
        )

        pipes = self._start_port.connected_pipes
        if not self._start_port.multi_connection and pipes:
            pipes[0].delete()

    def sceneMousePressEvent(self, event):
        """
        triggered mouse press event for the scene.
         - detect selected pipe and start connection.

        Args:
            event (QtGui.QGraphicsScenePressEvent):
                The event handler from the QtGui.QGraphicsScene
        """
        if event.modifiers() == QtCore.Qt.ShiftModifier:
            event.setModifiers(QtCore.Qt.ControlModifier)

        pipe_items = self._items_near(event.scenePos(), Pipe, 20)
        pipe = pipe_items[0] if pipe_items else None
        if pipe:
            self._active_pipe = pipe
            self._active_pipe.activate()
            port = self._active_pipe.port_from_pos(event.scenePos(), True)
            self.start_connection(port)

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

        if not self._connection_pipe:
            return

        # find the end port.
        end_port = None
        for item in self.scene().items(event.scenePos()):
            if isinstance(item, PortItem):
                end_port = item
                break

        # validate connection check.
        if self.validate_connection(self._start_port, end_port):
            # make the connection.
            self.make_pipe_connection(self._start_port, end_port)
        else:
            # delete pipe and end connection.
            self.end_connection()

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
        node.init_node()
        self.scene().addItem(node)

    def delete_nodes(self, nodes):
        for node in nodes:
            if isinstance(node, NodeItem):
                node.delete()

    def delete_selected_nodes(self):
        nodes = self.selected_nodes()
        if nodes:
            self.delete_nodes(nodes)

    def select_all_nodes(self):
        for node in self.all_nodes():
            node.setSelected(True)

    def connect_ports(self, from_port, to_port):
        if not isinstance(from_port, PortItem):
            return
        if self.validate_connection(from_port, to_port):
            self.make_pipe_connection(from_port, to_port)

    def save_session(self, file_path=None, save_dialog=True):
        if save_dialog:
            file_dlg = QtGui.QFileDialog.getSaveFileName(
                self,
                caption='Save Session Setup',
                filter='Node Graph (*.ngraph *.json)')
            file_path = file_dlg[0]
        if not file_path:
            return
        session = helpers.SessionSaver(self.all_nodes(), self.all_pipes())
        session.save_session(file_path)

    def load_session(self, file_path=None, open_dialog=True):
        if open_dialog:
            file_dlg = QtGui.QFileDialog.getOpenFileName(
                self,
                caption='Open Session Setup',
                filter='Node Graph (*.ngraph *.json)')
            file_path = file_dlg[0]
        if not file_path:
            return
        self.clear_scene()
        session = helpers.SessionLoader(self)
        session.load_file(file_path)

    def clear_scene(self):
        for node in self.all_nodes():
            node.delete()
        for item in self.scene().items():
            self.scene().removeItem(item)

    def clear_selection(self):
        self.scene().clearSelection()

    def center_selection(self, nodes=None):
        if not nodes:
            if self.selected_nodes():
                nodes = self.selected_nodes()
            elif self.all_nodes():
                nodes = self.all_nodes()
        if len(nodes) == 1:
            self.centerOn(nodes[0])
        else:
            group = self.scene().createItemGroup(nodes)
            group_rect = group.boundingRect()
            self.centerOn(group_rect.center().x(), group_rect.center().y())
            self.scene().destroyItemGroup(group)

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

