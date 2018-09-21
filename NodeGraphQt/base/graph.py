#!/usr/bin/python
import json
import os
import re

from PySide2 import QtCore
from PySide2.QtGui import QClipboard
from PySide2.QtWidgets import QUndoStack, QAction

from NodeGraphQt.base.actions import setup_actions
from NodeGraphQt.base.commands import (NodeAddedCmd,
                                       NodeRemovedCmd,
                                       NodeMovedCmd,
                                       PortConnectedCmd)
from NodeGraphQt.base.model import NodeGraphModel
from NodeGraphQt.base.node import NodeObject
from NodeGraphQt.base.vendor import NodeVendor
from NodeGraphQt.widgets.viewer import NodeViewer


class NodeGraph(QtCore.QObject):

    def __init__(self, parent=None):
        super(NodeGraph, self).__init__(parent)
        self._model = NodeGraphModel()
        self._viewer = NodeViewer()
        self._undo_stack = QUndoStack(self)
        self._init_actions()
        self._wire_signals()

    def _wire_signals(self):
        self._viewer.moved_nodes.connect(self._on_nodes_moved)
        self._viewer.search_triggered.connect(self._on_search_triggered)
        self._viewer.connection_changed.connect(self._on_connection_changed)

    def _init_actions(self):
        # setup tab search shortcut.
        tab = QAction('Search Nodes', self)
        tab.setShortcut('tab')
        tab.triggered.connect(self._toggle_tab_search)
        self._viewer.addAction(tab)
        setup_actions(self)

    def _toggle_tab_search(self):
        """
        toggle the tab search widget.
        """
        self._viewer.tab_search_set_nodes(NodeVendor.names)
        self._viewer.tab_search_toggle()

    def _on_nodes_moved(self, node_data):
        """
        called when selected nodes in the viewer has changed position.

        Args:
            node_data (dict): {<node_view>: <previous_pos>}
        """
        self._undo_stack.beginMacro('moved nodes')
        for node_view, prev_pos in node_data.items():
            node = self._model.nodes[node_view.id]
            self._undo_stack.push(NodeMovedCmd(node, node.pos(), prev_pos))
        self._undo_stack.endMacro()

    def _on_search_triggered(self, node_type, pos):
        """
        called when the tab search widget is triggered in the viewer.

        Args:
            node_type (str): node identifier.
            pos (tuple): x,y position for the node.
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

        label = 'connected node(s)' if connected else 'disconnected node(s)'
        ptypes = {'in': 'inputs', 'out': 'outputs'}

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

    @property
    def model(self):
        """
        Return the node graph model.

        Returns:
            NodeGraphModel: model object.
        """
        return self._model

    def show(self):
        """
        Show node graph viewer widget.
        """
        self._viewer.show()

    def hide(self):
        """
        Hide node graph viewer widget.
        """
        self._viewer.hide()

    def close(self):
        """
        Close node graph viewer widget.
        """
        self._viewer.close()

    def viewer(self):
        """
        Return the node graph viewer widget object.

        Returns:
            NodeGraphQt.widgets.viewer.NodeViewer: viewer widget.
        """
        return self._viewer

    def scene(self):
        """
        Return the scene object.

        Returns:
            NodeGraphQt.widgets.scene.NodeScene: node scene.
        """
        return self._viewer.scene()

    def undo_stack(self):
        """
        Returns the undo stack used in the node graph

        Returns:
            QUndoStack: undo stack.
        """
        return self._undo_stack

    def begin_undo(self, name='undo'):
        """
        Start of an undo block followed by a end_undo().

        Args:
            name (str): name for the undo block.
        """
        self._undo_stack.beginMacro(name)

    def end_undo(self):
        """
        End of an undo block started by begin_undo().
        """
        self._undo_stack.endMacro()

    def context_menu(self):
        """
        Returns a node graph context menu object.

        Returns:
            ContextMenu: node graph context menu object instance.
        """
        return self._viewer.context_menu()

    def acyclic(self):
        """
        Returns true if the current node graph is acyclic.

        Returns:
            bool: true if acyclic.
        """
        return self._model.acyclic

    def set_acyclic(self, mode=True):
        """
        Set the node graph to be acyclic or not. (default=True)

        Args:
            mode (bool): false to disable acyclic.
        """
        self._model.acyclic = mode
        self._viewer.acyclic = mode

    def set_pipe_layout(self, layout='curved'):
        """
        Set node graph pipes to be drawn straight or curved by default
        all pipes are set curved. (default='curved')

        Args:
            layout (str): 'straight' or 'curved'
        """
        self._viewer.set_pipe_layout(layout)

    def set_zoom(self, zoom=0):
        """
        Set the zoom factor of the Node Graph the default is 0.

        Args:
            zoom (int): zoom factor max zoom out -10 max zoom in 10.
        """
        self._viewer.set_zoom(zoom)

    def get_zoom(self):
        """
        Get the current zoom level of the node graph.

        Returns:
            int: the current zoom level.
        """
        return self._viewer.get_zoom()

    def center_on(self, nodes=None):
        """
        Center the node graph on the given nodes or all nodes by default.

        Args:
            nodes (list[NodeGraphQt.Node]): a list of nodes.
        """
        self._viewer.center_selection(nodes)

    def center_selection(self):
        """
        Center the node graph on the current selected nodes.
        """
        nodes = self._viewer.selected_nodes()
        self._viewer.center_selection(nodes)

    def registered_nodes(self):
        """
        Return a list of all node types that have been registered.
        To register a node see "NodeGraphWidget.register_node()"

        Returns:
            list[str]: node types.
        """
        return sorted(NodeVendor.nodes.keys())

    def register_node(self, node, alias=None):
        """
        Register a node.

        Args:
            node (NodeGraphQt.Node): node object.
            alias (str): custom alias name for the node type.
        """
        NodeVendor.register_node(node, alias)

    def create_node(self, node_type, name=None, selected=True, color=None, pos=None):
        """
        Create a new node in the node graph.
        To list all node types see "NodeGraphWidget.registered_nodes()"

        Args:
            node_type (str): node instance type.
            name (str): set name of the node.
            selected (bool): set created node to be selected.
            color (tuple or str): node color (255, 255, 255) or '#FFFFFF'.
            pos (tuple): set position of the node (x, y).

        Returns:
            NodeGraphQt.Node: created instance of a node.
        """
        NodeInstance = NodeVendor.create_node_instance(node_type)
        if NodeInstance:
            node = NodeInstance()
            node._graph = self
            node.update()

            self._undo_stack.beginMacro('created node')
            self._undo_stack.push(NodeAddedCmd(self, node, pos))
            if name:
                node.set_name(name)
            else:
                node.set_name(node.NODE_NAME)
            if color:
                if isinstance(color, str):
                    color = color[1:] if color[0] is '#' else color
                    color = tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))
                node.set_color(*color)
            node.set_selected(selected)
            self._undo_stack.endMacro()
            return node
        raise Exception('\n\n>> Cannot find node:\t"{}"\n'.format(node_type))

    def add_node(self, node):
        """
        Add a node into the node graph.

        Args:
            node (NodeGraphQt.Node): node object.
        """
        assert isinstance(node, NodeObject), 'node must be a Node instance.'
        node._graph = self
        node.NODE_NAME = self.get_unique_name(node.NODE_NAME)
        node.model.name = node.NODE_NAME
        node.update()
        self._undo_stack.push(NodeAddedCmd(self, node))

    def delete_node(self, node):
        """
        Remove the node from the node graph.

        Args:
            node (NodeGraphQt.Node): node object.
        """
        assert isinstance(node, NodeObject), \
            'node must be a instance of a NodeObject.'
        self._undo_stack.push(NodeRemovedCmd(self, node))

    def delete_nodes(self, nodes):
        """
        Remove a list of nodes from the node graph.

        Args:
            nodes (list[NodeGraphQt.Node]): list of node instances.
        """
        self._undo_stack.beginMacro('deleted nodes')
        [self.delete_node(n) for n in nodes]
        self._undo_stack.endMacro()

    def all_nodes(self):
        """
        Return all nodes in the node graph.

        Returns:
            list[NodeGraphQt.Node]: list of nodes.
        """
        return list(self._model.nodes.values())

    def selected_nodes(self):
        """
        Return all selected nodes that are in the node graph.

        Returns:
            list[NodeGraphQt.Node]: list of nodes.
        """
        nodes = []
        for item in self._viewer.selected_nodes():
            node = self._model.nodes[item.id]
            nodes.append(node)
        return nodes

    def select_all(self):
        """
        Select all nodes in the current node graph.
        """
        self._undo_stack.beginMacro('select all')
        for node in self.all_nodes():
            node.set_selected(True)
        self._undo_stack.endMacro()

    def clear_selection(self):
        """
        Clears the selection in the node graph.
        """
        self._undo_stack.beginMacro('deselected nodes')
        for node in self.all_nodes():
            node.set_selected(False)
        self._undo_stack.endMacro()

    def get_node_by_id(self, node_id=None):
        """
        Get the node object by it's id.

        Args:
            node_id (str): node id

        Returns:
            NodeGraphQt.NodeObject: node object.
        """
        return self._model.nodes.get(node_id)

    def get_node_by_name(self, name):
        """
        Returns node object that matches the name.

        Args:
            name (str): name of the node.
        Returns:
            NodeGraphQt.Node: node object.
        """
        for node_id, node in self._model.nodes.items():
            if node.name() == name:
                return node

    def get_unique_name(self, name):
        """
        return a unique node name for the node.

        Args:
            name (str): node name.

        Returns:
            str: unique node name.
        """
        name = ' '.join(name.split())
        node_names = [n.name() for n in self.all_nodes()]
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

    def current_session(self):
        """
        returns the file path to the currently loaded session.

        Returns:
            str: path to the currently loaded session
        """
        return self._model.session

    def clear_session(self):
        """
        clear the loaded node layout session.
        """
        for n in self.all_nodes():
            self.delete_node(n)
        self._undo_stack.clear()
        self._model.session = None

    def _serialize(self, nodes):
        """
        serialize nodes to a dict.

        Args:
            nodes (list[NodeGraphQt.Nodes]): list of node instances.

        Returns:
            dict: serialized data.
        """
        serial_data = {'nodes': {}, 'connections': []}
        nodes_data = {}
        for n in nodes:
            nodes_data.update(n.model.to_dict)

        for n_id, n_data in nodes_data.items():
            serial_data['nodes'][n_id] = n_data
            inputs = n_data.pop('inputs') if n_data.get('inputs') else {}
            outputs = n_data.pop('outputs') if n_data.get('outputs') else {}

            for pname, conn_data in inputs.items():
                for conn_id, prt_names in conn_data.items():
                    for conn_prt in prt_names:
                        pipe = {'in': [n_id, pname], 'out': [conn_id, conn_prt]}
                        if pipe not in serial_data['connections']:
                            serial_data['connections'].append(pipe)

            for pname, conn_data in outputs.items():
                for conn_id, prt_names in conn_data.items():
                    for conn_prt in prt_names:
                        pipe = {'out': [n_id, pname], 'in': [conn_id, conn_prt]}
                        if pipe not in serial_data['connections']:
                            serial_data['connections'].append(pipe)

        if not serial_data['connections']:
            serial_data.pop('connections')

        return serial_data

    def _deserialize(self, data, relative_pos=False, pos=None):
        """
        deserialize node data.

        Args:
            data (dict): node data.
            relative_pos (bool): position node relative to the cursor.

        Returns:
            list[NodeGraphQt.Nodes]: list of node instances.
        """
        nodes = {}

        # build the nodes.
        for n_id, n_data in data.get('nodes', {}).items():
            identifier = n_data['type']
            NodeInstance = NodeVendor.create_node_instance(identifier)
            if NodeInstance:
                node = NodeInstance()
                node._graph = self

                name = self.get_unique_name(n_data.get('name', node.NODE_NAME))
                n_data['name'] = name

                # set properties.
                for prop, val in node.model.properties.items():
                    if prop in n_data.keys():
                        setattr(node.model, prop, n_data[prop])

                # set custom properties.
                for prop, val in n_data.get('custom', {}).items():
                    if prop in node.model.custom_properties.keys():
                        node.model.custom_properties[prop] = val

                node.update()

                self._undo_stack.push(
                    NodeAddedCmd(self, node, n_data.get('pos'))
                )
                nodes[n_id] = node

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
            [setattr(n.model, 'pos', n.view.pos) for n in node_objs]
        elif pos:
            self._viewer.move_nodes([n.view for n in node_objs], pos=pos)

        return node_objs

    def save_session(self, file_path):
        """
        Saves the current node graph session layout to a JSON formatted file.

        Args:
            file_path (str): path to the saved node layout.
        """
        serliazed_data = self._serialize(self.selected_nodes())
        file_path = file_path.strip()
        with open(file_path, 'w') as file_out:
            json.dump(serliazed_data, file_out, indent=2, separators=(',', ':'))

    def load_session(self, file_path):
        """
        Load node graph session layout file.

        Args:
            file_path (str): path to the serialized layout file.
        """
        file_path = file_path.strip()
        if not os.path.isfile(file_path):
            raise IOError('file does not exist.')

        self.clear_session()

        try:
            with open(file_path) as data_file:
                layout_data = json.load(data_file)
        except Exception as e:
            layout_data = None
            print('Cannot read data from file.\n{}'.format(e))

        if not layout_data:
            return

        self._deserialize(layout_data)
        self._undo_stack.clear()
        self._model.session = file_path

    def copy_nodes(self, nodes=None):
        """
        copy nodes to the clipboard by default this method copies
        the selected nodes from the node graph.

        Args:
            nodes (list[NodeGraphQt.Node]): list of node instances.
        """
        nodes = nodes or self.selected_nodes()
        if not nodes:
            return False
        clipboard = QClipboard()
        serial_data = self._serialize(nodes)
        serial_str = json.dumps(serial_data)
        if serial_str:
            clipboard.setText(serial_str)
            return True
        return False

    def paste_nodes(self):
        """
        Pastes nodes from the clipboard.
        """
        clipboard = QClipboard()
        cb_string = clipboard.text()
        if not cb_string:
            return

        self._undo_stack.beginMacro('pasted nodes')
        serial_data = json.loads(cb_string)
        self.clear_selection()
        nodes = self._deserialize(serial_data, True)
        [n.set_selected(True) for n in nodes]
        self._undo_stack.endMacro()

    def duplicate_nodes(self, nodes):
        """
        Create duplicates nodes.

        Args:
            nodes (list[NodeGraphQt.Node]): list of node objects.
        Returns:
            list[NodeGraphQt.Node]: list of duplicated node instances.
        """
        if not nodes:
            return

        self._undo_stack.beginMacro('duplicated nodes')

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
        Disable/Enable specified nodes.

        Args:
            nodes (list[NodeGraphQt.Node]): list of node instances.
            mode (bool): (optional) disable state of the nodes.
        """
        if not nodes:
            return
        if mode is None:
            mode = not nodes[0].disabled()
        if len(nodes) > 1:
            text = {False: 'enabled', True: 'disabled'}[mode]
            text = '{} ({}) nodes'.format(text, len(nodes))
            self._undo_stack.beginMacro(text)
            [n.set_disabled(mode) for n in nodes]
            self._undo_stack.endMacro()
            return
        nodes[0].set_disabled(mode)
