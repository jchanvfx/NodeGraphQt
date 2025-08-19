#!/usr/bin/python
# -*- coding: utf-8 -*-
import math
from distutils.version import LooseVersion

from Qt import QtGui, QtCore, QtWidgets

from NodeGraphQt.base.menu import BaseMenu
from NodeGraphQt.constants import (
    LayoutDirectionEnum,
    PortTypeEnum,
    PipeEnum,
    PipeLayoutEnum,
    ViewerEnum,
    Z_VAL_PIPE,
)
from NodeGraphQt.qgraphics.node_abstract import AbstractNodeItem
from NodeGraphQt.qgraphics.node_backdrop import BackdropNodeItem
from NodeGraphQt.qgraphics.pipe import PipeItem, LivePipeItem
from NodeGraphQt.qgraphics.port import PortItem
from NodeGraphQt.qgraphics.slicer import SlicerPipeItem
from NodeGraphQt.widgets.dialogs import BaseDialog, FileDialog
from NodeGraphQt.widgets.scene import NodeScene
from NodeGraphQt.widgets.tab_search import TabSearchMenuWidget

ZOOM_MIN = -0.95
ZOOM_MAX = 2.0


class NodeViewer(QtWidgets.QGraphicsView):
    """
    The widget interface used for displaying the scene and nodes.

    functions in this class should mainly be called by the
    class:`NodeGraphQt.NodeGraph` class.
    """

    # node viewer signals.
    # (some of these signals are called by port & node items and connected
    # to the node graph slot functions)
    moved_nodes = QtCore.Signal(object)
    search_triggered = QtCore.Signal(str, tuple)
    connection_sliced = QtCore.Signal(list)
    connection_changed = QtCore.Signal(list, list)
    insert_node = QtCore.Signal(object, str, object)
    node_name_changed = QtCore.Signal(str, str)
    node_backdrop_updated = QtCore.Signal(str, str, object)

    # pass through signals that are translated into "NodeGraph()" signals.
    node_selected = QtCore.Signal(str)
    node_selection_changed = QtCore.Signal(list, list)
    node_double_clicked = QtCore.Signal(str)
    data_dropped = QtCore.Signal(QtCore.QMimeData, object)
    context_menu_prompt = QtCore.Signal(str, object)

    def __init__(self, parent=None, undo_stack=None):
        """
        Args:
            parent:
            undo_stack (QtWidgets.QUndoStack): undo stack from the parent
                                               graph controller.
        """
        super(NodeViewer, self).__init__(parent)

        self.setScene(NodeScene(self))
        self.setRenderHint(QtGui.QPainter.Antialiasing, True)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setViewportUpdateMode(QtWidgets.QGraphicsView.BoundingRectViewportUpdate)
        self.setCacheMode(QtWidgets.QGraphicsView.CacheBackground)

        self.setAcceptDrops(True)
        self.resize(850, 800)

        self._scene_range = QtCore.QRectF(
            0, 0, self.size().width(), self.size().height())
        self._update_scene()
        self._last_size = self.size()

        self._layout_direction = LayoutDirectionEnum.HORIZONTAL.value

        self._pipe_layout = PipeLayoutEnum.CURVED.value
        self._detached_port = None
        self._start_port = None
        self._origin_pos = None
        self._previous_pos = QtCore.QPoint(int(self.width() / 2),
                                           int(self.height() / 2))
        self._prev_selection_nodes = []
        self._prev_selection_pipes = []
        self._node_positions = {}

        self._rubber_band = QtWidgets.QRubberBand(
            QtWidgets.QRubberBand.Rectangle, self
        )
        self._rubber_band.isActive = False

        text_color = QtGui.QColor(*tuple(map(
            lambda i, j: i - j, (255, 255, 255),
            ViewerEnum.BACKGROUND_COLOR.value
        )))
        text_color.setAlpha(50)
        self._cursor_text = QtWidgets.QGraphicsTextItem()
        self._cursor_text.setFlag(
            QtWidgets.QGraphicsTextItem.ItemIsSelectable, False
        )
        self._cursor_text.setDefaultTextColor(text_color)
        self._cursor_text.setZValue(Z_VAL_PIPE - 1)
        font = self._cursor_text.font()
        font.setPointSize(7)
        self._cursor_text.setFont(font)
        self.scene().addItem(self._cursor_text)

        self._LIVE_PIPE = LivePipeItem()
        self._LIVE_PIPE.setVisible(False)
        self.scene().addItem(self._LIVE_PIPE)

        self._SLICER_PIPE = SlicerPipeItem()
        self._SLICER_PIPE.setVisible(False)
        self.scene().addItem(self._SLICER_PIPE)

        self._search_widget = TabSearchMenuWidget()
        self._search_widget.search_submitted.connect(self._on_search_submitted)

        # workaround fix for shortcuts from the non-native menu.
        # actions don't seem to trigger so we create a hidden menu bar.
        self._ctx_menu_bar = QtWidgets.QMenuBar(self)
        self._ctx_menu_bar.setNativeMenuBar(False)
        # shortcuts don't work with "setVisibility(False)".
        self._ctx_menu_bar.setMaximumSize(0, 0)

        # context menus.
        self._ctx_graph_menu = BaseMenu('NodeGraph', self)
        self._ctx_node_menu = BaseMenu('Nodes', self)

        if undo_stack:
            self._undo_action = undo_stack.createUndoAction(self, '&Undo')
            self._redo_action = undo_stack.createRedoAction(self, '&Redo')
        else:
            self._undo_action = None
            self._redo_action = None

        self._build_context_menus()

        self.acyclic = True
        self.pipe_collision = False
        self.pipe_slicing = True

        self.LMB_state = False
        self.RMB_state = False
        self.MMB_state = False
        self.ALT_state = False
        self.CTRL_state = False
        self.SHIFT_state = False
        self.COLLIDING_state = False

        # connection constrains.
        # TODO: maybe this should be a reference to the graph model instead?
        self.accept_connection_types = None
        self.reject_connection_types = None

    def __repr__(self):
        return '<{}() object at {}>'.format(
            self.__class__.__name__, hex(id(self)))

    def focusInEvent(self, event):
        """
        Args:
            event (QtGui.QFocusEvent): focus event.
        """
        # workaround fix: Re-populate the QMenuBar so the QAction shotcuts don't
        #                 conflict with parent existing host app.
        self._ctx_menu_bar.addMenu(self._ctx_graph_menu)
        self._ctx_menu_bar.addMenu(self._ctx_node_menu)
        return super(NodeViewer, self).focusInEvent(event)

    def focusOutEvent(self, event):
        """
        Args:
            event (QtGui.QFocusEvent): focus event.
        """
        # workaround fix: Clear the QMenuBar so the QAction shotcuts don't
        #                 conflict with existing parent host app.
        self._ctx_menu_bar.clear()
        return super(NodeViewer, self).focusOutEvent(event)

    # --- private ---

    def _build_context_menus(self):
        """
        Build context menu for the node graph.
        """
        # "node context menu" disabled by default and enabled when a action
        # is added through the "NodesMenu" interface.
        self._ctx_node_menu.setDisabled(True)

        # add the base menus.
        self._ctx_menu_bar.addMenu(self._ctx_graph_menu)
        self._ctx_menu_bar.addMenu(self._ctx_node_menu)

        # setup the undo and redo actions.
        if self._undo_action and self._redo_action:
            self._undo_action.setShortcuts(QtGui.QKeySequence.Undo)
            self._redo_action.setShortcuts(QtGui.QKeySequence.Redo)
            if LooseVersion(QtCore.qVersion()) >= LooseVersion('5.10'):
                self._undo_action.setShortcutVisibleInContextMenu(True)
                self._redo_action.setShortcutVisibleInContextMenu(True)

            # undo & redo always at the top of the "node graph context menu".
            self._ctx_graph_menu.addAction(self._undo_action)
            self._ctx_graph_menu.addAction(self._redo_action)
            self._ctx_graph_menu.addSeparator()

    def _set_viewer_zoom(self, value, sensitivity=None, pos=None):
        """
        Sets the zoom level.

        Args:
            value (float): zoom factor.
            sensitivity (float): zoom sensitivity.
            pos (QtCore.QPoint): mapped position.
        """
        if pos:
            pos = self.mapToScene(pos)
        if sensitivity is None:
            scale = 1.001 ** value
            self.scale(scale, scale, pos)
            return

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
        self.scale(scale, scale, pos)

    def _set_viewer_pan(self, pos_x, pos_y):
        """
        Set the viewer in panning mode.

        Args:
            pos_x (float): x pos.
            pos_y (float): y pos.
        """
        self._scene_range.adjust(pos_x, pos_y, pos_x, pos_y)
        self._update_scene()

    def scale(self, sx, sy, pos=None):
        scale = [sx, sx]
        center = pos or self._scene_range.center()
        w = self._scene_range.width() / scale[0]
        h = self._scene_range.height() / scale[1]
        self._scene_range = QtCore.QRectF(
            center.x() - (center.x() - self._scene_range.left()) / scale[0],
            center.y() - (center.y() - self._scene_range.top()) / scale[1],
            w, h
        )
        self._update_scene()

    def _update_scene(self):
        """
        Redraw the scene.
        """
        self.setSceneRect(self._scene_range)
        self.fitInView(self._scene_range, QtCore.Qt.KeepAspectRatio)

    def _combined_rect(self, nodes):
        """
        Returns a QRectF with the combined size of the provided node items.

        Args:
            nodes (list[AbstractNodeItem]): list of node qgraphics items.

        Returns:
            QtCore.QRectF: combined rect
        """
        group = self.scene().createItemGroup(nodes)
        rect = group.boundingRect()
        self.scene().destroyItemGroup(group)
        return rect

    def _items_near(self, pos, item_type=None, width=20, height=20):
        """
        Filter node graph items from the specified position, width and
        height area.

        Args:
            pos (QtCore.QPoint): scene pos.
            item_type: filter item type. (optional)
            width (int): width area.
            height (int): height area.

        Returns:
            list: qgraphics items from the scene.
        """
        x, y = pos.x() - width, pos.y() - height
        rect = QtCore.QRectF(x, y, width, height)
        items = []
        excl = [self._LIVE_PIPE, self._SLICER_PIPE]
        for item in self.scene().items(rect):
            if item in excl:
                continue
            if not item_type or isinstance(item, item_type):
                items.append(item)
        return items

    def _on_search_submitted(self, node_type):
        """
        Slot function triggered when the ``TabSearchMenuWidget`` has
        submitted a search.

        This will emit the "search_triggered" signal and tell the parent node
        graph to create a new node object.

        Args:
            node_type (str): node type identifier.
        """
        pos = self.mapToScene(self._previous_pos)
        self.search_triggered.emit(node_type, (pos.x(), pos.y()))

    def _on_pipes_sliced(self, path):
        """
        Triggered when the slicer pipe is active

        Args:
            path (QtGui.QPainterPath): slicer path.
        """
        ports = []
        for i in self.scene().items(path):
            if isinstance(i, PipeItem) and i != self._LIVE_PIPE:
                if any([i.input_port.locked, i.output_port.locked]):
                    continue
                ports.append([i.input_port, i.output_port])
        self.connection_sliced.emit(ports)

    # --- reimplemented events ---

    def resizeEvent(self, event):
        w, h = self.size().width(), self.size().height()
        if 0 in [w, h]:
            self.resize(self._last_size)
        delta = max(w / self._last_size.width(), h / self._last_size.height())
        self._set_viewer_zoom(delta)
        self._last_size = self.size()
        super(NodeViewer, self).resizeEvent(event)

    def contextMenuEvent(self, event):
        self.RMB_state = False

        ctx_menu = None
        ctx_menus = self.context_menus()

        prompted_data = None, None

        if ctx_menus['nodes'].isEnabled():
            pos = self.mapToScene(self._previous_pos)
            items = self._items_near(pos)
            nodes = [i for i in items if isinstance(i, AbstractNodeItem)]
            if nodes:
                node = nodes[0]
                ctx_menu = ctx_menus['nodes'].get_menu(node.type_, node.id)
                if ctx_menu:
                    for action in ctx_menu.actions():
                        if not action.menu():
                            action.node_id = node.id
                    prompted_data = 'nodes', node.id

        if not ctx_menu:
            ctx_menu = ctx_menus['graph']
            prompted_data = 'graph', None

        if len(ctx_menu.actions()) > 0:
            if ctx_menu.isEnabled():
                self.context_menu_prompt.emit(
                    prompted_data[0], prompted_data[1]
                )
                ctx_menu.exec_(event.globalPos())
            else:
                return super(NodeViewer, self).contextMenuEvent(event)

        return super(NodeViewer, self).contextMenuEvent(event)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.LMB_state = True
        elif event.button() == QtCore.Qt.RightButton:
            self.RMB_state = True
        elif event.button() == QtCore.Qt.MiddleButton:
            self.MMB_state = True

        self._origin_pos = event.pos()
        self._previous_pos = event.pos()
        (self._prev_selection_nodes,
         self._prev_selection_pipes) = self.selected_items()

        # close tab search
        if self._search_widget.isVisible():
            self.tab_search_toggle()

        # cursor pos.
        map_pos = self.mapToScene(event.pos())

        # pipe slicer enabled.
        if self.pipe_slicing:
            slicer_mode = all([
                self.ALT_state, self.SHIFT_state, self.LMB_state
            ])
            if slicer_mode:
                self._SLICER_PIPE.draw_path(map_pos, map_pos)
                self._SLICER_PIPE.setVisible(True)
                return

        # pan mode.
        if self.ALT_state:
            return

        items = self._items_near(map_pos, None, 20, 20)
        pipes = []
        nodes = []
        backdrop = None
        for itm in items:
            if isinstance(itm, PipeItem):
                pipes.append(itm)
            elif isinstance(itm, AbstractNodeItem):
                if isinstance(itm, BackdropNodeItem):
                    backdrop = itm
                    continue
                nodes.append(itm)

        if nodes:
            self.MMB_state = False

        # record the node selection as "self.selected_nodes()" is not updated
        # here on the mouse press event.
        selection = set([])

        if self.LMB_state:
            # toggle extend node selection.
            if self.SHIFT_state:
                if items and backdrop == items[0]:
                    backdrop.selected = not backdrop.selected
                    if backdrop.selected:
                        selection.add(backdrop)
                    for n in backdrop.get_nodes():
                        n.selected = backdrop.selected
                        if backdrop.selected:
                            selection.add(n)
                else:
                    for node in nodes:
                        node.selected = not node.selected
                        if node.selected:
                            selection.add(node)
            # unselected nodes with the "ctrl" key.
            elif self.CTRL_state:
                if items and backdrop == items[0]:
                    backdrop.selected = False
                else:
                    for node in nodes:
                        node.selected = False
            # if no modifier keys then add to selection set.
            else:
                if backdrop:
                    selection.add(backdrop)
                    for n in backdrop.get_nodes():
                        selection.add(n)
                for node in nodes:
                    if node.selected:
                        selection.add(node)

        selection.update(self.selected_nodes())

        # update the recorded node positions.
        self._node_positions.update({n: n.xy_pos for n in selection})

        # show selection marquee.
        if self.LMB_state and not items:
            rect = QtCore.QRect(self._previous_pos, QtCore.QSize())
            rect = rect.normalized()
            map_rect = self.mapToScene(rect).boundingRect()
            self.scene().update(map_rect)
            self._rubber_band.setGeometry(rect)
            self._rubber_band.isActive = True

        # stop here so we don't select a node.
        # (ctrl modifier can be used for something else in future.)
        if self.CTRL_state:
            return

        # allow new live pipe with the shift modifier on port that allow
        # for multi connection.
        if self.SHIFT_state:
            if pipes:
                pipes[0].reset()
                port = pipes[0].port_from_pos(map_pos, reverse=True)
                if not port.locked and port.multi_connection:
                    self._cursor_text.setPlainText('')
                    self._cursor_text.setVisible(False)
                    self.start_live_connection(port)

            # return here as the default behaviour unselects nodes with
            # the shift modifier.
            return

        if not self._LIVE_PIPE.isVisible():
            super(NodeViewer, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.LMB_state = False
        elif event.button() == QtCore.Qt.RightButton:
            self.RMB_state = False
        elif event.button() == QtCore.Qt.MiddleButton:
            self.MMB_state = False

        # hide pipe slicer.
        if self._SLICER_PIPE.isVisible():
            self._on_pipes_sliced(self._SLICER_PIPE.path())
            p = QtCore.QPointF(0.0, 0.0)
            self._SLICER_PIPE.draw_path(p, p)
            self._SLICER_PIPE.setVisible(False)

        # hide selection marquee
        if self._rubber_band.isActive:
            self._rubber_band.isActive = False
            if self._rubber_band.isVisible():
                rect = self._rubber_band.rect()
                map_rect = self.mapToScene(rect).boundingRect()
                self._rubber_band.hide()

                rect = QtCore.QRect(self._origin_pos, event.pos()).normalized()
                rect_items = self.scene().items(
                    self.mapToScene(rect).boundingRect()
                )
                node_ids = []
                for item in rect_items:
                    if isinstance(item, AbstractNodeItem):
                        node_ids.append(item.id)

                # emit the node selection signals.
                if node_ids:
                    prev_ids = [
                        n.id for n in self._prev_selection_nodes
                        if not n.selected
                    ]
                    self.node_selected.emit(node_ids[0])
                    self.node_selection_changed.emit(node_ids, prev_ids)

                self.scene().update(map_rect)
                return

        # find position changed nodes and emit signal.
        moved_nodes = {
            n: xy_pos for n, xy_pos in self._node_positions.items()
            if n.xy_pos != xy_pos
        }
        # only emit of node is not colliding with a pipe.
        if moved_nodes and not self.COLLIDING_state:
            self.moved_nodes.emit(moved_nodes)

        # reset recorded positions.
        self._node_positions = {}

        # emit signal if selected node collides with pipe.
        # Note: if collide state is true then only 1 node is selected.
        nodes, pipes = self.selected_items()
        if self.COLLIDING_state and nodes and pipes:
            self.insert_node.emit(pipes[0], nodes[0].id, moved_nodes)

        # emit node selection changed signal.
        prev_ids = [n.id for n in self._prev_selection_nodes if not n.selected]
        node_ids = [n.id for n in nodes if n not in self._prev_selection_nodes]
        self.node_selection_changed.emit(node_ids, prev_ids)

        super(NodeViewer, self).mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        if self.ALT_state and self.SHIFT_state:
            if self.pipe_slicing:
                if self.LMB_state and self._SLICER_PIPE.isVisible():
                    p1 = self._SLICER_PIPE.path().pointAtPercent(0)
                    p2 = self.mapToScene(self._previous_pos)
                    self._SLICER_PIPE.draw_path(p1, p2)
                    self._SLICER_PIPE.show()
            self._previous_pos = event.pos()
            super(NodeViewer, self).mouseMoveEvent(event)
            return

        if self.MMB_state and self.ALT_state:
            pos_x = (event.x() - self._previous_pos.x())
            zoom = 0.1 if pos_x > 0 else -0.1
            self._set_viewer_zoom(zoom, 0.05, pos=event.pos())
        elif self.MMB_state or (self.LMB_state and self.ALT_state):
            previous_pos = self.mapToScene(self._previous_pos)
            current_pos = self.mapToScene(event.pos())
            delta = previous_pos - current_pos
            self._set_viewer_pan(delta.x(), delta.y())

        if not self.ALT_state:
            if self.SHIFT_state or self.CTRL_state:
                if not self._LIVE_PIPE.isVisible():
                    self._cursor_text.setPos(self.mapToScene(event.pos()))

        if self.LMB_state and self._rubber_band.isActive:
            rect = QtCore.QRect(self._origin_pos, event.pos()).normalized()
            # if the rubber band is too small, do not show it.
            if max(rect.width(), rect.height()) > 5:
                if not self._rubber_band.isVisible():
                    self._rubber_band.show()
                map_rect = self.mapToScene(rect).boundingRect()
                path = QtGui.QPainterPath()
                path.addRect(map_rect)
                self._rubber_band.setGeometry(rect)
                self.scene().setSelectionArea(path)
                self.scene().update(map_rect)

                if self.SHIFT_state or self.CTRL_state:
                    nodes, pipes = self.selected_items()

                    for node in self._prev_selection_nodes:
                        node.selected = True

                    if self.CTRL_state:
                        for pipe in pipes:
                            pipe.setSelected(False)
                        for node in nodes:
                            node.selected = False

        elif self.LMB_state:
            self.COLLIDING_state = False
            nodes, pipes = self.selected_items()
            if len(nodes) == 1:
                node = nodes[0]
                [p.setSelected(False) for p in pipes]

                if self.pipe_collision:
                    colliding_pipes = [
                        i for i in node.collidingItems()
                        if isinstance(i, PipeItem) and i.isVisible()
                    ]
                    for pipe in colliding_pipes:
                        if not pipe.input_port:
                            continue
                        port_node_check = all([
                            not pipe.input_port.node is node,
                            not pipe.output_port.node is node
                        ])
                        if port_node_check:
                            pipe.setSelected(True)
                            self.COLLIDING_state = True
                            break

        self._previous_pos = event.pos()
        super(NodeViewer, self).mouseMoveEvent(event)

    def wheelEvent(self, event):
        try:
            delta = event.delta()
        except AttributeError:
            # For PyQt5
            delta = event.angleDelta().y()
            if delta == 0:
                delta = event.angleDelta().x()
        try:
            self._set_viewer_zoom(delta, pos=event.pos())
        except AttributeError:
            # For PyQt5 and above
            self._set_viewer_zoom(delta, pos=event.position().toPoint())

    def dropEvent(self, event):
        pos = self.mapToScene(event.pos())
        event.setDropAction(QtCore.Qt.CopyAction)
        self.data_dropped.emit(
            event.mimeData(), QtCore.QPoint(int(pos.x()), int(pos.y()))
        )

    def dragEnterEvent(self, event):
        is_acceptable = any([
            event.mimeData().hasFormat(i) for i in
            ['nodegraphqt/nodes', 'text/plain', 'text/uri-list']
        ])
        if is_acceptable:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        is_acceptable = any([
            event.mimeData().hasFormat(i) for i in
            ['nodegraphqt/nodes', 'text/plain', 'text/uri-list']
        ])
        if is_acceptable:
            event.accept()
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        event.ignore()

    def keyPressEvent(self, event):
        """
        Key press event re-implemented to update the states for attributes:
        - ALT_state
        - CTRL_state
        - SHIFT_state

        Args:
            event (QtGui.QKeyEvent): key event.
        """
        self.ALT_state = event.modifiers() == QtCore.Qt.AltModifier
        self.CTRL_state = event.modifiers() == QtCore.Qt.ControlModifier
        self.SHIFT_state = event.modifiers() == QtCore.Qt.ShiftModifier

        # Todo: find a better solution to catch modifier keys.
        if event.modifiers() == (QtCore.Qt.AltModifier | QtCore.Qt.ShiftModifier):
            self.ALT_state = True
            self.SHIFT_state = True

        if self._LIVE_PIPE.isVisible():
            super(NodeViewer, self).keyPressEvent(event)
            return

        # show cursor text
        overlay_text = None
        self._cursor_text.setVisible(False)
        if not self.ALT_state:
            if self.SHIFT_state:
                overlay_text = '\n    SHIFT:\n    Toggle/Extend Selection'
            elif self.CTRL_state:
                overlay_text = '\n    CTRL:\n    Deselect Nodes'
        elif self.ALT_state and self.SHIFT_state:
            if self.pipe_slicing:
                overlay_text = '\n    ALT + SHIFT:\n    Pipe Slicer Enabled'
        if overlay_text:
            self._cursor_text.setPlainText(overlay_text)
            self._cursor_text.setPos(self.mapToScene(self._previous_pos))
            self._cursor_text.setVisible(True)

        super(NodeViewer, self).keyPressEvent(event)

    def keyReleaseEvent(self, event):
        """
        Key release event re-implemented to update the states for attributes:
        - ALT_state
        - CTRL_state
        - SHIFT_state

        Args:
            event (QtGui.QKeyEvent): key event.
        """
        self.ALT_state = event.modifiers() == QtCore.Qt.AltModifier
        self.CTRL_state = event.modifiers() == QtCore.Qt.ControlModifier
        self.SHIFT_state = event.modifiers() == QtCore.Qt.ShiftModifier
        super(NodeViewer, self).keyReleaseEvent(event)

        # hide and reset cursor text.
        self._cursor_text.setPlainText('')
        self._cursor_text.setVisible(False)

    # --- scene events ---

    def sceneMouseMoveEvent(self, event):
        """
        triggered mouse move event for the scene.
         - redraw the live connection pipe.

        Args:
            event (QtWidgets.QGraphicsSceneMouseEvent):
                The event handler from the QtWidgets.QGraphicsScene
        """
        if not self._LIVE_PIPE.isVisible():
            return
        if not self._start_port:
            return

        pos = event.scenePos()
        pointer_color = None
        for item in self.scene().items(pos):
            if not isinstance(item, PortItem):
                continue

            x = item.boundingRect().width() / 2
            y = item.boundingRect().height() / 2
            pos = item.scenePos()
            pos.setX(pos.x() + x)
            pos.setY(pos.y() + y)
            if item == self._start_port:
                break
            pointer_color = PipeEnum.HIGHLIGHT_COLOR.value
            accept = self._validate_accept_connection(self._start_port, item)
            if not accept:
                pointer_color = [150, 60, 255]
                break
            reject = self._validate_reject_connection(self._start_port, item)
            if reject:
                pointer_color = [150, 60, 255]
                break

            if self.acyclic:
                if item.node == self._start_port.node:
                    pointer_color = PipeEnum.DISABLED_COLOR.value
                elif item.port_type == self._start_port.port_type:
                    pointer_color = PipeEnum.DISABLED_COLOR.value
            break

        self._LIVE_PIPE.draw_path(
            self._start_port, cursor_pos=pos, color=pointer_color
        )

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
        if self.ALT_state and self.SHIFT_state:
            return

        # viewer pan mode.
        if self.ALT_state:
            return

        if self._LIVE_PIPE.isVisible():
            self.apply_live_connection(event)
            return

        pos = event.scenePos()
        items = self._items_near(pos, None, 5, 5)

        # filter from the selection stack in the following order
        # "node, port, pipe" this is to avoid selecting items under items.
        node, port, pipe = None, None, None
        for item in items:
            if isinstance(item, AbstractNodeItem):
                node = item
            elif isinstance(item, PortItem):
                port = item
            elif isinstance(item, PipeItem):
                pipe = item
            if any([node, port, pipe]):
                break

        if port:
            if port.locked:
                return

            if not port.multi_connection and port.connected_ports:
                self._detached_port = port.connected_ports[0]
            self.start_live_connection(port)
            if not port.multi_connection:
                [p.delete() for p in port.connected_pipes]
            return

        if node:
            node_items = self._items_near(pos, AbstractNodeItem, 3, 3)

            # record the node positions at selection time.
            for n in node_items:
                self._node_positions[n] = n.xy_pos

            # emit selected node id with LMB.
            if event.button() == QtCore.Qt.LeftButton:
                self.node_selected.emit(node.id)

            if not isinstance(node, BackdropNodeItem):
                return

        if pipe:
            if not self.LMB_state:
                return

            from_port = pipe.port_from_pos(pos, True)

            if from_port.locked:
                return

            from_port.hovered = True

            attr = {
                PortTypeEnum.IN.value: 'output_port',
                PortTypeEnum.OUT.value: 'input_port'
            }
            self._detached_port = getattr(pipe, attr[from_port.port_type])
            self.start_live_connection(from_port)
            self._LIVE_PIPE.draw_path(self._start_port, cursor_pos=pos)

            if self.SHIFT_state:
                self._LIVE_PIPE.shift_selected = True
                return

            pipe.delete()

    def sceneMouseReleaseEvent(self, event):
        """
        triggered mouse release event for the scene.

        Args:
            event (QtWidgets.QGraphicsSceneMouseEvent):
                The event handler from the QtWidgets.QGraphicsScene
        """
        if event.button() != QtCore.Qt.MiddleButton:
            self.apply_live_connection(event)

    # --- port connections ---

    def _validate_accept_connection(self, from_port, to_port):
        """
        Check if a pipe connection is allowed if there are a constraints set
        on the ports.

        Args:
            from_port (PortItem):
            to_port (PortItem):

        Returns:
            bool: true to allow connection.
        """
        accept_validation = []

        to_ptype = to_port.port_type
        from_ptype = from_port.port_type

        # validate the start.
        from_data = self.accept_connection_types.get(from_port.node.type_) or {}
        constraints = from_data.get(from_ptype, {}).get(from_port.name, {})
        accept_data = constraints.get(to_port.node.type_, {})
        accepted_pnames = accept_data.get(to_ptype, {})
        if constraints:
            if to_port.name in accepted_pnames:
                accept_validation.append(True)
            else:
                accept_validation.append(False)

        # validate the end.
        to_data = self.accept_connection_types.get(to_port.node.type_) or {}
        constraints = to_data.get(to_ptype, {}).get(to_port.name, {})
        accept_data = constraints.get(from_port.node.type_, {})
        accepted_pnames = accept_data.get(from_ptype, {})
        if constraints:
            if from_port.name in accepted_pnames:
                accept_validation.append(True)
            else:
                accept_validation.append(False)

        if False in accept_validation:
            return False
        return True

    def _validate_reject_connection(self, from_port, to_port):
        """
        Check if a pipe connection is NOT allowed if there are a constrains set
        on the ports.

        Args:
            from_port (PortItem):
            to_port (PortItem):

        Returns:
            bool: true to reject connection.
        """
        to_ptype = to_port.port_type
        from_ptype = from_port.port_type

        to_data = self.reject_connection_types.get(to_port.node.type_) or {}
        constraints = to_data.get(to_ptype, {}).get(to_port.name, {})
        reject_data = constraints.get(from_port.node.type_, {})

        rejected_pnames = reject_data.get(from_ptype)
        if rejected_pnames:
            if from_port.name in rejected_pnames:
                return True
            return False

        from_data = self.reject_connection_types.get(from_port.node.type_) or {}
        constraints = from_data.get(from_ptype, {}).get(from_port.name, {})
        reject_data = constraints.get(to_port.node.type_, {})

        rejected_pnames = reject_data.get(to_ptype)
        if rejected_pnames:
            if to_port.name in rejected_pnames:
                return True
            return False
        return False

    def apply_live_connection(self, event):
        """
        triggered mouse press/release event for the scene.
        - verifies the live connection pipe.
        - makes a connection pipe if valid.
        - emits the "connection changed" signal.

        Args:
            event (QtWidgets.QGraphicsSceneMouseEvent):
                The event handler from the QtWidgets.QGraphicsScene
        """
        if not self._LIVE_PIPE.isVisible():
            return

        self._start_port.hovered = False

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
            if self._detached_port and not self._LIVE_PIPE.shift_selected:
                dist = math.hypot(self._previous_pos.x() - self._origin_pos.x(),
                                  self._previous_pos.y() - self._origin_pos.y())
                if dist <= 2.0:  # cursor pos threshold.
                    self.establish_connection(self._start_port,
                                              self._detached_port)
                    self._detached_port = None
                else:
                    disconnected.append((self._start_port, self._detached_port))
                    self.connection_changed.emit(disconnected, connected)

            self._detached_port = None
            self.end_live_connection()
            return

        else:
            if self._start_port is end_port:
                return

        # if connection to itself
        same_node_connection = end_port.node == self._start_port.node
        if not self.acyclic:
            # allow a node cycle connection.
            same_node_connection = False

        # constrain check
        accept_connection = self._validate_accept_connection(
            self._start_port, end_port
        )
        reject_connection = self._validate_reject_connection(
            self._start_port, end_port
        )

        # restore connection check.
        restore_connection = any([
            # if the end port is locked.
            end_port.locked,
            # if same port type.
            end_port.port_type == self._start_port.port_type,
            # if connection to itself.
            same_node_connection,
            # if end port is the start port.
            end_port == self._start_port,
            # if detached port is the end port.
            self._detached_port == end_port,
            # if a port has a accept port type constrain.
            not accept_connection,
            # if a port has a reject port type constrain.
            reject_connection
        ])
        if restore_connection:
            if self._detached_port:
                to_port = self._detached_port or end_port
                self.establish_connection(self._start_port, to_port)
                self._detached_port = None
            self.end_live_connection()
            return

        # end connection if starting port is already connected.
        if self._start_port.multi_connection and \
                self._start_port in end_port.connected_ports:
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

    def start_live_connection(self, selected_port):
        """
        create new pipe for the connection.
        (show the live pipe visibility from the port following the cursor position)
        """
        if not selected_port:
            return
        self._start_port = selected_port
        if self._start_port.type == PortTypeEnum.IN.value:
            self._LIVE_PIPE.input_port = self._start_port
        elif self._start_port == PortTypeEnum.OUT.value:
            self._LIVE_PIPE.output_port = self._start_port
        self._LIVE_PIPE.setVisible(True)
        self._LIVE_PIPE.draw_index_pointer(
            selected_port,
            self.mapToScene(self._origin_pos)
        )

    def end_live_connection(self):
        """
        delete live connection pipe and reset start port.
        (hides the pipe item used for drawing the live connection)
        """
        self._LIVE_PIPE.reset_path()
        self._LIVE_PIPE.setVisible(False)
        self._LIVE_PIPE.shift_selected = False
        self._start_port = None

    def establish_connection(self, start_port, end_port):
        """
        establish a new pipe connection.
        (adds a new pipe item to draw between 2 ports)
        """
        pipe = PipeItem()
        self.scene().addItem(pipe)
        pipe.set_connections(start_port, end_port)
        pipe.draw_path(pipe.input_port, pipe.output_port)
        if start_port.node.selected or end_port.node.selected:
            pipe.highlight()
        if not start_port.node.visible or not end_port.node.visible:
            pipe.hide()

    @staticmethod
    def acyclic_check(start_port, end_port):
        """
        Validate the node connections, so it doesn't loop itself.

        Args:
            start_port (PortItem): port item.
            end_port (PortItem): port item.

        Returns:
            bool: True if port connection is valid.
        """
        start_node = start_port.node
        check_nodes = [end_port.node]
        io_types = {
            PortTypeEnum.IN.value: 'outputs',
            PortTypeEnum.OUT.value: 'inputs'
        }
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
        state = self._search_widget.isVisible()
        if not state:
            self._search_widget.setVisible(state)
            self.setFocus()
            return

        pos = self._previous_pos
        rect = self._search_widget.rect()
        new_pos = QtCore.QPoint(int(pos.x() - rect.width() / 2),
                                int(pos.y() - rect.height() / 2))
        self._search_widget.move(new_pos)
        self._search_widget.setVisible(state)
        self._search_widget.setFocus()

        rect = self.mapToScene(rect).boundingRect()
        self.scene().update(rect)

    def rebuild_tab_search(self):
        if isinstance(self._search_widget, TabSearchMenuWidget):
            self._search_widget.rebuild = True

    def qaction_for_undo(self):
        """
        Get the undo QAction from the parent undo stack.

        Returns:
            QtWidgets.QAction: undo action.
        """
        return self._undo_action

    def qaction_for_redo(self):
        """
        Get the redo QAction from the parent undo stack.

        Returns:
            QtWidgets.QAction: redo action.
        """
        return self._redo_action

    def context_menus(self):
        """
        All the available context menus for the viewer.

        Returns:
            dict: viewer context menu.
        """
        return {'graph': self._ctx_graph_menu, 'nodes': self._ctx_node_menu}

    def question_dialog(self, text, title='Node Graph', dialog_icon=None,
                        custom_icon=None, parent=None):
        """
        Prompt node viewer question dialog widget with "yes", "no" buttons.

        Args:
            text (str): dialog text.
            title (str): dialog window title.
            dialog_icon (str): display icon. ("information", "warning", "critical")
            custom_icon (str): custom icon to display.
            parent (QtWidgets.QObject): override dialog parent. (optional)

        Returns:
            bool: true if user click yes.
        """
        parent = parent or self

        self.clear_key_state()
        return BaseDialog.question_dialog(
            parent, text, title, dialog_icon, custom_icon
        )

    def message_dialog(self, text, title='Node Graph', dialog_icon=None,
                       custom_icon=None, parent=None):
        """
        Prompt node viewer message dialog widget with "ok" button.

        Args:
            text (str): dialog text.
            title (str): dialog window title.
            dialog_icon (str): display icon. ("information", "warning", "critical")
            custom_icon (str): custom icon to display.
            parent (QtWidgets.QObject): override dialog parent. (optional)
        """
        parent = parent or self

        self.clear_key_state()
        BaseDialog.message_dialog(parent, text, title, dialog_icon, custom_icon)

    def load_dialog(self, current_dir=None, ext=None, parent=None):
        """
        Prompt node viewer file load dialog widget.

        Args:
            current_dir (str): directory path starting point. (optional)
            ext (str): custom file extension filter type. (optional)
            parent (QtWidgets.QObject): override dialog parent. (optional)

        Returns:
            str: selected file path.
        """
        parent = parent or self

        self.clear_key_state()
        ext = '*{} '.format(ext) if ext else ''
        ext_filter = ';;'.join([
            'Node Graph ({}*json)'.format(ext), 'All Files (*)'
        ])
        file_dlg = FileDialog.getOpenFileName(
            parent, 'Open File', current_dir, ext_filter)
        file = file_dlg[0] or None
        return file

    def save_dialog(self, current_dir=None, ext=None, parent=None):
        """
        Prompt node viewer file save dialog widget.

        Args:
            current_dir (str): directory path starting point. (optional)
            ext (str): custom file extension filter type. (optional)
            parent (QtWidgets.QObject): override dialog parent. (optional)

        Returns:
            str: selected file path.
        """
        parent = parent or self

        self.clear_key_state()
        ext_label = '*{} '.format(ext) if ext else ''
        ext_type = '.{}'.format(ext) if ext else '.json'
        ext_map = {'Node Graph ({}*json)'.format(ext_label): ext_type,
                   'All Files (*)': ''}
        file_dlg = FileDialog.getSaveFileName(
            parent, 'Save Session', current_dir, ';;'.join(ext_map.keys()))
        file_path = file_dlg[0]
        if not file_path:
            return
        ext = ext_map[file_dlg[1]]
        if ext and not file_path.endswith(ext):
            file_path += ext

        return file_path

    def all_pipes(self):
        """
        Returns all pipe qgraphic items.

        Returns:
            list[PipeItem]: instances of pipe items.
        """
        excl = [self._LIVE_PIPE, self._SLICER_PIPE]
        return [i for i in self.scene().items()
                if isinstance(i, PipeItem) and i not in excl]

    def all_nodes(self):
        """
        Returns all node qgraphic items.

        Returns:
            list[AbstractNodeItem]: instances of node items.
        """
        return [i for i in self.scene().items()
                if isinstance(i, AbstractNodeItem)]

    def selected_nodes(self):
        """
        Returns selected node qgraphic items.

        Returns:
            list[AbstractNodeItem]: instances of node items.
        """
        return [i for i in self.scene().selectedItems()
                if isinstance(i, AbstractNodeItem)]

    def selected_pipes(self):
        """
        Returns selected pipe qgraphic items.

        Returns:
            list[Pipe]: pipe items.
        """
        pipes = [i for i in self.scene().selectedItems()
                 if isinstance(i, PipeItem)]
        return pipes

    def selected_items(self):
        """
        Return selected graphic items in the scene.

        Returns:
            tuple(list[AbstractNodeItem], list[Pipe]):
                selected (node items, pipe items).
        """
        nodes = []
        pipes = []
        for item in self.scene().selectedItems():
            if isinstance(item, AbstractNodeItem):
                nodes.append(item)
            elif isinstance(item, PipeItem):
                pipes.append(item)
        return nodes, pipes

    def add_node(self, node, pos=None):
        """
        Add node item into the scene.

        Args:
            node (AbstractNodeItem): node item instance.
            pos (tuple or list): node scene position.
        """
        pos = pos or (self._previous_pos.x(), self._previous_pos.y())
        node.pre_init(self, pos)
        self.scene().addItem(node)
        node.post_init(self, pos)

    @staticmethod
    def remove_node(node):
        """
        Remove node item from the scene.

        Args:
            node (AbstractNodeItem): node item instance.
        """
        if isinstance(node, AbstractNodeItem):
            node.delete()

    def move_nodes(self, nodes, pos=None, offset=None):
        """
        Globally move specified nodes.

        Args:
            nodes (list[AbstractNodeItem]): node items.
            pos (tuple or list): custom x, y position.
            offset (tuple or list): x, y position offset.
        """
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
        """
        Center on the given nodes or all nodes by default.

        Args:
            nodes (list[AbstractNodeItem]): a list of node items.
        """
        if not nodes:
            if self.selected_nodes():
                nodes = self.selected_nodes()
            elif self.all_nodes():
                nodes = self.all_nodes()
            if not nodes:
                return

        rect = self._combined_rect(nodes)
        self._scene_range.translate(rect.center() - self._scene_range.center())
        self.setSceneRect(self._scene_range)

    def get_pipe_layout(self):
        """
        Returns the pipe layout mode.

        Returns:
            int: pipe layout mode.
        """
        return self._pipe_layout

    def set_pipe_layout(self, layout):
        """
        Sets the pipe layout mode and redraw all pipe items in the scene.

        Args:
            layout (int): pipe layout mode. (see the constants module)
        """
        self._pipe_layout = layout
        for pipe in self.all_pipes():
            pipe.draw_path(pipe.input_port, pipe.output_port)

    def get_layout_direction(self):
        """
        Returns the layout direction set on the node graph viewer
        used by the pipe items for drawing.

        Returns:
            int: graph layout mode.
        """
        return self._layout_direction

    def set_layout_direction(self, direction):
        """
        Sets the node graph viewer layout direction for re-drawing
        the pipe items.

        Args:
            direction (int): graph layout direction.
        """
        self._layout_direction = direction
        for pipe_item in self.all_pipes():
            pipe_item.draw_path(pipe_item.input_port, pipe_item.output_port)

    def reset_zoom(self, cent=None):
        """
        Reset the viewer zoom level.

        Args:
            cent (QtCore.QPoint): specified center.
        """
        self._scene_range = QtCore.QRectF(0, 0,
                                          self.size().width(),
                                          self.size().height())
        if cent:
            self._scene_range.translate(cent - self._scene_range.center())
        self._update_scene()

    def get_zoom(self):
        """
        Returns the viewer zoom level.

        Returns:
            float: zoom level.
        """
        transform = self.transform()
        cur_scale = (transform.m11(), transform.m22())
        return float('{:0.2f}'.format(cur_scale[0] - 1.0))

    def set_zoom(self, value=0.0):
        """
        Set the viewer zoom level.

        Args:
            value (float): zoom level
        """
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
        self._set_viewer_zoom(value, 0.0)

    def zoom_to_nodes(self, nodes):
        self._scene_range = self._combined_rect(nodes)
        self._update_scene()

        if self.get_zoom() > 0.1:
            self.reset_zoom(self._scene_range.center())

    def force_update(self):
        """
        Redraw the current node graph scene.
        """
        self._update_scene()

    def scene_rect(self):
        """
        Returns the scene rect size.

        Returns:
            list[float]: x, y, width, height
        """
        return [self._scene_range.x(), self._scene_range.y(),
                self._scene_range.width(), self._scene_range.height()]

    def set_scene_rect(self, rect):
        """
        Sets the scene rect and redraws the scene.

        Args:
            rect (list[float]): x, y, width, height
        """
        self._scene_range = QtCore.QRectF(*rect)
        self._update_scene()

    def scene_center(self):
        """
        Get the center x,y pos from the scene.

        Returns:
            list[float]: x, y position.
        """
        cent = self._scene_range.center()
        return [cent.x(), cent.y()]

    def scene_cursor_pos(self):
        """
        Returns the cursor last position mapped to the scene.

        Returns:
            QtCore.QPoint: cursor position.
        """
        return self.mapToScene(self._previous_pos)

    def nodes_rect_center(self, nodes):
        """
        Get the center x,y pos from the specified nodes.

        Args:
            nodes (list[AbstractNodeItem]): list of node qgrphics items.

        Returns:
            list[float]: x, y position.
        """
        cent = self._combined_rect(nodes).center()
        return [cent.x(), cent.y()]

    def clear_key_state(self):
        """
        Resets the Ctrl, Shift, Alt modifiers key states.
        """
        self.CTRL_state = False
        self.SHIFT_state = False
        self.ALT_state = False

    def use_OpenGL(self):
        """
        Use QOpenGLWidget as the viewer.
        """
        # use QOpenGLWidget instead of the deprecated QGLWidget to avoid
        # problems with Wayland.
        import Qt
        if Qt.IsPySide2:
            from PySide2.QtWidgets import QOpenGLWidget
        elif Qt.IsPyQt5:
            from PyQt5.QtWidgets import QOpenGLWidget
        self.setViewport(QOpenGLWidget())
