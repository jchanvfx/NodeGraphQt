#!/usr/bin/python
# -*- coding: utf-8 -*-
import copy
import gc
import json
import os
import re

from Qt import QtCore, QtWidgets, QtGui

from .commands import (NodeAddedCmd,
                       NodeRemovedCmd,
                       NodeMovedCmd,
                       PortConnectedCmd)
from .factory import NodeFactory
from .menu import NodeGraphMenu, NodesMenu
from .model import NodeGraphModel
from .node import NodeObject, BackdropNode, BaseNode
from .port import Port
from ..constants import (
    URI_SCHEME, URN_SCHEME,
    NODE_LAYOUT_DIRECTION, NODE_LAYOUT_HORIZONTAL, NODE_LAYOUT_VERTICAL,
    PIPE_LAYOUT_CURVED, PIPE_LAYOUT_STRAIGHT, PIPE_LAYOUT_ANGLE,
    IN_PORT, OUT_PORT,
    VIEWER_GRID_LINES
)
from ..widgets.node_space_bar import node_space_bar
from ..widgets.viewer import NodeViewer


class NodeGraph(QtCore.QObject):
    """
    The ``NodeGraph`` class is the main controller for managing all nodes
    and the node graph.

    Inherited from: :class:`PySide2.QtCore.QObject`

    .. image:: _images/graph.png
        :width: 60%
    """

    node_created = QtCore.Signal(NodeObject)
    """
    Signal triggered when a node is created in the node graph.

    :parameters: :class:`NodeGraphQt.NodeObject`
    :emits: created node
    """
    nodes_deleted = QtCore.Signal(list)
    """
    Signal triggered when nodes have been deleted from the node graph.

    :parameters: list[str]
    :emits: list of deleted node ids.
    """
    node_selected = QtCore.Signal(NodeObject)
    """
    Signal triggered when a node is clicked with the LMB.

    :parameters: :class:`NodeGraphQt.NodeObject`
    :emits: selected node
    """
    node_selection_changed = QtCore.Signal(list, list)
    """
    Signal triggered when the node selection has changed.

    :parameters: list[:class:`NodeGraphQt.NodeObject`],
                 list[:class:`NodeGraphQt.NodeObject`]
    :emits: selected node, deselected nodes.
    """
    node_double_clicked = QtCore.Signal(NodeObject)
    """
    Signal triggered when a node is double clicked and emits the node.

    :parameters: :class:`NodeGraphQt.NodeObject`
    :emits: selected node
    """
    port_connected = QtCore.Signal(Port, Port)
    """
    Signal triggered when a node port has been connected.

    :parameters: :class:`NodeGraphQt.Port`, :class:`NodeGraphQt.Port`
    :emits: input port, output port
    """
    port_disconnected = QtCore.Signal(Port, Port)
    """
    Signal triggered when a node port has been disconnected.

    :parameters: :class:`NodeGraphQt.Port`, :class:`NodeGraphQt.Port`
    :emits: input port, output port
    """
    property_changed = QtCore.Signal(NodeObject, str, object)
    """
    Signal is triggered when a property has changed on a node.

    :parameters: :class:`NodeGraphQt.BaseNode`, str, object
    :emits: triggered node, property name, property value
    """
    data_dropped = QtCore.Signal(QtCore.QMimeData, QtCore.QPoint)
    """
    Signal is triggered when data has been dropped to the graph.

    :parameters: :class:`PySide2.QtCore.QMimeData`, :class:`PySide2.QtCore.QPoint`
    :emits: mime data, node graph position
    """
    session_changed = QtCore.Signal(str)
    """
    Signal is triggered when session has been changed.

    :parameters: :str
    :emits: new session path
    """

    def __init__(self, parent=None):
        super(NodeGraph, self).__init__(parent)
        self.setObjectName('NodeGraphQt')
        self._widget = None
        self._undo_view = None
        self._model = NodeGraphModel()
        self._viewer = NodeViewer()
        self._node_factory = NodeFactory()
        self._undo_stack = QtWidgets.QUndoStack(self)
        self._current_node_space = None
        self._editable = True

        self._wire_signals()
        self._node_space_bar = node_space_bar(self)
        self._auto_update = True

    def __repr__(self):
        return '<{} object at {}>'.format(
            self.__class__.__name__, hex(id(self)))

    def _wire_signals(self):
        """
        Connect up all the signals and slots here.
        """
        # hard coded tab search.
        tab = QtWidgets.QShortcut(
            QtGui.QKeySequence(QtCore.Qt.Key_Tab), self._viewer)
        tab.activated.connect(self._toggle_tab_search)
        self._viewer.need_show_tab_search.connect(self._toggle_tab_search)

        # internal signals.
        self._viewer.search_triggered.connect(self._on_search_triggered)
        self._viewer.connection_sliced.connect(self._on_connection_sliced)
        self._viewer.connection_changed.connect(self._on_connection_changed)
        self._viewer.moved_nodes.connect(self._on_nodes_moved)
        self._viewer.node_double_clicked.connect(self._on_node_double_clicked)
        self._viewer.node_name_changed.connect(self._on_node_name_changed)
        self._viewer.node_backdrop_updated.connect(
            self._on_node_backdrop_updated)
        self._viewer.insert_node.connect(self._on_insert_node)

        # pass through translated signals.
        self._viewer.node_selected.connect(self._on_node_selected)
        self._viewer.node_selection_changed.connect(
            self._on_node_selection_changed)
        self._viewer.data_dropped.connect(self._on_node_data_dropped)

    def _on_insert_node(self, pipe, node_id, prev_node_pos):
        """
        Slot function triggered when a selected node has collided with a pipe.

        Args:
            pipe (Pipe): collided pipe item.
            node_id (str): selected node id to insert.
            prev_node_pos (dict): previous node position. {NodeItem: [prev_x, prev_y]}
        """
        if not self._editable:
            return
        node = self.get_node_by_id(node_id)

        # exclude if not a BaseNode
        if not isinstance(node, BaseNode):
            return

        disconnected = [(pipe.input_port, pipe.output_port)]
        connected = []

        if node.input_ports():
            connected.append(
                (pipe.output_port, node.input_ports()[0].view)
            )
        if node.output_ports():
            connected.append(
                (node.output_ports()[0].view, pipe.input_port)
            )

        self._undo_stack.beginMacro('inserted node')
        self._on_connection_changed(disconnected, connected)
        self._on_nodes_moved(prev_node_pos)
        self._undo_stack.endMacro()

    def _toggle_tab_search(self):
        """
        toggle the tab search widget.
        """
        if not self._editable:
            return
        if self._viewer.underMouse():
            self._viewer.tab_search_set_nodes(self._node_factory.names)
            self._viewer.tab_search_toggle()

    def _on_property_bin_changed(self, node_id, prop_name, prop_value):
        """
        called when a property widget has changed in a properties bin.
        (emits the node object, property name, property value)

        Args:
            node_id (str): node id.
            prop_name (str): node property name.
            prop_value (object): python built in types.
        """
        if not self._editable:
            return
        node = self.get_node_by_id(node_id)

        # prevent signals from causing a infinite loop.
        _exc = [float, int, str, bool, None]
        if node.get_property(prop_name) != prop_value:
            if type(node.get_property(prop_name)) in _exc:
                value = prop_value
            else:
                value = copy.deepcopy(prop_value)
            node.set_property(prop_name, value)

    def _on_node_name_changed(self, node_id, name):
        """
        called when a node text qgraphics item in the viewer is edited.
        (sets the name through the node object so undo commands are registered.)

        Args:
            node_id (str): node id emitted by the viewer.
            name (str): new node name.
        """
        node = self.get_node_by_id(node_id)
        node.set_name(name)

        # TODO: not sure about redrawing the node here.
        node.view.draw_node()

    def _on_node_double_clicked(self, node_id):
        """
        called when a node in the viewer is double click.
        (emits the node object when the node is clicked)

        Args:
            node_id (str): node id emitted by the viewer.
        """
        node = self.get_node_by_id(node_id)
        self.node_double_clicked.emit(node)
        if isinstance(node, SubGraph):
            self.set_node_space(node)

    def _on_node_selected(self, node_id):
        """
        called when a node in the viewer is selected on left click.
        (emits the node object when the node is clicked)

        Args:
            node_id (str): node id emitted by the viewer.
        """
        node = self.get_node_by_id(node_id)
        self.node_selected.emit(node)

    def _on_node_selection_changed(self, sel_ids, desel_ids):
        """
        called when the node selection changes in the viewer.
        (emits node objects <selected nodes>, <deselected nodes>)

        Args:
            sel_ids (list[str]): new selected node ids.
            desel_ids (list[str]): deselected node ids.
        """
        sel_nodes = [self.get_node_by_id(nid) for nid in sel_ids]
        unsel_nodes = [self.get_node_by_id(nid) for nid in desel_ids]
        self.node_selection_changed.emit(sel_nodes, unsel_nodes)

    def _on_node_data_dropped(self, data, pos):
        """
        called when data has been dropped on the viewer.

        Example Identifiers:
            URI = ngqt://path/to/node/session.graph
            URN = ngqt::node:com.nodes.MyNode1;node:com.nodes.MyNode2

        Args:
            data (QtCore.QMimeData): mime data.
            pos (QtCore.QPoint): scene position relative to the drop.
        """
        uri_regex = re.compile('{}(?:/*)([\w/]+)(\\.\w+)'.format(URI_SCHEME))
        urn_regex = re.compile('{}([\w\\.:;]+)'.format(URN_SCHEME))
        if data.hasFormat('text/uri-list'):
            for url in data.urls():
                local_file = url.toLocalFile()
                if local_file:
                    try:
                        self.import_session(local_file)
                        continue
                    except Exception as e:
                        pass

                url_str = url.toString()
                uri_search = uri_regex.search(url_str)
                urn_search = urn_regex.search(url_str)
                if uri_search:
                    path = uri_search.group(1)
                    ext = uri_search.group(2)
                    self.import_session('{}{}'.format(path, ext))
                elif urn_search:
                    search_str = urn_search.group(1)
                    node_ids = sorted(re.findall('node:([\w\\.]+)', search_str))
                    for node_id in node_ids:
                        x, y = pos.x(), pos.y()
                        self.create_node(node_id, pos=[x, y])
                        x += 20
                        y += 20

    def _on_nodes_moved(self, node_data):
        """
        called when selected nodes in the viewer has changed position.

        Args:
            node_data (dict): {<node_view>: <previous_pos>}
        """
        self._undo_stack.beginMacro('move nodes')
        for node_view, prev_pos in node_data.items():
            node = self._model.nodes[node_view.id]
            self._undo_stack.push(NodeMovedCmd(node, node.pos(), prev_pos))
        self._undo_stack.endMacro()

    def _on_node_backdrop_updated(self, node_id, update_property, value):
        """
        called when a BackdropNode is updated.

        Args:
            node_id (str): backdrop node id.
            value (str): update type.
        """
        backdrop = self.get_node_by_id(node_id)
        if backdrop and isinstance(backdrop, BackdropNode):
            backdrop.on_backdrop_updated(update_property, value)

    def _on_search_triggered(self, node_type, pos):
        """
        called when the tab search widget is triggered in the viewer.

        Args:
            node_type (str): node identifier.
            pos (tuple or list): x, y position for the node.
        """
        self.create_node(node_type, pos=pos)

    def _on_connection_changed(self, disconnected, connected):
        """
        called when a pipe connection has been changed in the viewer.

        Args:
            disconnected (list[list[widgets.port.PortItem]):
                pair list of port view items.
            connected (list[list[widgets.port.PortItem]]):
                pair list of port view items.
        """
        if not self._editable:
            return
        if not (disconnected or connected):
            return

        label = 'connect node(s)' if connected else 'disconnect node(s)'
        ptypes = {IN_PORT: 'inputs', OUT_PORT: 'outputs'}

        self._undo_stack.beginMacro(label)
        for p1_view, p2_view in disconnected:
            node1 = self._model.nodes[p1_view.node.id]
            node2 = self._model.nodes[p2_view.node.id]
            port1 = getattr(node1, ptypes[p1_view.port_type])()[p1_view.name]
            port2 = getattr(node2, ptypes[p2_view.port_type])()[p2_view.name]
            port1.disconnect_from(port2)
        for p1_view, p2_view in connected:
            node1 = self._model.nodes[p1_view.node.id]
            node2 = self._model.nodes[p2_view.node.id]
            port1 = getattr(node1, ptypes[p1_view.port_type])()[p1_view.name]
            port2 = getattr(node2, ptypes[p2_view.port_type])()[p2_view.name]
            port1.connect_to(port2)
        self._undo_stack.endMacro()

    def _on_connection_sliced(self, ports):
        """
        slot when connection pipes have been sliced.

        Args:
            ports (list[list[widgets.port.PortItem]]):
                pair list of port connections (in port, out port)
        """
        if not ports or not self._editable:
            return
        ptypes = {IN_PORT: 'inputs', OUT_PORT: 'outputs'}
        self._undo_stack.beginMacro('slice connections')
        for p1_view, p2_view in ports:
            node1 = self._model.nodes[p1_view.node.id]
            node2 = self._model.nodes[p2_view.node.id]
            port1 = getattr(node1, ptypes[p1_view.port_type])()[p1_view.name]
            port2 = getattr(node2, ptypes[p2_view.port_type])()[p2_view.name]
            port1.disconnect_from(port2)
        self._undo_stack.endMacro()

    @property
    def model(self):
        """
        The model used for storing the node graph data.

        Returns:
            NodeGraphQt.base.model.NodeGraphModel: node graph model.
        """
        return self._model

    @property
    def node_factory(self):
        """
        Return the node factory object used by the node graph.

        Returns:
            NodeFactory: node factory.
        """
        return self._node_factory

    @property
    def widget(self):
        """
        The node graph widget for adding into a layout.

        Returns:
            PySide2.QtWidgets.QWidget: node graph widget.
        """
        if self._widget is None:
            self._widget = QtWidgets.QWidget()
            layout = QtWidgets.QVBoxLayout(self._widget)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)
            if self.root_node() is not None:
                layout.addWidget(self._node_space_bar)
            layout.addWidget(self._viewer)
        return self._widget

    @property
    def undo_view(self):
        """
        Returns node graph undo view.

        Returns:
            PySide2.QtWidgets.QUndoView: node graph undo view.
        """
        if self._undo_view is None:
            self._undo_view = QtWidgets.QUndoView(self._undo_stack)
            self._undo_view.setWindowTitle("Undo History")
        return self._undo_view

    @property
    def auto_update(self):
        """
        Returns whether the graph can run node automatically.
        """
        return self._auto_update

    @property
    def editable(self):
        """
        Returns whether the graph is editable.
        """
        return self._editable

    @editable.setter
    def editable(self, state):
        """
        Set whether the graph is editable.

        Args:
            state(bool).
        """
        self._editable = state
        self._viewer.editable = state
        self._viewer.scene().editable = state

    def show(self):
        """
        Show node graph widget this is just a convenience
        function to :meth:`NodeGraph.widget.show()`.
        """
        self.widget.show()

    def close(self):
        """
        Close node graph NodeViewer widget this is just a convenience
        function to :meth:`NodeGraph.widget.close()`.
        """
        self.widget.close()

    def viewer(self):
        """
        Returns the internal view interface used by the node graph.

        Warnings:
            Methods in the ``NodeViewer`` are used internally
            by ``NodeGraphQt`` components.

        See Also:
            :attr:`NodeGraph.widget` for adding the node graph into a
            :class:`PySide2.QtWidgets.QLayout`.

        Returns:
            NodeGraphQt.widgets.viewer.NodeViewer: viewer interface.
        """
        return self._viewer

    def scene(self):
        """
        Returns the ``QGraphicsScene`` object used in the node graph.

        Returns:
            NodeGraphQt.widgets.scene.NodeScene: node scene.
        """
        return self._viewer.scene()

    def background_color(self):
        """
        Return the node graph background color.

        Returns:
            tuple: r, g ,b
        """
        return self.scene().background_color

    def set_background_color(self, r, g, b):
        """
        Set node graph background color.

        Args:
            r (int): red value.
            g (int): green value.
            b (int): blue value.
        """
        self.scene().background_color = (r, g, b)
        self._viewer.force_update()

    def grid_color(self):
        """
        Return the node graph grid color.

        Returns:
            tuple: r, g ,b
        """
        return self.scene().grid_color

    def set_grid_color(self, r, g, b):
        """
        Set node graph grid color.

        Args:
            r (int): red value.
            g (int): green value.
            b (int): blue value.
        """
        self.scene().grid_color = (r, g, b)
        self._viewer.force_update()

    def set_grid_mode(self, mode=VIEWER_GRID_LINES):
        """
        Set node graph grid mode.

        Note:
            By default grid mode is set to "VIEWER_GRID_LINES".

            Node graph background types:

            * :attr:`NodeGraphQt.constants.VIEWER_GRID_NONE`
            * :attr:`NodeGraphQt.constants.VIEWER_GRID_DOTS`
            * :attr:`NodeGraphQt.constants.VIEWER_GRID_LINES`

        Args:
            mode (int): background style.
        """
        self.scene().grid_mode = mode
        self._viewer.force_update()

    def add_properties_bin(self, prop_bin):
        """
        Wire up a properties bin widget to the node graph.

        Args:
            prop_bin (NodeGraphQt.PropertiesBinWidget): properties widget.
        """
        prop_bin.property_changed.connect(self._on_property_bin_changed)

    def undo_stack(self):
        """
        Returns the undo stack used in the node graph.

        See Also:
            :meth:`NodeGraph.begin_undo()`,
            :meth:`NodeGraph.end_undo()`

        Returns:
            QtWidgets.QUndoStack: undo stack.
        """
        return self._undo_stack

    def clear_undo_stack(self):
        """
        Clears the undo stack.

        Note:
            Convenience function to
            :meth:`NodeGraph.undo_stack().clear()`

        See Also:
            :meth:`NodeGraph.begin_undo()`,
            :meth:`NodeGraph.end_undo()`,
            :meth:`NodeGraph.undo_stack()`
        """
        self._undo_stack.clear()
        gc.collect()

    def begin_undo(self, name):
        """
        Start of an undo block followed by a
        :meth:`NodeGraph.end_undo()`.

        Args:
            name (str): name for the undo block.
        """
        self._undo_stack.beginMacro(name)

    def end_undo(self):
        """
        End of an undo block started by
        :meth:`NodeGraph.begin_undo()`.
        """
        self._undo_stack.endMacro()

    def context_menu(self):
        """
        Returns the main context menu from the node graph.

        Note:
            This is a convenience function to
            :meth:`NodeGraph.get_context_menu`
            with the arg ``menu="graph"``

        Returns:
            NodeGraphQt.NodeGraphMenu: context menu object.
        """
        return self.get_context_menu('graph')

    def context_nodes_menu(self):
        """
        Returns the main context menu for the nodes.

        Note:
            This is a convenience function to
            :meth:`NodeGraph.get_context_menu`
            with the arg ``menu="nodes"``

        Returns:
            NodeGraphQt.NodesMenu: context menu object.
        """
        return self.get_context_menu('nodes')

    def get_context_menu(self, menu):
        """
        Returns the context menu specified by the name.

        Menu Types:
            - ``"graph"`` context menu from the node graph.
            - ``"nodes"`` context menu for the nodes.

        Args:
            menu (str): menu name.

        Returns:
            NodeGraphQt.NodeGraphMenu or NodeGraphQt.NodesMenu: context menu object.
        """
        menus = self._viewer.context_menus()
        if menus.get(menu):
            if menu == 'graph':
                return NodeGraphMenu(self, menus[menu])
            elif menu == 'nodes':
                return NodesMenu(self, menus[menu])

    def disable_context_menu(self, disabled=True, name='all'):
        """
        Disable/Enable context menus from the node graph.

        Menu Types:
            - ``"all"`` all context menus from the node graph.
            - ``"graph"`` context menu from the node graph.
            - ``"nodes"`` context menu for the nodes.

        Args:
            disabled (bool): true to enable context menu.
            name (str): menu name. (default: ``"all"``)
        """
        if name == 'all':
            for k, menu in self._viewer.context_menus().items():
                menu.setDisabled(disabled)
                menu.setVisible(not disabled)
            return
        menus = self._viewer.context_menus()
        if menus.get(name):
            menus[name].setDisabled(disabled)
            menus[name].setVisible(not disabled)

    def acyclic(self):
        """
        Returns true if the current node graph is acyclic.

        See Also:
            :meth:`NodeGraph.set_acyclic`

        Returns:
            bool: true if acyclic (default: ``True``).
        """
        return self._model.acyclic

    def set_acyclic(self, mode=False):
        """
        Enable the node graph to be a acyclic graph. (default: ``False``)

        See Also:
            :meth:`NodeGraph.acyclic`

        Args:
            mode (bool): true to enable acyclic.
        """
        self._model.acyclic = mode
        self._viewer.acyclic = mode

    def pipe_collision(self):
        """
        Returns if pipe collision is enabled in the current session.

        See Also:
            To enable/disable pipe collision
            :meth:`NodeGraph.set_pipe_collision`

        Returns:
            bool: True if pipe collision is enabled.
        """
        return self._model.pipe_collision

    def set_pipe_collision(self, mode=False):
        """
        Enable/Disable pipe collision. (default: ``False``)

        When enabled dragging a node over a pipe will allow the node to be
        inserted as a new connection between the pipe.

        See Also:
            :meth:`NodeGraph.pipe_collision`

        Args:
            mode (bool): True to enable pipe collision.
        """
        self._model.pipe_collision = mode
        self._viewer.pipe_collision = mode

    def set_pipe_style(self, style=PIPE_LAYOUT_CURVED):
        """
        Set node graph pipes to be drawn as straight, curved or angled.

        .. image:: _images/pipe_layout_types.gif
            :width: 80%

        Note:
            By default pipe layout is set to "PIPE_LAYOUT_CURVED".

            Pipe Layout Styles:

            * :attr:`NodeGraphQt.constants.PIPE_LAYOUT_CURVED`
            * :attr:`NodeGraphQt.constants.PIPE_LAYOUT_STRAIGHT`
            * :attr:`NodeGraphQt.constants.PIPE_LAYOUT_ANGLE`

        Args:
            style (int): pipe layout style.
        """
        pipe_max = max([PIPE_LAYOUT_CURVED,
                        PIPE_LAYOUT_STRAIGHT,
                        PIPE_LAYOUT_ANGLE])
        style = style if 0 <= style <= pipe_max else PIPE_LAYOUT_CURVED
        self._viewer.set_pipe_layout(style)

    def fit_to_selection(self):
        """
        Sets the zoom level to fit selected nodes.
        If no nodes are selected then all nodes in the graph will be framed.
        """
        if self._current_node_space is None:
            all_nodes = self.all_nodes()
        else:
            all_nodes = self._current_node_space.children()

        nodes = self.selected_nodes() or all_nodes
        if not nodes:
            return
        self._viewer.zoom_to_nodes([n.view for n in nodes])

    def reset_zoom(self):
        """
        Reset the zoom level
        """
        self._viewer.reset_zoom()

    def set_zoom(self, zoom=0):
        """
        Set the zoom factor of the Node Graph the default is ``0.0``

        Args:
            zoom (float): zoom factor (max zoom out ``-0.9`` / max zoom in ``2.0``)
        """
        self._viewer.set_zoom(zoom)

    def get_zoom(self):
        """
        Get the current zoom level of the node graph.

        Returns:
            float: the current zoom level.
        """
        return self._viewer.get_zoom()

    def center_on(self, nodes=None):
        """
        Center the node graph on the given nodes or all nodes by default.

        Args:
            nodes (list[NodeGraphQt.BaseNode]): a list of nodes.
        """
        self._viewer.center_selection(nodes)

    def center_selection(self):
        """
        Centers on the current selected nodes.
        """
        nodes = self._viewer.selected_nodes()
        self._viewer.center_selection(nodes)

    def registered_nodes(self):
        """
        Return a list of all node types that have been registered.

        See Also:
            To register a node :meth:`NodeGraph.register_node`

        Returns:
            list[str]: list of node type identifiers.
        """
        return sorted(self._node_factory.nodes.keys())

    def register_node(self, node, alias=None):
        """
        Register the node to the :meth:`NodeGraph.node_factory`

        Args:
            node (NodeGraphQt.NodeObject): node.
            alias (str): custom alias name for the node type.
        """
        self._node_factory.register_node(node, alias)
        self._viewer.rebuild_tab_search()

    def register_nodes(self, nodes):
        """
        Register the nodes to the :meth:`NodeGraph.node_factory`

        Args:
            nodes (list): list of nodes.
        """
        [self._node_factory.register_node(n) for n in nodes]
        self._viewer.rebuild_tab_search()

    def create_node(self, node_type, name=None, selected=True, color=None,
                    text_color=None, pos=None):
        """
        Create a new node in the node graph.

        See Also:
            To list all node types :meth:`NodeGraph.registered_nodes`

        Args:
            node_type (str): node instance type.
            name (str): set name of the node.
            selected (bool): set created node to be selected.
            color (tuple or str): node color ``(255, 255, 255)`` or ``"#FFFFFF"``.
            text_color (tuple or str): text color ``(255, 255, 255)`` or ``"#FFFFFF"``.
            pos (list[int, int]): initial x, y position for the node (default: ``(0, 0)``).

        Returns:
            BaseNode or NodeObject: the created instance of the node.
        """
        if not self._editable:
            return
        NodeCls = self._node_factory.create_node_instance(node_type)
        if NodeCls:
            node = NodeCls()
            node.model._graph_model = self.model

            wid_types = node.model.__dict__.pop('_TEMP_property_widget_types')
            prop_attrs = node.model.__dict__.pop('_TEMP_property_attrs')

            if self.model.get_node_common_properties(node.type_) is None:
                node_attrs = {node.type_: {
                    n: {'widget_type': wt} for n, wt in wid_types.items()
                }}
                for pname, pattrs in prop_attrs.items():
                    node_attrs[node.type_][pname].update(pattrs)
                self.model.set_node_common_properties(node_attrs)

            node.NODE_NAME = self.get_unique_name(name or node.NODE_NAME)
            node.model.name = node.NODE_NAME
            node.model.selected = selected
            node.set_graph(self)

            def format_color(clr):
                if isinstance(clr, str):
                    clr = clr.strip('#')
                    return tuple(int(clr[i:i + 2], 16) for i in (0, 2, 4))
                return clr

            if color:
                node.model.color = format_color(color)
            if text_color:
                node.model.text_color = format_color(text_color)
            if pos:
                node.model.pos = [float(pos[0]), float(pos[1])]

            # set node parent
            if not node.has_property('root'):
                node.set_parent(self._current_node_space)
            else:
                node.set_parent(None)

            # update the node view from model.
            node.update()

            undo_cmd = NodeAddedCmd(self, node, node.model.pos)
            undo_cmd.setText('create node: "{}"'.format(node.NODE_NAME))

            if isinstance(node, SubGraph):
                self.begin_undo('create sub graph node')
                self._undo_stack.push(undo_cmd)
                if node.get_property('create_from_select'):
                    node.create_from_nodes(self.selected_nodes())
                self.end_undo()
            else:
                self._undo_stack.push(undo_cmd)
            self.node_created.emit(node)
            return node
        raise Exception('\n\n>> Cannot find node:\t"{}"\n'.format(node_type))

    def add_node(self, node, pos=None, unique_name=True):
        """
        Add a node into the node graph.
        unlike the :meth:`NodeGraph.create_node` function this will not
        trigger the :attr:`NodeGraph.node_created` signal.

        Args:
            node (NodeGraphQt.BaseNode): node object.
            pos (list[float]): node x,y position. (optional)
            unique_name (bool): make node name unique
        """
        if not self._editable:
            return
        assert isinstance(node, NodeObject), 'node must be a Node instance.'

        wid_types = node.model.__dict__.pop('_TEMP_property_widget_types')
        prop_attrs = node.model.__dict__.pop('_TEMP_property_attrs')

        if self.model.get_node_common_properties(node.type_) is None:
            node_attrs = {node.type_: {
                n: {'widget_type': wt} for n, wt in wid_types.items()
            }}
            for pname, pattrs in prop_attrs.items():
                node_attrs[node.type_][pname].update(pattrs)
            self.model.set_node_common_properties(node_attrs)
        node.set_graph(self)
        if unique_name:
            node.NODE_NAME = self.get_unique_name(node.NODE_NAME)
        node.model._graph_model = self.model
        node.model.name = node.NODE_NAME
        node.update()

        self._undo_stack.beginMacro('add node: "{}"'.format(node.name()))
        self._undo_stack.push(NodeAddedCmd(self, node, pos))
        node.set_selected(True)
        self._undo_stack.endMacro()

    def set_node_space(self, node):
        """
        Set the node space of the node graph.

        Args:
            node (NodeGraphQt.SubGraph): node object.
        """
        if node is self._current_node_space or not isinstance(node, SubGraph):
            return

        if self._current_node_space is not None:
            self._current_node_space.exit()

        self._current_node_space = node
        if node is not None:
            node.enter()
            self._node_space_bar.set_node(node)
            self.editable = node.is_editable()
            [n.set_editable(self.editable) for n in node.children() if isinstance(n, BaseNode)]
        else:
            self.editable = True

    def get_node_space(self):
        """
        Get the node space of the node graph.

        Returns:
            node (NodeGraphQt.SubGraph): node object or None.
        """
        return self._current_node_space

    def delete_node(self, node):
        """
        Remove the node from the node graph.

        Args:
            node (NodeGraphQt.BaseNode): node object.
        """
        if not self._editable:
            return
        assert isinstance(node, NodeObject), \
            'node must be a instance of a NodeObject.'
        if node is self.root_node():
            return

        node_id = node.id
        self._undo_stack.beginMacro('delete node: "{}"'.format(node.name()))
        if isinstance(node, BaseNode):
            for p in node.input_ports():
                if p.locked():
                    p.set_locked(False, connected_ports=False)
                p.clear_connections()
            for p in node.output_ports():
                if p.locked():
                    p.set_locked(False, connected_ports=False)
                p.clear_connections()

        if isinstance(node, SubGraph):
            self.delete_nodes(node.children())
            self._undo_stack.push(NodeRemovedCmd(self, node))

        self._undo_stack.push(NodeRemovedCmd(self, node))
        self._undo_stack.endMacro()
        self.nodes_deleted.emit([node_id])

    def delete_nodes(self, nodes):
        """
        Remove a list of specified nodes from the node graph.

        Args:
            nodes (list[NodeGraphQt.BaseNode]): list of node instances.
        """
        if not nodes:
            return
        if not self._editable:
            return
        node_ids = [n.id for n in nodes]
        root_node = self.root_node()
        self._undo_stack.beginMacro('delete nodes')
        for node in nodes:
            if isinstance(node, BaseNode):
                for p in node.input_ports():
                    if p.locked():
                        p.set_locked(False, connected_ports=False)
                    p.clear_connections()
                for p in node.output_ports():
                    if p.locked():
                        p.set_locked(False, connected_ports=False)
                    p.clear_connections()
            if isinstance(node, SubGraph):
                self.delete_nodes(node.children())
            if node is not root_node:
                self._undo_stack.push(NodeRemovedCmd(self, node))
        self._undo_stack.endMacro()
        self.nodes_deleted.emit(node_ids)

    def delete_pipe(self, pipe):
        self._on_connection_changed([(pipe.input_port, pipe.output_port)], [])

    def delete_pipes(self, pipes):
        disconnected = []
        for pipe in pipes:
            disconnected.append((pipe.input_port, pipe.output_port))
        if disconnected:
            self._on_connection_changed(disconnected, [])

    def all_nodes(self):
        """
        Return all nodes in the node graph.

        Returns:
            list[NodeGraphQt.BaseNode]: list of nodes.
        """
        return list(self._model.nodes.values())

    def selected_nodes(self):
        """
        Return all selected nodes that are in the node graph.

        Returns:
            list[NodeGraphQt.BaseNode]: list of nodes.
        """
        nodes = []
        for item in self._viewer.selected_nodes():
            node = self._model.nodes[item.id]
            nodes.append(node)
        return nodes

    def select_all(self):
        """
        Select all nodes in the node graph.
        """
        self._undo_stack.beginMacro('select all')
        if self._current_node_space is not None:
            [node.set_selected(True) for node in self._current_node_space.children()]
        else:
            [node.set_selected(True) for node in self.all_nodes()]
        self._undo_stack.endMacro()

    def clear_selection(self):
        """
        Clears the selection in the node graph.
        """
        self._undo_stack.beginMacro('clear selection')
        [node.set_selected(False) for node in self.all_nodes()]
        self._undo_stack.endMacro()

    def get_node_by_id(self, node_id=None):
        """
        Returns the node from the node id string.

        Args:
            node_id (str): node id (:attr:`NodeObject.id`)

        Returns:
            NodeGraphQt.NodeObject: node object.
        """
        return self._model.nodes.get(node_id, None)

    def get_node_by_path(self, node_path):
        """
        Returns the node from the node path string.

        Args:
            node_path (str): node path (:attr:`NodeObject.path()`)

        Returns:
            NodeGraphQt.NodeObject: node object.
        """
        names = [name for name in node_path.split("/") if name]
        names.pop(0)

        node = self.root_node()
        if node is None:
            return None

        for name in names:
            find = False
            for n in node.children():
                if n.name() == name:
                    node = n
                    find = True
                    continue
            if not find:
                return None
        return node

    def get_node_by_name(self, name):
        """
        Returns node that matches the name.

        Args:
            name (str): name of the node.
        Returns:
            NodeGraphQt.NodeObject: node object.
        """
        if self._current_node_space is not None:
            nodes = self._current_node_space.children()
        else:
            nodes = self.all_nodes()
        for node in nodes:
            if node.name() == name:
                return node
        return None

    def get_unique_name(self, name):
        """
        Creates a unique node name to avoid having nodes with the same name.

        Args:
            name (str): node name.

        Returns:
            str: unique node name.
        """
        name = ' '.join(name.split())
        if self._current_node_space is not None:
            node_names = [n.name() for n in self._current_node_space.children()]
        else:
            node_names = [n.name() for n in self.all_nodes()]
        if name not in node_names:
            return name

        regex = re.compile('[\w ]+(?: )*(\d+)')
        search = regex.search(name)
        if not search:
            for x in range(1, len(node_names) + 2):
                new_name = '{} {}'.format(name, x)
                if new_name not in node_names:
                    return new_name

        version = search.group(1)
        name = name[:len(version) * -1].strip()
        for x in range(1, len(node_names) + 2):
            new_name = '{} {}'.format(name, x)
            if new_name not in node_names:
                return new_name
        return name + "_"

    def current_session(self):
        """
        Returns the file path to the currently loaded session.

        Returns:
            str: path to the currently loaded session
        """
        return self._model.session

    def clear_session(self):
        """
        Clears the current node graph session.
        """
        root_node = self.root_node()
        for n in self.all_nodes():
            if n is root_node:
                continue
            if isinstance(n, BaseNode):
                for p in n.input_ports():
                    if p.locked():
                        p.set_locked(False, connected_ports=False)
                    p.clear_connections()
                for p in n.output_ports():
                    if p.locked():
                        p.set_locked(False, connected_ports=False)
                    p.clear_connections()
            self._undo_stack.push(NodeRemovedCmd(self, n))
        self.set_node_space(root_node)
        self.clear_undo_stack()
        self._model.session = ''
        self.session_changed.emit('')

    def _serialize(self, nodes):
        """
        serialize nodes to a dict.
        (used internally by the node graph)

        Args:
            nodes (list[NodeGraphQt.Nodes]): list of node instances.

        Returns:
            dict: serialized data.
        """
        serial_data = {'graph': {}, 'nodes': {}, 'connections': []}
        nodes_data = {}

        # serialize graph session.
        serial_data['graph']['acyclic'] = self.acyclic()
        serial_data['graph']['pipe_collision'] = self.pipe_collision()

        # serialize nodes.
        root_node = self.root_node()
        for n in nodes:
            if n is root_node:
                continue
            # update the node model.
            n.update_model()

            node_dict = n.model.to_dict

            if isinstance(n, SubGraph):
                published = n.get_property('published')
                if not published:
                    children = n.children()
                    if children:
                        node_dict[n.model.id]['sub_graph'] = self._serialize(children)

            nodes_data.update(node_dict)

        for n_id, n_data in nodes_data.items():
            serial_data['nodes'][n_id] = n_data

            # serialize connections
            inputs = n_data.pop('inputs') if n_data.get('inputs') else {}
            outputs = n_data.pop('outputs') if n_data.get('outputs') else {}

            for pname, conn_data in inputs.items():
                for conn_id, prt_names in conn_data.items():
                    for conn_prt in prt_names:
                        pipe = {IN_PORT: [n_id, pname],
                                OUT_PORT: [conn_id, conn_prt]}
                        if pipe not in serial_data['connections']:
                            serial_data['connections'].append(pipe)

            for pname, conn_data in outputs.items():
                for conn_id, prt_names in conn_data.items():
                    for conn_prt in prt_names:
                        pipe = {OUT_PORT: [n_id, pname],
                                IN_PORT: [conn_id, conn_prt]}
                        if pipe not in serial_data['connections']:
                            serial_data['connections'].append(pipe)

        if not serial_data['connections']:
            serial_data.pop('connections')

        return serial_data

    def _deserialize(self, data, relative_pos=False, pos=None, set_parent=True):
        """
        deserialize node data.
        (used internally by the node graph)

        Args:
            data (dict): node data.
            relative_pos (bool): position node relative to the cursor.
            pos (tuple or list): custom x, y position.
            set_parent (bool): set node parent to current node space.

        Returns:
            list[NodeGraphQt.Nodes]: list of node instances.
        """
        if not self._editable:
            return

        # update node graph properties.
        for attr_name, attr_value in data.get('graph', {}).items():
            if attr_name == 'acyclic':
                self.set_acyclic(attr_value)
            elif attr_name == 'pipe_collision':
                self.set_pipe_collision(attr_value)

        _temp_auto_update = self._auto_update
        self._auto_update = False

        nodes = {}
        # build the nodes.
        for n_id, n_data in data.get('nodes', {}).items():
            identifier = n_data['type_']
            NodeCls = self._node_factory.create_node_instance(identifier)
            if NodeCls:
                node = NodeCls()
                node.NODE_NAME = n_data.get('name', node.NODE_NAME)
                # set properties.
                for prop in node.model.properties.keys():
                    if prop in n_data.keys():
                        node.model.set_property(prop, n_data[prop])
                # set custom properties.
                for prop, val in n_data.get('custom', {}).items():
                    node.model.set_property(prop, val)

                nodes[n_id] = node

                if isinstance(node, SubGraph):
                    node.create_by_deserialize = True
                    self.add_node(node, n_data.get('pos'), unique_name=set_parent)
                    published = n_data['custom'].get('published', False)
                    if not published:
                        sub_graph = n_data.get('sub_graph', None)
                        if sub_graph:
                            children = self._deserialize(sub_graph, relative_pos, pos, False)
                            [child.set_parent(node) for child in children]
                else:
                    self.add_node(node, n_data.get('pos'), unique_name=set_parent)

                if n_data.get('dynamic_port', None):
                    node.set_ports({
                        'input_ports': n_data['input_ports'],
                        'output_ports': n_data['output_ports']
                    })

        # build the connections.
        for connection in data.get('connections', []):
            nid, pname = connection.get('in', ('', ''))
            in_node = nodes.get(nid)
            if not in_node:
                continue
            in_port = in_node.inputs().get(pname) if in_node else None

            nid, pname = connection.get('out', ('', ''))
            out_node = nodes.get(nid)
            if not out_node:
                continue
            out_port = out_node.outputs().get(pname) if out_node else None

            if in_port and out_port:
                self._undo_stack.push(PortConnectedCmd(in_port, out_port))

        node_objs = list(nodes.values())
        if relative_pos:
            self._viewer.move_nodes([n.view for n in node_objs])
            [setattr(n.model, 'pos', n.view.xy_pos) for n in node_objs]
        elif pos:
            self._viewer.move_nodes([n.view for n in node_objs], pos=pos)
            [setattr(n.model, 'pos', n.view.xy_pos) for n in node_objs]

        if set_parent:
            [node.set_parent(self._current_node_space) for node in node_objs]
        self._auto_update = _temp_auto_update

        return node_objs

    def serialize_session(self):
        """
        Serializes the current node graph layout to a dictionary.

        See Also:
            :meth:`NodeGraph.deserialize_session`,
            :meth:`NodeGraph.save_session`,
            :meth:`NodeGraph.load_session`

        Returns:
            dict: serialized session of the current node layout.
        """
        return self._serialize(self.all_nodes())

    def deserialize_session(self, layout_data):
        """
        Load node graph session from a dictionary object.

        See Also:
            :meth:`NodeGraph.serialize_session`,
            :meth:`NodeGraph.load_session`,
            :meth:`NodeGraph.save_session`

        Args:
            layout_data (dict): dictionary object containing a node session.
        """
        self.clear_session()
        self._deserialize(layout_data)
        self.clear_undo_stack()

    def save_session(self, file_path):
        """
        Saves the current node graph session layout to a `JSON` formatted file.

        See Also:
            :meth:`NodeGraph.serialize_session`,
            :meth:`NodeGraph.deserialize_session`,
            :meth:`NodeGraph.load_session`,

        Args:
            file_path (str): path to the saved node layout.
        """

        root_node = self.root_node()
        if root_node is not None:
            nodes = root_node.children()
        else:
            nodes = self.all_nodes()

        serialized_data = self._serialize(nodes)

        node_space = self.get_node_space()
        if node_space is not None:
            node_space = node_space.id
        serialized_data['graph'] = {'node_space': node_space, 'pipe_layout': self._viewer.get_pipe_layout()}
        serialized_data['graph']['graph_rect'] = self._viewer.scene_rect()
        serialized_data['graph']['grid_mode'] = self.scene().grid_mode

        file_path = file_path.strip()
        with open(file_path, 'w') as file_out:
            json.dump(serialized_data, file_out, indent=2, separators=(',', ':'))

        self._model.session = file_path
        self.session_changed.emit(file_path)
        self._viewer.clear_key_state()

    def load_session(self, file_path):
        """
        Load node graph session layout file.

        See Also:
            :meth:`NodeGraph.deserialize_session`,
            :meth:`NodeGraph.serialize_session`,
            :meth:`NodeGraph.save_session`

        Args:
            file_path (str): path to the serialized layout file.
        """
        self.clear_session()
        self.import_session(file_path)

    def import_session(self, file_path):
        """
        Import node graph session layout file.

        Args:
            file_path (str): path to the serialized layout file.
        """
        file_path = file_path.strip()
        if not os.path.isfile(file_path):
            raise IOError('file does not exist: {}'.format(file_path))

        try:
            with open(file_path) as data_file:
                layout_data = json.load(data_file)
        except Exception as e:
            layout_data = None
            print('Cannot read data from file.\n{}'.format(e))

        if not layout_data:
            return

        self._deserialize(layout_data)

        if 'graph' in layout_data.keys():
            self.set_node_space(self.root_node())
            self._viewer.set_pipe_layout(layout_data['graph']['pipe_layout'])
            self._viewer.set_scene_rect(layout_data['graph']['graph_rect'])
            self.set_grid_mode(layout_data['graph'].get('grid_mode', VIEWER_GRID_LINES))

        self.set_node_space(self.root_node())
        self.clear_undo_stack()
        self._model.session = file_path
        self.session_changed.emit(file_path)

    def copy_nodes(self, nodes=None):
        """
        Copy nodes to the clipboard.

        See Also:
            :meth:`NodeGraph.cut_nodes`

        Args:
            nodes (list[NodeGraphQt.BaseNode]):
                list of nodes (default: selected nodes).
        """
        nodes = nodes or self.selected_nodes()
        if not nodes:
            return False
        clipboard = QtWidgets.QApplication.clipboard()
        serial_data = self._serialize(nodes)
        serial_str = json.dumps(serial_data)
        if serial_str:
            clipboard.setText(serial_str)
            return True
        return False

    def cut_nodes(self, nodes=None):
        """
        Cut nodes to the clipboard.

        See Also:
            :meth:`NodeGraph.copy_nodes`

        Args:
            nodes (list[NodeGraphQt.BaseNode]):
                list of nodes (default: selected nodes).
        """
        self._undo_stack.beginMacro('cut nodes')
        nodes = nodes or self.selected_nodes()
        self.copy_nodes(nodes)
        self.delete_nodes(nodes)
        self._undo_stack.endMacro()

    def paste_nodes(self):
        """
        Pastes nodes copied from the clipboard.
        """
        if not self._editable:
            return
        clipboard = QtWidgets.QApplication.clipboard()
        cb_text = clipboard.text()
        if not cb_text:
            return

        self._undo_stack.beginMacro('pasted nodes')
        serial_data = json.loads(cb_text)
        self.clear_selection()
        nodes = self._deserialize(serial_data, relative_pos=True)
        [n.set_selected(True) for n in nodes]
        self._undo_stack.endMacro()

    def duplicate_nodes(self, nodes):
        """
        Create duplicate copy from the list of nodes.

        Args:
            nodes (list[NodeGraphQt.BaseNode]): list of nodes.
        Returns:
            list[NodeGraphQt.BaseNode]: list of duplicated node instances.
        """
        if not nodes or not self._editable:
            return

        self._undo_stack.beginMacro('duplicate nodes')

        self.clear_selection()
        serial = self._serialize(nodes)
        new_nodes = self._deserialize(serial)
        offset = 50
        for n in new_nodes:
            x, y = n.pos()
            n.set_pos(x + offset, y + offset)
            n.set_property('selected', True)

        self._undo_stack.endMacro()
        return new_nodes

    def disable_nodes(self, nodes, mode=None):
        """
        Set weather to Disable or Enable specified nodes.

        See Also:
            :meth:`NodeObject.set_disabled`

        Args:
            nodes (list[NodeGraphQt.BaseNode]): list of node instances.
            mode (bool): (optional) disable state of the nodes.
        """
        if not nodes or not self._editable:
            return
        if mode is None:
            mode = not nodes[0].disabled()
        if len(nodes) > 1:
            text = {False: 'enable', True: 'disable'}[mode]
            text = '{} ({}) nodes'.format(text, len(nodes))
            self._undo_stack.beginMacro(text)
            [n.set_disabled(mode) for n in nodes]
            self._undo_stack.endMacro()
            return
        nodes[0].set_disabled(mode)

    # auto layout node functions.

    @staticmethod
    def _update_node_rank(node, nodes_rank, down_stream=True):
        """
        Recursive function for updating the node ranking.

        Args:
            node (NodeGraphQt.BaseNode): node to start from.
            nodes_rank (dict): node ranking object to be updated.
            down_stream (bool): true to rank down stram.
        """
        if down_stream:
            node_values = node.connected_output_nodes().values()
        else:
            node_values = node.connected_input_nodes().values()

        connected_nodes = set()
        for nodes in node_values:
            connected_nodes.update(nodes)

        rank = nodes_rank[node] + 1
        for n in connected_nodes:
            if n in nodes_rank:
                nodes_rank[n] = max(nodes_rank[n], rank)
            else:
                nodes_rank[n] = rank
            NodeGraph._update_node_rank(n, nodes_rank, down_stream)

    @staticmethod
    def _compute_node_rank(nodes, down_stream=True):
        """
        Compute the ranking of nodes.

        Args:
            nodes (list[NodeGraphQt.BaseNode]): nodes to start ranking from.
            down_stream (bool): true to compute down stream.

        Returns:
            dict: {NodeGraphQt.BaseNode: node_rank, ...}
        """
        nodes_rank = {}
        for node in nodes:
            nodes_rank[node] = 0
            NodeGraph._update_node_rank(node, nodes_rank, down_stream)
        return nodes_rank

    def auto_layout_nodes(self, nodes=None, down_stream=True, start_nodes=None):
        """
        Auto layout the nodes in the node graph.

        Note:
            If the node graph is acyclic then the ``start_nodes`` will need
            to be specified.

        Args:
            nodes (list[NodeGraphQt.BaseNode]): list of nodes to auto layout
                if nodes is None then all nodes is layed out.
            down_stream (bool): false to layout up stream.
            start_nodes (list[NodeGraphQt.BaseNode]):
                list of nodes to start the auto layout from (Optional).
        """
        self.begin_undo('Auto Layout Nodes')

        nodes = nodes or self.all_nodes()

        # filter out the backdrops.
        backdrops = {
            n: n.nodes() for n in nodes if isinstance(n, BackdropNode)
        }
        filtered_nodes = [n for n in nodes if not isinstance(n, BackdropNode)]

        start_nodes = start_nodes or []
        if down_stream:
            start_nodes += [
                n for n in filtered_nodes
                if not any(n.connected_input_nodes().values())
            ]
        else:
            start_nodes += [
                n for n in filtered_nodes
                if not any(n.connected_output_nodes().values())
            ]

        if not start_nodes:
            return

        node_views = [n.view for n in nodes]
        nodes_center_0 = self.viewer().nodes_rect_center(node_views)

        nodes_rank = NodeGraph._compute_node_rank(start_nodes, down_stream)

        rank_map = {}
        for node, rank in nodes_rank.items():
            if rank in rank_map:
                rank_map[rank].append(node)
            else:
                rank_map[rank] = [node]

        if NODE_LAYOUT_DIRECTION is NODE_LAYOUT_HORIZONTAL:
            current_x = 0
            node_height = 120
            for rank in sorted(range(len(rank_map)), reverse=not down_stream):
                ranked_nodes = rank_map[rank]
                max_width = max([node.view.width for node in ranked_nodes])
                current_x += max_width
                current_y = 0
                for idx, node in enumerate(ranked_nodes):
                    dy = max(node_height, node.view.height)
                    current_y += 0 if idx == 0 else dy
                    node.set_pos(current_x, current_y)
                    current_y += dy * 0.5 + 10

                current_x += max_width * 0.5 + 100
        elif NODE_LAYOUT_DIRECTION is NODE_LAYOUT_VERTICAL:
            current_y = 0
            node_width = 250
            for rank in sorted(range(len(rank_map)), reverse=not down_stream):
                ranked_nodes = rank_map[rank]
                max_height = max([node.view.height for node in ranked_nodes])
                current_y += max_height
                current_x = 0
                for idx, node in enumerate(ranked_nodes):
                    dx = max(node_width, node.view.width)
                    current_x += 0 if idx == 0 else dx
                    node.set_pos(current_x, current_y)
                    current_x += dx * 0.5 + 10

                current_y += max_height * 0.5 + 100

        nodes_center_1 = self.viewer().nodes_rect_center(node_views)
        dx = nodes_center_0[0] - nodes_center_1[0]
        dy = nodes_center_0[1] - nodes_center_1[1]
        [n.set_pos(n.x_pos() + dx, n.y_pos() + dy) for n in nodes]

        # wrap the backdrop nodes.
        for backdrop, contained_nodes in backdrops.items():
            backdrop.wrap_nodes(contained_nodes)

        self.end_undo()

    # prompt dialog functions.

    def question_dialog(self, text, title='Node Graph'):
        """
        Prompts a question open dialog with ``"Yes"`` and ``"No"`` buttons in
        the node graph.

        Note:
            Convenience function to
            :meth:`NodeGraph.viewer().question_dialog`

        Args:
            text (str): question text.
            title (str): dialog window title.

        Returns:
            bool: true if user clicked yes.
        """
        return self._viewer.question_dialog(text, title)

    def message_dialog(self, text, title='Node Graph'):
        """
        Prompts a file open dialog in the node graph.

        Note:
            Convenience function to
            :meth:`NodeGraph.viewer().message_dialog`

        Args:
            text (str): message text.
            title (str): dialog window title.
        """
        self._viewer.message_dialog(text, title)

    def load_dialog(self, current_dir=None, ext=None):
        """
        Prompts a file open dialog in the node graph.

        Note:
            Convenience function to
            :meth:`NodeGraph.viewer().load_dialog`

        Args:
            current_dir (str): path to a directory.
            ext (str): custom file type extension (default: ``"json"``)

        Returns:
            str: selected file path.
        """
        return self._viewer.load_dialog(current_dir, ext)

    def save_dialog(self, current_dir=None, ext=None):
        """
        Prompts a file save dialog in the node graph.

        Note:
            Convenience function to
            :meth:`NodeGraph.viewer().save_dialog`

        Args:
            current_dir (str): path to a directory.
            ext (str): custom file type extension (default: ``"json"``)

        Returns:
            str: selected file path.
        """
        return self._viewer.save_dialog(current_dir, ext)

    ### ---

    def use_OpenGL(self):
        """
        Use OpenGL to draw the graph.
        """
        self._viewer.use_OpenGL()

    def graph_rect(self):
        """
        Get the graph viewer range.

        Returns:
            list: [x, y, width, height].
        """
        return self._viewer.scene_rect()

    def set_graph_rect(self, rect):
        """
        Set the graph viewer range.

        Args:
            rect (list): [x, y, width, height].
        """
        self._viewer.set_scene_rect(rect)

    def root_node(self):
        """
        Get the graph root node.

        Returns:
            node (BaseNode): node object.
        """
        return self.get_node_by_id('0' * 13)


class SubGraph(object):
    """
    The ``NodeGraphQt.SubGraph`` class is the base class that all
    Sub Graph Node inherit from.

    *Implemented on NodeGraphQt:* ``v0.1.0``

    .. image:: _images/example_subgraph.gif
        :width: 80%

    """

    def __init__(self):
        self._children = set()

    def children(self):
        """
        Returns the children of the sub graph.
        """
        return list(self._children)

    def create_from_nodes(self, nodes):
        """
        Create sub graph from the nodes.

        Args:
            nodes (list[NodeGraphQt.NodeObject]): nodes to create the sub graph.
        """
        if self in nodes:
            nodes.remove(self)
        [n.set_parent(self) for n in nodes]

    def add_child(self, node):
        """
        Add a node to the sub graph.

        Args:
            node (NodeGraphQt.BaseNode): node object.
        """
        self._children.add(node)

    def remove_child(self, node):
        """
        Remove a node from the sub graph.

        Args:
            node (NodeGraphQt.BaseNode): node object.
        """
        if node in self._children:
            self._children.remove(node)

    def enter(self):
        """
        Action when enter the sub graph.
        """
        pass

    def exit(self):
        """
        Action when exit the sub graph.
        """
        pass
