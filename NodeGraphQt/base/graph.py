#!/usr/bin/python
# -*- coding: utf-8 -*-
import copy
import json
import os
import re
from pathlib import Path

from Qt import QtCore, QtWidgets

from NodeGraphQt.base.commands import (NodeAddedCmd, NodeMovedCmd,
                                       NodesRemovedCmd, PortConnectedCmd)
from NodeGraphQt.base.factory import NodeFactory
from NodeGraphQt.base.menu import NodeGraphMenu, NodesMenu
from NodeGraphQt.base.model import NodeGraphModel
from NodeGraphQt.base.node import NodeObject
from NodeGraphQt.base.port import Port
from NodeGraphQt.constants import (MIME_TYPE, URI_SCHEME, URN_SCHEME,
                                   LayoutDirectionEnum, PipeLayoutEnum,
                                   PortTypeEnum, ViewerEnum)
from NodeGraphQt.errors import NodeCreationError, NodeDeletionError
from NodeGraphQt.nodes.backdrop_node import BackdropNode
from NodeGraphQt.nodes.base_node import BaseNode
from NodeGraphQt.nodes.group_node import GroupNode
from NodeGraphQt.nodes.port_node import PortInputNode, PortOutputNode
from NodeGraphQt.widgets.node_graph import NodeGraphWidget, SubGraphWidget
from NodeGraphQt.widgets.viewer import NodeViewer
from NodeGraphQt.widgets.viewer_nav import NodeNavigationWidget


class NodeGraph(QtCore.QObject):
    """
    The ``NodeGraph`` class is the main controller for managing all nodes
    and the node graph.

    .. inheritance-diagram:: NodeGraphQt.NodeGraph
        :top-classes: PySide2.QtCore.QObject

    .. image:: ../_images/graph.png
        :width: 60%
    """

    nodes_registered = QtCore.Signal(list)
    """
    Signal triggered when a node is registered into the node graph.

    :parameters: list[:class:`NodeGraphQt.NodeObject`]
    :emits: registered nodes
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

    :parameters: str
    :emits: new session path
    """
    context_menu_prompt = QtCore.Signal(object, object)
    """
    Signal is triggered just before a context menu is shown.

    :parameters: 
        :class:`NodeGraphQt.NodeGraphMenu` or :class:`NodeGraphQt.NodesMenu`, 
        :class:`NodeGraphQt.BaseNode`
    :emits: triggered context menu, node object.
    """

    def __init__(self, parent=None, **kwargs):
        """
        Args:
            parent (object): object parent.
            **kwargs (dict): Used for overriding internal objects at init time.
        """
        super(NodeGraph, self).__init__(parent)
        self.setObjectName('NodeGraph')
        self._model = (
            kwargs.get('model') or NodeGraphModel())
        self._node_factory = (
            kwargs.get('node_factory') or NodeFactory())
        self._undo_view = None
        self._undo_stack = (
            kwargs.get('undo_stack') or QtWidgets.QUndoStack(self)
        )
        self._widget = None
        self._sub_graphs = {}
        self._viewer = (
            kwargs.get('viewer') or NodeViewer(undo_stack=self._undo_stack)
        )

        layout_direction = kwargs.get('layout_direction')
        if layout_direction:
            if layout_direction not in [e.value for e in LayoutDirectionEnum]:
                layout_direction = LayoutDirectionEnum.HORIZONTAL.value
            self._model.layout_direction = layout_direction
        else:
            layout_direction = self._model.layout_direction
        self._viewer.set_layout_direction(layout_direction)

        pipe_style = kwargs.get('pipe_style')
        if pipe_style is not None:
            if pipe_style not in [e.value for e in PipeLayoutEnum]:
                pipe_style = PipeLayoutEnum.CURVED.value
            self._model.pipe_style = pipe_style
        else:
            pipe_style = self._model.pipe_style
        self._viewer.set_pipe_layout(pipe_style)

        # viewer needs a reference to the model port connection constrains
        # for the user interaction with the live pipe.
        self._viewer.accept_connection_types = self._model.accept_connection_types
        self._viewer.reject_connection_types = self._model.reject_connection_types

        self._context_menu = {}

        self._register_context_menu()
        self._register_builtin_nodes()
        self._wire_signals()

    def __repr__(self):
        return '<{}("root") object at {}>'.format(
            self.__class__.__name__, hex(id(self)))

    def _register_context_menu(self):
        """
        Register the default context menus.
        """
        if not self._viewer:
            return
        menus = self._viewer.context_menus()
        if menus.get('graph'):
            self._context_menu['graph'] = NodeGraphMenu(self, menus['graph'])
        if menus.get('nodes'):
            self._context_menu['nodes'] = NodesMenu(self, menus['nodes'])

    def _register_builtin_nodes(self):
        """
        Register the default builtin nodes to the :meth:`NodeGraph.node_factory`
        """
        self.register_node(BackdropNode, alias='Backdrop')

    def _wire_signals(self):
        """
        Connect up all the signals and slots here.
        """

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
        self._viewer.context_menu_prompt.connect(self._on_context_menu_prompt)

    def _on_context_menu_prompt(self, menu_name, node_id):
        """
        Slot function triggered just before a context menu is shown.

        Args:
            menu_name (str): context menu name.
            node_id (str): node id if triggered from the nodes context menu.
        """
        node = self.get_node_by_id(node_id)
        menu = self.get_context_menu(menu_name)
        self.context_menu_prompt.emit(menu, node)

    def _on_insert_node(self, pipe, node_id, prev_node_pos):
        """
        Slot function triggered when a selected node has collided with a pipe.

        Args:
            pipe (Pipe): collided pipe item.
            node_id (str): selected node id to insert.
            prev_node_pos (dict): previous node position. {NodeItem: [prev_x, prev_y]}
        """
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

    def _on_property_bin_changed(self, node_id, prop_name, prop_value):
        """
        called when a property widget has changed in a properties bin.
        (emits the node object, property name, property value)

        Args:
            node_id (str): node id.
            prop_name (str): node property name.
            prop_value (object): python built in types.
        """
        node = self.get_node_by_id(node_id)

        # prevent signals from causing a infinite loop.
        if node.get_property(prop_name) != prop_value:
            node.set_property(prop_name, prop_value)

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

    def _on_node_data_dropped(self, mimedata, pos):
        """
        called when data has been dropped on the viewer.

        Example Identifiers:
            URI = ngqt://path/to/node/session.graph
            URN = ngqt::node:com.nodes.MyNode1;node:com.nodes.MyNode2

        Args:
            mimedata (QtCore.QMimeData): mime data.
            pos (QtCore.QPoint): scene position relative to the drop.
        """
        uri_regex = re.compile(r'{}(?:/*)([\w/]+)(\.\w+)'.format(URI_SCHEME))
        urn_regex = re.compile(r'{}([\w\.:;]+)'.format(URN_SCHEME))
        if mimedata.hasFormat(MIME_TYPE):
            data = mimedata.data(MIME_TYPE).data().decode()
            urn_search = urn_regex.search(data)
            if urn_search:
                search_str = urn_search.group(1)
                node_ids = sorted(re.findall(r'node:([\w\.]+)', search_str))
                x, y = pos.x(), pos.y()
                for node_id in node_ids:
                    self.create_node(node_id, pos=[x, y])
                    x += 80
                    y += 80
        elif mimedata.hasFormat('text/uri-list'):
            not_supported_urls = []
            for url in mimedata.urls():
                local_file = url.toLocalFile()
                if local_file:
                    try:
                        self.import_session(local_file)
                        continue
                    except Exception as e:
                        not_supported_urls.append(url)

                url_str = url.toString()
                if url_str:
                    uri_search = uri_regex.search(url_str)
                    if uri_search:
                        path = uri_search.group(1)
                        ext = uri_search.group(2)
                        try:
                            self.import_session('{}{}'.format(path, ext))
                        except Exception as e:
                            not_supported_urls.append(url)

            if not_supported_urls:
                print(
                    'Can\'t import the following urls: \n{}'
                    .format('\n'.join(not_supported_urls))
                )
                self.data_dropped.emit(mimedata, pos)
        else:
            self.data_dropped.emit(mimedata, pos)

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
        if not (disconnected or connected):
            return

        label = 'connect node(s)' if connected else 'disconnect node(s)'
        ptypes = {PortTypeEnum.IN.value: 'inputs',
                  PortTypeEnum.OUT.value: 'outputs'}

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
        if not ports:
            return
        ptypes = {PortTypeEnum.IN.value: 'inputs',
                  PortTypeEnum.OUT.value: 'outputs'}
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
            NodeGraphWidget: node graph widget.
        """
        if self._widget is None:
            self._widget = NodeGraphWidget()
            self._widget.addTab(self._viewer, 'Node Graph')
            # hide the close button on the first tab.
            tab_bar = self._widget.tabBar()
            tab_flags = [
                QtWidgets.QTabBar.RightSide,
                QtWidgets.QTabBar.LeftSide
            ]
            for btn_flag in tab_flags:
                tab_btn = tab_bar.tabButton(0, btn_flag)
                if tab_btn:
                    tab_btn.deleteLater()
                    tab_bar.setTabButton(0, btn_flag, None)
            self._widget.tabCloseRequested.connect(
                self._on_close_sub_graph_tab
            )
        return self._widget

    @property
    def undo_view(self):
        """
        Returns node graph undo history list widget.

        Returns:
            PySide2.QtWidgets.QUndoView: node graph undo view.
        """
        if self._undo_view is None:
            self._undo_view = QtWidgets.QUndoView(self._undo_stack)
            self._undo_view.setWindowTitle('Undo History')
        return self._undo_view

    def cursor_pos(self):
        """
        Returns the cursor last position in the node graph.

        Returns:
            tuple(float, float): cursor x,y coordinates of the scene.
        """
        cursor_pos = self.viewer().scene_cursor_pos()
        if not cursor_pos:
            return 0.0, 0.0
        return cursor_pos.x(), cursor_pos.y()

    def toggle_node_search(self):
        """
        toggle the node search widget visibility.
        """
        if self._viewer.underMouse():
            self._viewer.tab_search_set_nodes(self._node_factory.names)
            self._viewer.tab_search_toggle()

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
            by ``NodeGraphQt`` components to get the widget use
            :attr:`NodeGraph.widget`.

        See Also:
            :attr:`NodeGraph.widget` to add the node graph widget into a
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

    def set_grid_mode(self, mode=None):
        """
        Set node graph background grid mode.

        (default: :attr:`NodeGraphQt.constants.ViewerEnum.GRID_DISPLAY_LINES`).

        See: :attr:`NodeGraphQt.constants.ViewerEnum`

        .. code-block:: python
            :linenos:

            graph = NodeGraph()
            graph.set_grid_mode(ViewerEnum.GRID_DISPLAY_DOTS.value)

        Args:
            mode (int): background style.
        """
        display_types = [
            ViewerEnum.GRID_DISPLAY_NONE.value,
            ViewerEnum.GRID_DISPLAY_DOTS.value,
            ViewerEnum.GRID_DISPLAY_LINES.value
        ]
        if mode not in display_types:
            mode = ViewerEnum.GRID_DISPLAY_LINES.value
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
        Returns the context menu for the node graph.

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
        Returns the context menu for the nodes.

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

        menu types:

            - ``"graph"`` context menu from the node graph.
            - ``"nodes"`` context menu for the nodes.

        Args:
            menu (str): menu name.

        Returns:
            NodeGraphQt.NodeGraphMenu or NodeGraphQt.NodesMenu: context menu object.
        """
        return self._context_menu.get(menu)

    def _deserialize_context_menu(self, menu, menu_data, anchor_path=None):
        """
        Populate context menu from a dictionary.

        Args:
            menu (NodeGraphQt.NodeGraphMenu or NodeGraphQt.NodesMenu):
                parent context menu.
            menu_data (list[dict] or dict): serialized menu data.
            anchor_path (str or None): directory to interpret file paths relative to (optional)
        """
        if not menu:
            raise ValueError('No context menu named: "{}"'.format(menu))

        import importlib.util
        import sys

        nodes_menu = self.get_context_menu('nodes')

        anchor = Path(anchor_path).resolve()
        if anchor.is_file():
            anchor = anchor.parent

        def build_menu_command(menu, data):
            """
            Create menu command from serialized data.

            Args:
                menu (NodeGraphQt.NodeGraphMenu or NodeGraphQt.NodesMenu):
                    menu object.
                data (dict): serialized menu command data.
            """
            func_path = Path(data['file'])
            if not func_path.is_absolute():
                func_path = anchor.joinpath(func_path)

            base_name = func_path.parent.name
            file_name = func_path.stem

            mod_name = '{}.{}'.format(base_name, file_name)

            spec = importlib.util.spec_from_file_location(mod_name, func_path)
            mod = importlib.util.module_from_spec(spec)
            sys.modules[mod_name] = mod
            spec.loader.exec_module(mod)

            cmd_func = getattr(mod, data['function_name'])
            cmd_name = data.get('label') or '<command>'
            cmd_shortcut = data.get('shortcut')
            cmd_kwargs = {'func': cmd_func, 'shortcut': cmd_shortcut}

            if menu == nodes_menu and data.get('node_type'):
                cmd_kwargs['node_type'] = data['node_type']

            menu.add_command(name=cmd_name, **cmd_kwargs)

        if isinstance(menu_data, dict):
            item_type = menu_data.get('type')
            if item_type == 'separator':
                menu.add_separator()
            elif item_type == 'command':
                build_menu_command(menu, menu_data)
            elif item_type == 'menu':
                sub_menu = menu.add_menu(menu_data['label'])
                items = menu_data.get('items', [])
                self._deserialize_context_menu(sub_menu, items, anchor_path)
        elif isinstance(menu_data, list):
            for item_data in menu_data:
                self._deserialize_context_menu(menu, item_data, anchor_path)

    def set_context_menu(self, menu_name, data, anchor_path=None):
        """
        Populate a context menu from serialized data.

        example of serialized menu data:

        .. highlight:: python
        .. code-block:: python

            [
                {
                    'type': 'menu',
                    'label': 'node sub menu',
                    'items': [
                        {
                            'type': 'command',
                            'label': 'test command',
                            'file': '../path/to/my/test_module.py',
                            'function': 'run_test',
                            'node_type': 'nodeGraphQt.nodes.MyNodeClass'
                        },

                    ]
                },
            ]

        the ``run_test`` example function:

        .. highlight:: python
        .. code-block:: python

            def run_test(graph):
                print(graph.selected_nodes())


        Args:
            menu_name (str): name of the parent context menu to populate under.
            data (dict): serialized menu data.
            anchor_path (str or None): directory to interpret file paths relative to (optional)
        """
        context_menu = self.get_context_menu(menu_name)
        self._deserialize_context_menu(context_menu, data, anchor_path)

    def set_context_menu_from_file(self, file_path, menu='graph'):
        """
        Populate a context menu from a serialized json file.

        menu types:

            - ``"graph"`` context menu from the node graph.
            - ``"nodes"`` context menu for the nodes.

        Args:
            menu (str): name of the parent context menu to populate under.
            file_path (str): serialized menu commands json file.
        """
        file = Path(file_path).resolve()

        menu = menu or 'graph'
        if not file.is_file():
            raise IOError('file doesn\'t exist: "{}"'.format(file))

        with file.open(encoding='utf8') as f:
            data = json.load(f)
        context_menu = self.get_context_menu(menu)
        self._deserialize_context_menu(context_menu, data, file)

    def disable_context_menu(self, disabled=True, name='all'):
        """
        Disable/Enable context menus from the node graph.

        menu types:

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

    def set_acyclic(self, mode=True):
        """
        Enable the node graph to be a acyclic graph. (default: ``True``)

        See Also:
            :meth:`NodeGraph.acyclic`

        Args:
            mode (bool): true to enable acyclic.
        """
        self._model.acyclic = mode
        self._viewer.acyclic = self._model.acyclic

    def pipe_collision(self):
        """
        Returns if pipe collision is enabled.

        See Also:
            To enable/disable pipe collision
            :meth:`NodeGraph.set_pipe_collision`

        Returns:
            bool: True if pipe collision is enabled.
        """
        return self._model.pipe_collision

    def set_pipe_collision(self, mode=True):
        """
        Enable/Disable pipe collision.

        When enabled dragging a node over a pipe will allow the node to be
        inserted as a new connection between the pipe.

        See Also:
            :meth:`NodeGraph.pipe_collision`

        Args:
            mode (bool): False to disable pipe collision.
        """
        self._model.pipe_collision = mode
        self._viewer.pipe_collision = self._model.pipe_collision

    def pipe_slicing(self):
        """
        Returns if pipe slicing is enabled.

        See Also:
            To enable/disable pipe slicer
            :meth:`NodeGraph.set_pipe_slicing`

        Returns:
            bool: True if pipe slicing is enabled.
        """
        return self._model.pipe_slicing

    def set_pipe_slicing(self, mode=True):
        """
        Enable/Disable pipe slicer.

        When set to true holding down ``Alt + Shift + LMB Drag`` will allow node
        pipe connections to be sliced.

        .. image:: ../_images/slicer.png
            :width: 400px

        See Also:
            :meth:`NodeGraph.pipe_slicing`

        Args:
            mode (bool): False to disable the slicer pipe.
        """
        self._model.pipe_slicing = mode
        self._viewer.pipe_slicing = self._model.pipe_slicing

    def pipe_style(self):
        """
        Returns the current pipe layout style.

        See Also:
            :meth:`NodeGraph.set_pipe_style`

        Returns:
            int: pipe style value. :attr:`NodeGraphQt.constants.PipeLayoutEnum`
        """
        return self._model.pipe_style

    def set_pipe_style(self, style=PipeLayoutEnum.CURVED.value):
        """
        Set node graph pipes to be drawn as curved `(default)`, straight or angled.

        .. code-block:: python
            :linenos:

            graph = NodeGraph()
            graph.set_pipe_style(PipeLayoutEnum.CURVED.value)

        See: :attr:`NodeGraphQt.constants.PipeLayoutEnum`

        .. image:: ../_images/pipe_layout_types.gif
            :width: 80%


        Args:
            style (int): pipe layout style.
        """
        pipe_max = max([PipeLayoutEnum.CURVED.value,
                        PipeLayoutEnum.STRAIGHT.value,
                        PipeLayoutEnum.ANGLE.value])
        style = style if 0 <= style <= pipe_max else PipeLayoutEnum.CURVED.value
        self._model.pipe_style = style
        self._viewer.set_pipe_layout(style)

    def layout_direction(self):
        """
        Return the current node graph layout direction.

        `Implemented in` ``v0.3.0``

        See Also:
            :meth:`NodeGraph.set_layout_direction`

        Returns:
            int: layout direction.
        """
        return self._model.layout_direction

    def set_layout_direction(self, direction):
        """
        Sets the node graph layout direction to horizontal or vertical.
        This function will also override the layout direction on all
        nodes in the current node graph.

        `Implemented in` ``v0.3.0``

        **Layout Types:**

        - :attr:`NodeGraphQt.constants.LayoutDirectionEnum.HORIZONTAL`
        - :attr:`NodeGraphQt.constants.LayoutDirectionEnum.VERTICAL`

        .. image:: ../_images/layout_direction_switch.gif
            :width: 300px

        Warnings:
            This function does not register to the undo stack.

        See Also:
            :meth:`NodeGraph.layout_direction`,
            :meth:`NodeObject.set_layout_direction`

        Args:
            direction (int): layout direction.
        """
        direction_types = [e.value for e in LayoutDirectionEnum]
        if direction not in direction_types:
            direction = LayoutDirectionEnum.HORIZONTAL.value
        self._model.layout_direction = direction
        for node in self.all_nodes():
            node.set_layout_direction(direction)
        self._viewer.set_layout_direction(direction)

    def fit_to_selection(self):
        """
        Sets the zoom level to fit selected nodes.
        If no nodes are selected then all nodes in the graph will be framed.
        """
        nodes = self.selected_nodes() or self.all_nodes()
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
        nodes = nodes or []
        self._viewer.center_selection([n.view for n in nodes])

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
            node (type[NodeGraphQt.NodeObject]): node object.
            alias (str): custom alias name for the node type.
        """
        self._node_factory.register_node(node, alias)
        self._viewer.rebuild_tab_search()
        self.nodes_registered.emit([node])

    def register_nodes(self, nodes):
        """
        Register the nodes to the :meth:`NodeGraph.node_factory`

        Args:
            nodes (list): list of nodes.
        """
        [self._node_factory.register_node(n) for n in nodes]
        self._viewer.rebuild_tab_search()
        self.nodes_registered.emit(nodes)

    def create_node(self, node_type, name=None, selected=True, color=None,
                    text_color=None, pos=None, push_undo=True):
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
            push_undo (bool): register the command to the undo stack. (default: True)

        Returns:
            BaseNode: the created instance of the node.
        """
        node = self._node_factory.create_node_instance(node_type)
        if node:
            node._graph = self
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

            accept_types = node.model.__dict__.pop(
                '_TEMP_accept_connection_types'
            )
            for ptype, pdata in accept_types.get(node.type_, {}).items():
                for pname, accept_data in pdata.items():
                    for accept_ntype, accept_ndata in accept_data.items():
                        for accept_ptype, accept_pnames in accept_ndata.items():
                            for accept_pname in accept_pnames:
                                self._model.add_port_accept_connection_type(
                                    port_name=pname,
                                    port_type=ptype,
                                    node_type=node.type_,
                                    accept_pname=accept_pname,
                                    accept_ptype=accept_ptype,
                                    accept_ntype=accept_ntype
                                )
            reject_types = node.model.__dict__.pop(
                '_TEMP_reject_connection_types'
            )
            for ptype, pdata in reject_types.get(node.type_, {}).items():
                for pname, reject_data in pdata.items():
                    for reject_ntype, reject_ndata in reject_data.items():
                        for reject_ptype, reject_pnames in reject_ndata.items():
                            for reject_pname in reject_pnames:
                                self._model.add_port_reject_connection_type(
                                    port_name=pname,
                                    port_type=ptype,
                                    node_type=node.type_,
                                    reject_pname=reject_pname,
                                    reject_ptype=reject_ptype,
                                    reject_ntype=reject_ntype
                                )

            node.NODE_NAME = self.get_unique_name(name or node.NODE_NAME)
            node.model.name = node.NODE_NAME
            node.model.selected = selected

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

            # initial node direction layout.
            node.model.layout_direction = self.layout_direction()

            node.update()

            undo_cmd = NodeAddedCmd(
                self, node, pos=node.model.pos, emit_signal=True
            )
            if push_undo:
                undo_label = 'create node: "{}"'.format(node.NODE_NAME)
                self._undo_stack.beginMacro(undo_label)
                for n in self.selected_nodes():
                    n.set_property('selected', False, push_undo=True)
                self._undo_stack.push(undo_cmd)
                self._undo_stack.endMacro()
            else:
                for n in self.selected_nodes():
                    n.set_property('selected', False, push_undo=False)
                undo_cmd.redo()

            return node

        raise NodeCreationError('Can\'t find node: "{}"'.format(node_type))

    def add_node(self, node, pos=None, selected=True, push_undo=True, inherite_graph_style=True):
        """
        Add a node into the node graph.
        unlike the :meth:`NodeGraph.create_node` function this will not
        trigger the :attr:`NodeGraph.node_created` signal.

        Args:
            node (NodeGraphQt.BaseNode): node object.
            pos (list[float]): node x,y position. (optional)
            selected (bool): node selected state. (optional)
            push_undo (bool): register the command to the undo stack. (default: True)
            inherite_graph_style (bool): when True the node will inherite the
                node graph layout direction. (default: True)
        """
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

        accept_types = node.model.__dict__.pop(
            '_TEMP_accept_connection_types'
        )
        for ptype, pdata in accept_types.get(node.type_, {}).items():
            for pname, accept_data in pdata.items():
                for accept_ntype, accept_ndata in accept_data.items():
                    for accept_ptype, accept_pnames in accept_ndata.items():
                        for accept_pname in accept_pnames:
                            self._model.add_port_accept_connection_type(
                                port_name=pname,
                                port_type=ptype,
                                node_type=node.type_,
                                accept_pname=accept_pname,
                                accept_ptype=accept_ptype,
                                accept_ntype=accept_ntype
                            )
        reject_types = node.model.__dict__.pop(
            '_TEMP_reject_connection_types'
        )
        for ptype, pdata in reject_types.get(node.type_, {}).items():
            for pname, reject_data in pdata.items():
                for reject_ntype, reject_ndata in reject_data.items():
                    for reject_ptype, reject_pnames in reject_ndata.items():
                        for reject_pname in reject_pnames:
                            self._model.add_port_reject_connection_type(
                                port_name=pname,
                                port_type=ptype,
                                node_type=node.type_,
                                reject_pname=reject_pname,
                                reject_ptype=reject_ptype,
                                reject_ntype=reject_ntype
                            )

        node._graph = self
        node.NODE_NAME = self.get_unique_name(node.NODE_NAME)
        node.model._graph_model = self.model
        node.model.name = node.NODE_NAME

        # initial node direction layout.
        if inherite_graph_style:
            node.model.layout_direction = self.layout_direction()

        # update method must be called before it's been added to the viewer.
        node.update()

        undo_cmd = NodeAddedCmd(self, node, pos=pos, emit_signal=False)
        if push_undo:
            self._undo_stack.beginMacro('add node: "{}"'.format(node.name()))
            self._undo_stack.push(undo_cmd)
            if selected:
                node.set_selected(True)
            self._undo_stack.endMacro()
        else:
            undo_cmd.redo()

    def delete_node(self, node, push_undo=True):
        """
        Remove the node from the node graph.

        Args:
            node (NodeGraphQt.BaseNode): node object.
            push_undo (bool): register the command to the undo stack. (default: True)
        """
        assert isinstance(node, NodeObject), \
            'node must be a instance of a NodeObject.'
        node_id = node.id
        if push_undo:
            self._undo_stack.beginMacro('delete node: "{}"'.format(node.name()))

        if isinstance(node, BaseNode):
            for p in node.input_ports():
                if p.locked():
                    p.set_locked(False,
                                 connected_ports=False,
                                 push_undo=push_undo)
                p.clear_connections(push_undo=push_undo)
            for p in node.output_ports():
                if p.locked():
                    p.set_locked(False,
                                 connected_ports=False,
                                 push_undo=push_undo)
                p.clear_connections(push_undo=push_undo)

        # collapse group node before removing.
        if isinstance(node, GroupNode) and node.is_expanded:
            node.collapse()

        undo_cmd = NodesRemovedCmd(self, [node], emit_signal=True)
        if push_undo:
            self._undo_stack.push(undo_cmd)
            self._undo_stack.endMacro()
        else:
            undo_cmd.redo()

    def remove_node(self, node, push_undo=True):
        """
        Remove the node from the node graph.

        unlike the :meth:`NodeGraph.delete_node` function this will not
        trigger the :attr:`NodeGraph.nodes_deleted` signal.

        Args:
            node (NodeGraphQt.BaseNode): node object.
            push_undo (bool): register the command to the undo stack. (default: True)

        """
        assert isinstance(node, NodeObject), 'node must be a Node instance.'

        if push_undo:
            self._undo_stack.beginMacro('delete node: "{}"'.format(node.name()))

        # collapse group node before removing.
        if isinstance(node, GroupNode) and node.is_expanded:
            node.collapse()

        if isinstance(node, BaseNode):
            for p in node.input_ports():
                if p.locked():
                    p.set_locked(False,
                                 connected_ports=False,
                                 push_undo=push_undo)
                p.clear_connections(push_undo=push_undo)
            for p in node.output_ports():
                if p.locked():
                    p.set_locked(False,
                                 connected_ports=False,
                                 push_undo=push_undo)
                p.clear_connections(push_undo=push_undo)

        undo_cmd = NodesRemovedCmd(self, [node], emit_signal=False)
        if push_undo:
            self._undo_stack.push(undo_cmd)
            self._undo_stack.endMacro()
        else:
            undo_cmd.redo()

    def delete_nodes(self, nodes, push_undo=True):
        """
        Remove a list of specified nodes from the node graph.

        Args:
            nodes (list[NodeGraphQt.BaseNode]): list of node instances.
            push_undo (bool): register the command to the undo stack. (default: True)
        """
        if not nodes:
            return
        if len(nodes) == 1:
            self.delete_node(nodes[0], push_undo=push_undo)
            return
        node_ids = [n.id for n in nodes]
        if push_undo:
            self._undo_stack.beginMacro(
                'deleted "{}" node(s)'.format(len(nodes))
            )
        for node in nodes:

            # collapse group node before removing.
            if isinstance(node, GroupNode) and node.is_expanded:
                node.collapse()

            if isinstance(node, BaseNode):
                for p in node.input_ports():
                    if p.locked():
                        p.set_locked(False,
                                     connected_ports=False,
                                     push_undo=push_undo)
                    p.clear_connections(push_undo=push_undo)
                for p in node.output_ports():
                    if p.locked():
                        p.set_locked(False,
                                     connected_ports=False,
                                     push_undo=push_undo)
                    p.clear_connections(push_undo=push_undo)

        undo_cmd = NodesRemovedCmd(self, nodes, emit_signal=True)
        if push_undo:
            self._undo_stack.push(undo_cmd)
            self._undo_stack.endMacro()
        else:
            undo_cmd.redo()

        self.nodes_deleted.emit(node_ids)

    def extract_nodes(self, nodes, push_undo=True, prompt_warning=True):
        """
        Extract select nodes from its connections.

        Args:
            nodes (list[NodeGraphQt.BaseNode]): list of node instances.
            push_undo (bool): register the command to the undo stack. (default: True)
            prompt_warning (bool): prompt warning dialog box.
        """
        if not nodes:
            return

        locked_ports = []
        base_nodes = []
        for node in nodes:
            if not isinstance(node, BaseNode):
                continue

            for port in node.input_ports() + node.output_ports():
                if port.locked():
                    locked_ports.append('{0.node.name}: {0.name}'.format(port))

            base_nodes.append(node)

        if locked_ports:
            message = (
                'Selected nodes cannot be extracted because the following '
                'ports are locked:\n{}'.format('\n'.join(sorted(locked_ports)))
            )
            if prompt_warning:
                self._viewer.message_dialog(message, 'Can\'t Extract Nodes')
            return

        if push_undo:
            self._undo_stack.beginMacro(
                'extracted "{}" node(s)'.format(len(nodes))
            )

        for node in base_nodes:
            for port in node.input_ports() + node.output_ports():
                for connected_port in port.connected_ports():
                    if connected_port.node() in base_nodes:
                        continue
                    port.disconnect_from(connected_port, push_undo=push_undo)

        if push_undo:
            self._undo_stack.endMacro()

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

    def selected_pipes(self):
        """
        Return all selected pipes that are in the node graph.

        Returns:
            list[tuple[NodeGraphQt.Port,NodeGraphQt.Port]]: list of port tuples
        """
        pipes = []
        ptypes = {PortTypeEnum.IN.value: "inputs", PortTypeEnum.OUT.value: "outputs"}

        for item in self._viewer.selected_pipes():
            p1_view = item.input_port
            p2_view = item.output_port

            node1 = self._model.nodes[p1_view.node.id]
            node2 = self._model.nodes[p2_view.node.id]

            port1 = getattr(node1, ptypes[p1_view.port_type])()[p1_view.name]
            port2 = getattr(node2, ptypes[p2_view.port_type])()[p2_view.name]

            pipe = (port1, port2)
            pipes.append(pipe)
        return pipes
    
    def select_all(self):
        """
        Select all nodes in the node graph.
        """
        self._undo_stack.beginMacro('select all')
        [node.set_selected(True) for node in self.all_nodes()]
        self._undo_stack.endMacro()

    def clear_selection(self):
        """
        Clears the selection in the node graph.
        """
        self._undo_stack.beginMacro('clear selection')
        [node.set_selected(False) for node in self.all_nodes()]
        self._undo_stack.endMacro()

    def invert_selection(self):
        """
        Inverts the current node selection.
        """
        if not self.selected_nodes():
            self.select_all()
            return
        self._undo_stack.beginMacro('invert selection')
        for node in self.all_nodes():
            node.set_selected(not node.selected())
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

    def get_node_by_name(self, name):
        """
        Returns node that matches the name.

        Args:
            name (str): name of the node.
        Returns:
            NodeGraphQt.NodeObject: node object.
        """
        for node_id, node in self._model.nodes.items():
            if node.name() == name:
                return node

    def get_nodes_by_type(self, node_type):
        """
        Return all nodes by their node type identifier.
        (see: :attr:`NodeGraphQt.NodeObject.type_`)

        Args:
            node_type (str): node type identifier.

        Returns:
            list[NodeGraphQt.NodeObject]: list of nodes.
        """
        return [n for n in self._model.nodes.values() if n.type_ == node_type]

    def get_unique_name(self, name):
        """
        Creates a unique node name to avoid having nodes with the same name.

        Args:
            name (str): node name.

        Returns:
            str: unique node name.
        """
        name = ' '.join(name.split())
        node_names = [n.name() for n in self.all_nodes()]
        if name not in node_names:
            return name

        regex = re.compile(r'\w+ (\d+)$')
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
        nodes = self.all_nodes()
        for n in nodes:
            if isinstance(n, BaseNode):
                for p in n.input_ports():
                    if p.locked():
                        p.set_locked(False, connected_ports=False)
                    p.clear_connections()
                for p in n.output_ports():
                    if p.locked():
                        p.set_locked(False, connected_ports=False)
                    p.clear_connections()
        self._undo_stack.push(NodesRemovedCmd(self, nodes))
        self._undo_stack.clear()
        self._model.session = ''

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
        serial_data['graph']['layout_direction'] = self.layout_direction()
        serial_data['graph']['acyclic'] = self.acyclic()
        serial_data['graph']['pipe_collision'] = self.pipe_collision()
        serial_data['graph']['pipe_slicing'] = self.pipe_slicing()
        serial_data['graph']['pipe_style'] = self.pipe_style()

        # connection constrains.
        serial_data['graph']['accept_connection_types'] = json.dumps(self.model.accept_connection_types, default=list)
        serial_data['graph']['reject_connection_types'] = json.dumps(self.model.reject_connection_types, default=list)

        # serialize nodes.
        for n in nodes:
            # update the node model.
            n.update_model()

            node_dict = n.serialize()
            nodes_data.update(node_dict)

        for n_id, n_data in nodes_data.items():
            serial_data['nodes'][n_id] = n_data

            # serialize connections
            inputs = n_data.pop('inputs') if n_data.get('inputs') else {}
            outputs = n_data.pop('outputs') if n_data.get('outputs') else {}

            for pname, conn_data in inputs.items():
                for conn_id, prt_names in conn_data.items():
                    for conn_prt in prt_names:
                        pipe = {
                            PortTypeEnum.IN.value: [n_id, pname],
                            PortTypeEnum.OUT.value: [conn_id, conn_prt]
                        }
                        if pipe not in serial_data['connections']:
                            serial_data['connections'].append(pipe)

            for pname, conn_data in outputs.items():
                for conn_id, prt_names in conn_data.items():
                    for conn_prt in prt_names:
                        pipe = {
                            PortTypeEnum.OUT.value: [n_id, pname],
                            PortTypeEnum.IN.value: [conn_id, conn_prt]
                        }
                        if pipe not in serial_data['connections']:
                            serial_data['connections'].append(pipe)

        if not serial_data['connections']:
            serial_data.pop('connections')

        return serial_data

    def _deserialize(self, data, relative_pos=False, pos=None, adjust_graph_style=True):
        """
        deserialize node data.
        (used internally by the node graph)

        Args:
            data (dict): node data.
            relative_pos (bool): position node relative to the cursor.
            pos (tuple or list): custom x, y position.
            adjust_graph_style (bool): if true adjust the node graph properties

        Returns:
            list[NodeGraphQt.Nodes]: list of node instances.
        """
        # update node graph properties.
        
        # Recursive function to convert last lists to sets
        def convert_last_list_to_set(d):
            for key, value in d.items():
                if isinstance(value, dict):
                    convert_last_list_to_set(value)
                elif isinstance(value, list):
                    d[key] = set(value)  # convert list to set

        for attr_name, attr_value in data.get("graph", {}).items():
            if adjust_graph_style:
                if attr_name == "layout_direction":
                    self.set_layout_direction(attr_value)
                elif attr_name == "acyclic":
                    self.set_acyclic(attr_value)
                elif attr_name == "pipe_collision":
                    self.set_pipe_collision(attr_value)
                elif attr_name == "pipe_slicing":
                    self.set_pipe_slicing(attr_value)
                elif attr_name == "pipe_style":
                    self.set_pipe_style(attr_value)

            # connection constrains.
            if attr_name == 'accept_connection_types':
                attr_value = json.loads(attr_value)
                convert_last_list_to_set(attr_value)
                self.model.accept_connection_types = attr_value

            elif attr_name == 'reject_connection_types':
                attr_value = json.loads(attr_value)
                convert_last_list_to_set(attr_value)
                self.model.reject_connection_types =  attr_value

        # build the nodes.
        nodes = {}
        for n_id, n_data in data.get('nodes', {}).items():
            identifier = n_data['type_']
            node = self._node_factory.create_node_instance(identifier)
            if node:
                node.NODE_NAME = n_data.get('name', node.NODE_NAME)
                # set properties.
                for prop in node.model.properties.keys():
                    if prop in n_data.keys():
                        node.model.set_property(prop, n_data[prop])
                # set custom properties.
                for prop, val in n_data.get('custom', {}).items():
                    node.model.set_property(prop, val)
                    if isinstance(node, BaseNode):
                        if prop in node.view.widgets:
                            node.view.widgets[prop].set_value(val)

                nodes[n_id] = node
                self.add_node(node, n_data.get('pos'), inherite_graph_style=adjust_graph_style)

                if n_data.get('port_deletion_allowed', None):
                    node.set_ports({
                        'input_ports': n_data['input_ports'],
                        'output_ports': n_data['output_ports']
                    })

        # build the connections.
        for connection in data.get('connections', []):
            nid, pname = connection.get('in', ('', ''))
            in_node = nodes.get(nid) or self.get_node_by_id(nid)
            if not in_node:
                continue
            in_port = in_node.inputs().get(pname) if in_node else None

            nid, pname = connection.get('out', ('', ''))
            out_node = nodes.get(nid) or self.get_node_by_id(nid)
            if not out_node:
                continue
            out_port = out_node.outputs().get(pname) if out_node else None

            if in_port and out_port:
                # only connect if input port is not connected yet or input port
                # can have multiple connections.
                # important when duplicating nodes.
                allow_connection = any([not in_port.model.connected_ports,
                                        in_port.model.multi_connection])
                if allow_connection:
                    self._undo_stack.push(
                        PortConnectedCmd(in_port, out_port, emit_signal=False)
                    )

                # Run on_input_connected to ensure connections are fully set up
                # after deserialization.
                in_node.on_input_connected(in_port, out_port)

        node_objs = nodes.values()
        if relative_pos:
            self._viewer.move_nodes([n.view for n in node_objs])
            [setattr(n.model, 'pos', n.view.xy_pos) for n in node_objs]
        elif pos:
            self._viewer.move_nodes([n.view for n in node_objs], pos=pos)
            [setattr(n.model, 'pos', n.view.xy_pos) for n in node_objs]

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

    def deserialize_session(self, layout_data, clear_session=True,
                            clear_undo_stack=True):
        """
        Load node graph session from a dictionary object.

        See Also:
            :meth:`NodeGraph.serialize_session`,
            :meth:`NodeGraph.load_session`,
            :meth:`NodeGraph.save_session`

        Args:
            layout_data (dict): dictionary object containing a node session.
            clear_session (bool): clear current session.
            clear_undo_stack (bool): clear the undo stack.
        """
        if clear_session:
            self.clear_session()
        self._deserialize(layout_data)
        self.clear_selection()
        if clear_undo_stack:
            self._undo_stack.clear()

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
        serialized_data = self.serialize_session()
        file_path = file_path.strip()

        def default(obj):
            if isinstance(obj, set):
                return list(obj)
            return obj

        with open(file_path, 'w') as file_out:
            json.dump(
                serialized_data,
                file_out,
                indent=2,
                separators=(',', ':'),
                default=default
            )

        # update the current session.
        self._model.session = file_path

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
        file_path = file_path.strip()
        if not os.path.isfile(file_path):
            raise IOError('file does not exist: {}'.format(file_path))

        self.clear_session()
        self.import_session(file_path, clear_undo_stack=True)

    def import_session(self, file_path, clear_undo_stack=True):
        """
        Import node graph into the current session.

        Args:
            file_path (str): path to the serialized layout file.
            clear_undo_stack (bool): clear the undo stack after import.
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

        self.deserialize_session(
            layout_data,
            clear_session=False,
            clear_undo_stack=clear_undo_stack
        )
        self._model.session = file_path

        self.session_changed.emit(file_path)

    def copy_nodes(self, nodes=None):
        """
        Copy nodes to the clipboard as a JSON formatted ``str``.

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
        Cut nodes to the clipboard as a JSON formatted ``str``.

        Note:
            This function doesn't trigger the
            :attr:`NodeGraph.nodes_deleted` signal.

        See Also:
            :meth:`NodeGraph.copy_nodes`

        Args:
            nodes (list[NodeGraphQt.BaseNode]):
                list of nodes (default: selected nodes).
        """
        nodes = nodes or self.selected_nodes()
        self.copy_nodes(nodes)
        self._undo_stack.beginMacro('cut nodes')

        for node in nodes:
            if isinstance(node, BaseNode):
                for p in node.input_ports():
                    if p.locked():
                        p.set_locked(False,
                                     connected_ports=False,
                                     push_undo=True)
                    p.clear_connections()
                for p in node.output_ports():
                    if p.locked():
                        p.set_locked(False,
                                     connected_ports=False,
                                     push_undo=True)
                    p.clear_connections()

            # collapse group node before removing.
            if isinstance(node, GroupNode) and node.is_expanded:
                node.collapse()

        self._undo_stack.push(NodesRemovedCmd(self, nodes))
        self._undo_stack.endMacro()

    def paste_nodes(self, adjust_graph_style=True):
        """
        Pastes nodes copied from the clipboard.
        
        Args:
            adjust_graph_style (bool): if true adjust the node graph properties
                                        other wise only the nodes are pasted.        
        Returns:
            list[NodeGraphQt.BaseNode]: list of pasted node instances.
        """
        clipboard = QtWidgets.QApplication.clipboard()
        cb_text = clipboard.text()
        if not cb_text:
            return

        try:
            serial_data = json.loads(cb_text)
        except json.decoder.JSONDecodeError as e:
            print('ERROR: Can\'t Decode Clipboard Data:\n'
                  '"{}"'.format(cb_text))
            return

        self._undo_stack.beginMacro('pasted nodes')
        self.clear_selection()
        nodes = self._deserialize(serial_data, relative_pos=True, adjust_graph_style=adjust_graph_style)
        [n.set_selected(True) for n in nodes]
        self._undo_stack.endMacro()
        return nodes

    def duplicate_nodes(self, nodes):
        """
        Create duplicate copy from the list of nodes.

        Args:
            nodes (list[NodeGraphQt.BaseNode]): list of nodes.
        Returns:
            list[NodeGraphQt.BaseNode]: list of duplicated node instances.
        """
        if not nodes:
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
        Toggle nodes to be either disabled or enabled state.

        See Also:
            :meth:`NodeObject.set_disabled`

        Args:
            nodes (list[NodeGraphQt.BaseNode]): list of nodes.
            mode (bool): (optional) override state of the nodes.
        """
        if not nodes:
            return

        if len(nodes) == 1:
            if mode is None:
                mode = not nodes[0].disabled()
            nodes[0].set_disabled(mode)
            return

        if mode is not None:
            states = {False: 'enable', True: 'disable'}
            text = '{} ({}) nodes'.format(states[mode], len(nodes))
            self._undo_stack.beginMacro(text)
            [n.set_disabled(mode) for n in nodes]
            self._undo_stack.endMacro()
            return

        text = []
        enabled_count = len([n for n in nodes if n.disabled()])
        disabled_count = len([n for n in nodes if not n.disabled()])
        if enabled_count > 0:
            text.append('enabled ({})'.format(enabled_count))
        if disabled_count > 0:
            text.append('disabled ({})'.format(disabled_count))
        text = ' / '.join(text) + ' nodes'

        self._undo_stack.beginMacro(text)
        [n.set_disabled(not n.disabled()) for n in nodes]
        self._undo_stack.endMacro()

    def use_OpenGL(self):
        """
        Set the viewport to use QOpenGLWidget widget to draw the graph.
        """
        self._viewer.use_OpenGL()

    # auto layout node functions.
    # --------------------------------------------------------------------------

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

        node_layout_direction = self._viewer.get_layout_direction()

        if node_layout_direction is LayoutDirectionEnum.HORIZONTAL.value:
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
        elif node_layout_direction is LayoutDirectionEnum.VERTICAL.value:
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

    # convenience dialog functions.
    # --------------------------------------------------------------------------

    def question_dialog(self, text, title='Node Graph', dialog_icon=None,
                        custom_icon=None, parent=None):
        """
        Prompts a question open dialog with ``"Yes"`` and ``"No"`` buttons in
        the node graph.

        Note:
            Convenience function to
            :meth:`NodeGraph.viewer().question_dialog`

        Args:
            text (str): question text.
            title (str): dialog window title.
            dialog_icon (str): display icon. ("information", "warning", "critical")
            custom_icon (str): custom icon to display.
            parent (QtWidgets.QObject): override dialog parent. (optional)

        Returns:
            bool: true if user clicked yes.
        """
        return self._viewer.question_dialog(
            text, title, dialog_icon, custom_icon, parent
        )

    def message_dialog(self, text, title='Node Graph', dialog_icon=None,
                       custom_icon=None, parent=None):
        """
        Prompts a file open dialog in the node graph.

        Note:
            Convenience function to
            :meth:`NodeGraph.viewer().message_dialog`

        Args:
            text (str): message text.
            title (str): dialog window title.
            dialog_icon (str): display icon. ("information", "warning", "critical")
            custom_icon (str): custom icon to display.
            parent (QtWidgets.QObject): override dialog parent. (optional)
        """
        self._viewer.message_dialog(
            text, title, dialog_icon, custom_icon, parent
        )

    def load_dialog(self, current_dir=None, ext=None, parent=None):
        """
        Prompts a file open dialog in the node graph.

        Note:
            Convenience function to
            :meth:`NodeGraph.viewer().load_dialog`

        Args:
            current_dir (str): path to a directory.
            ext (str): custom file type extension (default: ``"json"``)
            parent (QtWidgets.QObject): override dialog parent. (optional)

        Returns:
            str: selected file path.
        """
        return self._viewer.load_dialog(current_dir, ext, parent)

    def save_dialog(self, current_dir=None, ext=None,  parent=None):
        """
        Prompts a file save dialog in the node graph.

        Note:
            Convenience function to
            :meth:`NodeGraph.viewer().save_dialog`

        Args:
            current_dir (str): path to a directory.
            ext (str): custom file type extension (default: ``"json"``)
            parent (QtWidgets.QObject): override dialog parent. (optional)

        Returns:
            str: selected file path.
        """
        return self._viewer.save_dialog(current_dir, ext, parent)

    # group node / sub graph.
    # --------------------------------------------------------------------------

    def _on_close_sub_graph_tab(self, index):
        """
        Called when the close button is clicked on a expanded sub graph tab.

        Args:
            index (int): tab index.
        """
        node_id = self.widget.tabToolTip(index)
        group_node = self.get_node_by_id(node_id)
        self.collapse_group_node(group_node)

    @property
    def is_root(self):
        """
        Returns if the node graph controller is the root graph.

        Returns:
            bool: true is the node graph is root.
        """
        return True

    @property
    def sub_graphs(self):
        """
        Returns expanded group node sub graphs.

        Returns:
            dict: {<node_id>: <sub_graph>}
        """
        return self._sub_graphs

    # def graph_rect(self):
    #     """
    #     Get the graph viewer range (scene size).
    #
    #     Returns:
    #         list[float]: [x, y, width, height].
    #     """
    #     return self._viewer.scene_rect()
    #
    # def set_graph_rect(self, rect):
    #     """
    #     Set the graph viewer range (scene size).
    #
    #     Args:
    #         rect (list[float]): [x, y, width, height].
    #     """
    #     self._viewer.set_scene_rect(rect)

    def expand_group_node(self, node):
        """
        Expands a group node session in a new tab.

        Args:
            node (NodeGraphQt.GroupNode): group node.

        Returns:
            SubGraph: sub node graph used to manage the group node session.
        """
        if not isinstance(node, GroupNode):
            return
        if self._widget is None:
            raise RuntimeError('NodeGraph.widget not initialized!')

        self.viewer().clear_key_state()
        self.viewer().clearFocus()

        if node.id in self._sub_graphs:
            sub_graph = self._sub_graphs[node.id]
            tab_index = self._widget.indexOf(sub_graph.widget)
            self._widget.setCurrentIndex(tab_index)
            return sub_graph

        # build new sub graph.
        node_factory = copy.deepcopy(self.node_factory)
        layout_direction = self.layout_direction()
        kwargs = {
            'layout_direction': self.layout_direction(),
            'pipe_style': self.pipe_style(),
        }
        sub_graph = SubGraph(self,
                             node=node,
                             node_factory=node_factory,
                             **kwargs)

        # populate the sub graph.
        session = node.get_sub_graph_session()
        sub_graph.deserialize_session(session)

        # store reference to expanded.
        self._sub_graphs[node.id] = sub_graph

        # open new tab at root level.
        self.widget.add_viewer(sub_graph.widget, node.name(), node.id)

        return sub_graph

    def collapse_group_node(self, node):
        """
        Collapse a group node session tab and it's expanded child sub graphs.

        Args:
            node (NodeGraphQt.GroupNode): group node.
        """
        assert isinstance(node, GroupNode), 'node must be a GroupNode instance.'
        if self._widget is None:
            return

        if node.id not in self._sub_graphs:
            err = '{} sub graph not initialized!'.format(node.name())
            raise RuntimeError(err)

        sub_graph = self._sub_graphs.pop(node.id)
        sub_graph.collapse_group_node(node)

        # remove the sub graph tab.
        self.widget.remove_viewer(sub_graph.widget)

        # TODO: delete sub graph hmm... not sure if I need this here.
        del sub_graph


class SubGraph(NodeGraph):
    """
    The ``SubGraph`` class is just like the ``NodeGraph`` but is the main
    controller for managing the expanded node graph for a
    :class:`NodeGraphQt.GroupNode`.

    .. inheritance-diagram:: NodeGraphQt.SubGraph
        :top-classes: PySide2.QtCore.QObject

    .. image:: ../_images/sub_graph.png
        :width: 70%

    -
    """

    def __init__(self, parent=None, node=None, node_factory=None, **kwargs):
        """
        Args:
            parent (object): object parent.
            node (GroupNode): group node related to this sub graph.
            node_factory (NodeFactory): override node factory.
            **kwargs (dict): additional kwargs.
        """
        super(SubGraph, self).__init__(
            parent, node_factory=node_factory, **kwargs
        )

        # sub graph attributes.
        self._node = node
        self._parent_graph = parent
        self._subviewer_widget = None

        if self._parent_graph.is_root:
            self._initialized_graphs = [self]
            self._sub_graphs[self._node.id] = self
        else:
            # delete attributes if not top level sub graph.
            del self._widget
            del self._sub_graphs

        # clone context menu from the parent node graph.
        self._clone_context_menu_from_parent()

    def __repr__(self):
        return '<{}("{}") object at {}>'.format(
            self.__class__.__name__, self._node.name(), hex(id(self)))

    def _register_builtin_nodes(self):
        """
        Register the default builtin nodes to the :meth:`NodeGraph.node_factory`
        """
        return

    def _clone_context_menu_from_parent(self):
        """
        Clone the context menus from the parent node graph.
        """
        graph_menu = self.get_context_menu('graph')
        parent_menu = self.parent_graph.get_context_menu('graph')
        parent_viewer = self.parent_graph.viewer()
        excl_actions = [parent_viewer.qaction_for_undo(),
                        parent_viewer.qaction_for_redo()]

        def clone_menu(menu, menu_to_clone):
            """
            Args:
                menu (NodeGraphQt.NodeGraphMenu):
                menu_to_clone (NodeGraphQt.NodeGraphMenu):
            """
            sub_items = []
            for item in menu_to_clone.get_items():
                if item is None:
                    menu.add_separator()
                    continue
                name = item.name()
                if isinstance(item, NodeGraphMenu):
                    sub_menu = menu.add_menu(name)
                    sub_items.append([sub_menu, item])
                    continue

                if item in excl_actions:
                    continue

                menu.add_command(
                    name,
                    func=item.slot_function,
                    shortcut=item.qaction.shortcut()
                )

            for sub_menu, to_clone in sub_items:
                clone_menu(sub_menu, to_clone)

        # duplicate the menu items.
        clone_menu(graph_menu, parent_menu)

    def _build_port_nodes(self):
        """
        Build the corresponding input & output nodes from the parent node ports
        and remove any port nodes that are outdated..

        Returns:
             tuple(dict, dict): input nodes, output nodes.
        """
        node_layout_direction = self._viewer.get_layout_direction()

        # build the parent input port nodes.
        input_nodes = {n.name(): n for n in
                       self.get_nodes_by_type(PortInputNode.type_)}
        for port in self.node.input_ports():
            if port.name() not in input_nodes:
                input_node = PortInputNode(parent_port=port)
                input_node.NODE_NAME = port.name()
                input_node.model.set_property('name', port.name())
                input_node.add_output(port.name())
                input_nodes[port.name()] = input_node
                self.add_node(input_node, selected=False, push_undo=False)
                x, y = input_node.pos()
                if node_layout_direction is LayoutDirectionEnum.HORIZONTAL.value:
                    x -= 100
                elif node_layout_direction is LayoutDirectionEnum.VERTICAL.value:
                    y -= 100
                input_node.set_property('pos', [x, y], push_undo=False)

        # build the parent output port nodes.
        output_nodes = {n.name(): n for n in
                        self.get_nodes_by_type(PortOutputNode.type_)}
        for port in self.node.output_ports():
            if port.name() not in output_nodes:
                output_node = PortOutputNode(parent_port=port)
                output_node.NODE_NAME = port.name()
                output_node.model.set_property('name', port.name())
                output_node.add_input(port.name())
                output_nodes[port.name()] = output_node
                self.add_node(output_node, selected=False, push_undo=False)
                x, y = output_node.pos()
                if node_layout_direction is LayoutDirectionEnum.HORIZONTAL.value:
                    x += 100
                elif node_layout_direction is LayoutDirectionEnum.VERTICAL.value:
                    y += 100
                output_node.set_property('pos', [x, y], push_undo=False)

        return input_nodes, output_nodes

    def _deserialize(self, data, relative_pos=False, pos=None, adjust_graph_style=True):
        """
        deserialize node data.
        (used internally by the node graph)

        Args:
            data (dict): node data.
            relative_pos (bool): position node relative to the cursor.
            pos (tuple or list): custom x, y position.
            adjust_graph_style (bool): if true adjust the node graph properties

        Returns:
            list[NodeGraphQt.Nodes]: list of node instances.
        """
        # update node graph properties.
        for attr_name, attr_value in data.get('graph', {}).items():
            if adjust_graph_style:
                if attr_name == 'acyclic':
                    self.set_acyclic(attr_value)
                elif attr_name == 'pipe_collision':
                    self.set_pipe_collision(attr_value)

        # build the port input & output nodes here.
        input_nodes, output_nodes = self._build_port_nodes()

        # build the nodes.
        nodes = {}
        for n_id, n_data in data.get('nodes', {}).items():
            identifier = n_data['type_']
            name = n_data.get('name')
            if identifier == PortInputNode.type_:
                nodes[n_id] = input_nodes[name]
                nodes[n_id].set_pos(*(n_data.get('pos') or [0, 0]))
                continue
            elif identifier == PortOutputNode.type_:
                nodes[n_id] = output_nodes[name]
                nodes[n_id].set_pos(*(n_data.get('pos') or [0, 0]))
                continue

            node = self._node_factory.create_node_instance(identifier)
            if not node:
                continue

            node.NODE_NAME = name or node.NODE_NAME
            # set properties.
            for prop in node.model.properties.keys():
                if prop in n_data.keys():
                    node.model.set_property(prop, n_data[prop])
            # set custom properties.
            for prop, val in n_data.get('custom', {}).items():
                node.model.set_property(prop, val)

            nodes[n_id] = node
            self.add_node(node, n_data.get('pos'))

            if n_data.get('port_deletion_allowed', None):
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
                self._undo_stack.push(
                    PortConnectedCmd(in_port, out_port, emit_signal=False)
                )

        node_objs = list(nodes.values())
        if relative_pos:
            self._viewer.move_nodes([n.view for n in node_objs])
            [setattr(n.model, 'pos', n.view.xy_pos) for n in node_objs]
        elif pos:
            self._viewer.move_nodes([n.view for n in node_objs], pos=pos)
            [setattr(n.model, 'pos', n.view.xy_pos) for n in node_objs]

        return node_objs

    def _on_navigation_changed(self, node_id, rm_node_ids):
        """
        Slot when the node navigation widget has changed.

        Args:
            node_id (str): selected group node id.
            rm_node_ids (list[str]): list of group node id to remove.
        """
        # collapse child sub graphs.
        for rm_node_id in rm_node_ids:
            child_node = self.sub_graphs[rm_node_id].node
            self.collapse_group_node(child_node)

        # show the selected node id sub graph.
        sub_graph = self.sub_graphs.get(node_id)
        if sub_graph:
            self.widget.show_viewer(sub_graph.subviewer_widget)
            sub_graph.viewer().setFocus()

    @property
    def is_root(self):
        """
        Returns if the node graph controller is the main root graph.

        Returns:
            bool: true is the node graph is root.
        """
        return False

    @property
    def sub_graphs(self):
        """
        Returns expanded group node sub graphs.

        Returns:
            dict: {<node_id>: <sub_graph>}
        """
        if self.parent_graph.is_root:
            return self._sub_graphs
        return self.parent_graph.sub_graphs

    @property
    def initialized_graphs(self):
        """
        Returns a list of the sub graphs in the order they were initialized.

        Returns:
            list[NodeGraphQt.SubGraph]: list of sub graph objects.
        """
        if self._parent_graph.is_root:
            return self._initialized_graphs
        return self._parent_graph.initialized_graphs

    @property
    def widget(self):
        """
        The sub graph widget from the top most sub graph.

        Returns:
            SubGraphWidget: node graph widget.
        """
        if self.parent_graph.is_root:
            if self._widget is None:
                self._widget = SubGraphWidget()
                self._widget.add_viewer(self.subviewer_widget,
                                        self.node.name(),
                                        self.node.id)
                # connect the navigator widget signals.
                navigator = self._widget.navigator
                navigator.navigation_changed.connect(
                    self._on_navigation_changed
                )
            return self._widget
        return self.parent_graph.widget

    @property
    def navigation_widget(self):
        """
        The navigation widget from the top most sub graph.

        Returns:
            NodeNavigationWidget: navigation widget.
        """
        if self.parent_graph.is_root:
            return self.widget.navigator
        return self.parent_graph.navigation_widget

    @property
    def subviewer_widget(self):
        """
        The widget to the sub graph.

        Returns:
            PySide2.QtWidgets.QWidget: node graph widget.
        """
        if self._subviewer_widget is None:
            self._subviewer_widget = QtWidgets.QWidget()
            layout = QtWidgets.QVBoxLayout(self._subviewer_widget)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(1)
            layout.addWidget(self._viewer)
        return self._subviewer_widget

    @property
    def parent_graph(self):
        """
        The parent node graph controller.

        Returns:
            NodeGraphQt.NodeGraph or NodeGraphQt.SubGraph: parent graph.
        """
        return self._parent_graph

    @property
    def node(self):
        """
        Returns the parent node to the sub graph.

        .. image:: ../_images/group_node.png
            :width: 250px

        Returns:
            NodeGraphQt.GroupNode: group node.
        """
        return self._node

    def delete_node(self, node, push_undo=True):
        """
        Remove the node from the node sub graph.

        Note:
            :class:`.PortInputNode` & :class:`.PortOutputNode` can't be deleted
            as they are connected to a :class:`.Port` to remove these port nodes
            see :meth:`BaseNode.delete_input`, :meth:`BaseNode.delete_output`.

        Args:
            node (NodeGraphQt.BaseNode): node object.
            push_undo (bool): register the command to the undo stack. (default: True)
        """
        port_nodes = self.get_input_port_nodes() + self.get_output_port_nodes()
        if node in port_nodes and node.parent_port is not None:
            # note: port nodes can only be deleted by deleting the parent
            #       port object.
            raise NodeDeletionError(
                '{} can\'t be deleted as it is attached to a port!'.format(node)
            )
        super(SubGraph, self).delete_node(node, push_undo=push_undo)

    def delete_nodes(self, nodes, push_undo=True):
        """
        Remove a list of specified nodes from the node graph.

        Args:
            nodes (list[NodeGraphQt.BaseNode]): list of node instances.
            push_undo (bool): register the command to the undo stack. (default: True)
        """
        if not nodes:
            return

        port_nodes = self.get_input_port_nodes() + self.get_output_port_nodes()
        for node in nodes:
            if node in port_nodes and node.parent_port is not None:
                # note: port nodes can only be deleted by deleting the parent
                #       port object.
                raise NodeDeletionError(
                    '{} can\'t be deleted as it is attached to a port!'
                    .format(node)
                )

        super(SubGraph, self).delete_nodes(nodes, push_undo=push_undo)

    def collapse_graph(self, clear_session=True):
        """
        Collapse the current sub graph and hide its widget.

        Args:
            clear_session (bool): clear the current session.
        """
        # update the group node.
        serialized_session = self.serialize_session()
        self.node.set_sub_graph_session(serialized_session)

        # close the visible widgets.
        if self._undo_view:
            self._undo_view.close()

        if self._subviewer_widget:
            self.widget.hide_viewer(self._subviewer_widget)

        if clear_session:
            self.clear_session()

    def expand_group_node(self, node):
        """
        Expands a group node session in current sub view.

        Args:
            node (NodeGraphQt.GroupNode): group node.

        Returns:
            SubGraph: sub node graph used to manage the group node session.
        """
        assert isinstance(node, GroupNode), 'node must be a GroupNode instance.'
        if self._subviewer_widget is None:
            raise RuntimeError('SubGraph.widget not initialized!')

        self.viewer().clear_key_state()
        self.viewer().clearFocus()

        if node.id in self.sub_graphs:
            sub_graph_viewer = self.sub_graphs[node.id].viewer()
            sub_graph_viewer.setFocus()
            return self.sub_graphs[node.id]

        # collapse expanded child sub graphs.
        group_ids = [n.id for n in self.all_nodes() if isinstance(n, GroupNode)]
        for grp_node_id, grp_sub_graph in self.sub_graphs.items():
            # collapse current group node.
            if grp_node_id in group_ids:
                grp_node = self.get_node_by_id(grp_node_id)
                self.collapse_group_node(grp_node)

            # close the widgets
            grp_sub_graph.collapse_graph(clear_session=False)

        # build new sub graph.
        node_factory = copy.deepcopy(self.node_factory)
        sub_graph = SubGraph(self,
                             node=node,
                             node_factory=node_factory,
                             layout_direction=self.layout_direction())

        # populate the sub graph.
        serialized_session = node.get_sub_graph_session()
        sub_graph.deserialize_session(serialized_session)

        # open new sub graph view.
        self.widget.add_viewer(sub_graph.subviewer_widget,
                               node.name(),
                               node.id)

        # store the references.
        self.sub_graphs[node.id] = sub_graph
        self.initialized_graphs.append(sub_graph)

        return sub_graph

    def collapse_group_node(self, node):
        """
        Collapse a group node session and it's expanded child sub graphs.

        Args:
            node (NodeGraphQt.GroupNode): group node.
        """
        # update the references.
        sub_graph = self.sub_graphs.pop(node.id, None)
        if not sub_graph:
            return

        init_idx = self.initialized_graphs.index(sub_graph) + 1
        for sgraph in reversed(self.initialized_graphs[init_idx:]):
            self.initialized_graphs.remove(sgraph)

        # collapse child sub graphs here.
        child_ids = [
            n.id for n in sub_graph.all_nodes() if isinstance(n, GroupNode)
        ]
        for child_id in child_ids:
            if self.sub_graphs.get(child_id):
                child_graph = self.sub_graphs.pop(child_id)
                child_graph.collapse_graph(clear_session=True)
                # remove child viewer widget.
                self.widget.remove_viewer(child_graph.subviewer_widget)

        sub_graph.collapse_graph(clear_session=True)
        self.widget.remove_viewer(sub_graph.subviewer_widget)

    def get_input_port_nodes(self):
        """
        Return all the port nodes related to the group node input ports.

        .. image:: ../_images/port_in_node.png
            :width: 150px

        -

        See Also:
            :meth:`NodeGraph.get_nodes_by_type`,
            :meth:`SubGraph.get_output_port_nodes`

        Returns:
            list[NodeGraphQt.PortInputNode]: input nodes.
        """
        return self.get_nodes_by_type(PortInputNode.type_)

    def get_output_port_nodes(self):
        """
        Return all the port nodes related to the group node output ports.

        .. image:: ../_images/port_out_node.png
            :width: 150px

        -

        See Also:
            :meth:`NodeGraph.get_nodes_by_type`,
            :meth:`SubGraph.get_input_port_nodes`

        Returns:
            list[NodeGraphQt.PortOutputNode]: output nodes.
        """
        return self.get_nodes_by_type(PortOutputNode.type_)

    def get_node_by_port(self, port):
        """
        Returns the node related to the parent group node port object.

        Args:
            port (NodeGraphQt.Port): parent node port object.

        Returns:
            PortInputNode or PortOutputNode: port node object.
        """
        func_type = {
            PortTypeEnum.IN.value: self.get_input_port_nodes,
            PortTypeEnum.OUT.value: self.get_output_port_nodes
        }
        for n in func_type.get(port.type_(), []):
            if port == n.parent_port:
                return n
