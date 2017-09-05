#!/usr/bin/python
from PySide import QtGui, QtCore

from node import NodeItem
from port import PortItem
from scene import NodeScene
from viewer import NodeViewer


class Port(object):

    def __init__(self, port=None):
        self._port_item = port

    def __str__(self):
        name = self.__class__.__name__
        return '{}(name={}, node={})'.format(name, self.name(), self.node())

    def name(self):
        """
        name of the port.
        
        Returns:
            str: port name.
        """
        return self._port_item.name

    def node(self):
        """
        Return the parent node of the port.
        
        Returns:
            BlueprintNodeGraph.Node: node object.
        """
        return Node(self._port_item.node)

    def type(self):
        """
        Returns the port type.
        
        Returns:
            str: 'in' for input port or 'out' for output port.
        """
        return self._port_item.port_type

    # def color(self):
    #     """
    #     Returns the default port color.
    #
    #     Returns:
    #         tuple: (r, g, b, a) from 0-255 range.
    #     """
    #     return self._port_item.color
    #
    # def set_color(self, color):
    #     """
    #     Sets the default port color in (red, green, blur, alpha) value.
    #
    #     Args:
    #         color (tuple): (r, g, b, a)
    #     """
    #     self._port_item.color = color

    def connected_ports(self):
        """
        Returns all connected ports.

        Returns:
            list[BlueprintNodeGraph.Port]: list pf connected ports.
        """
        ports = []
        for port in self._port_item.connected_ports:
            port.append(Port(port))
        return ports

    def connect_to(self, port=None):
        """
        Creates a pipe and connects it to the port with a connection.

        Args:
            port (BlueprintNodeGraph.Port): port object. 
        """
        port_item = port._port_item
        if not isinstance(port_item, PortItem):
            return
        viewer = self._port_item.scene().viewer()
        viewer.connect_ports(self._port_item, port_item)

    # def disconnect_from(self, port=None):
    #     port_item = port._port_item
    #     if not isinstance(port_item, PortItem):
    #         return



class Node(object):

    def __init__(self, name='node', node=None):
        self._node_item = node if node else NodeItem()
        self._node_item.name = name

    def __str__(self):
        name = self.__class__.__name__
        return '{}(name={}, if={})'.format(name, self.name, self.id())

    def id(self):
        """
        The node unique id.
        
        Returns:
            str: UUID of the node.
        """
        return self._node_item.id

    def name(self):
        """
        Name of the node.
        
        Returns:
            str: name of the node.
        """
        return self._node_item.name

    def set_name(self, name=''):
        """
        Set the name of the node.
        
        Args:
            name (str): name for the node.
        """
        self._node_item.name = name

    def set_icon(self, icon=None):
        """
        Set the nodes icon.

        Args:
            icon (str): path to the icon image. 
        """
        self._node_item.icon = icon

    def color(self):
        """
        Returns the node color in (red, green, blur, alpha) value.
        
        Returns:
            tuple: (r, g, b, a) from 0-255 range.
        """
        return self._node_item.color

    def set_color(self, color=(0, 0, 0, 255)):
        """
        Sets the color of the node in (red, green, blur, alpha) value.

        Args:
            color (tuple): (r, g, b, a) 
        """
        self._node_item.color = color

    def selected(self):
        """
        Returns the selected state of the node.
        
        Returns:
            bool: True if the node is selected.
        """
        return self._node_item.isSelected()

    def set_selected(self, selected=True):
        """
        Set the node to be selected or not selected.
        
        Args:
            selected (bool): True to select the node.
        """
        self._node_item.setSelected(selected)

    def add_input(self, name='input', multi_input=False):
        """
        Adds a input port the the node.
        
        Args:
            name (str): name for the input port. 
            multi_input (bool): allow port to have more than one connection.
            
        Returns:
            BlueprintNodeGraph.Port: the created port object.
        """
        port_item = self._node_item.add_input(name, multi_input)
        return Port(port_item)

    def add_output(self, name='output', multi_output=False):
        """
        Adds a output port the the node.

        Args:
            name (str): name for the output port. 
            multi_output (bool): allow port to have more than one connection.
             
        Returns:
            BlueprintNodeGraph.Port: the created port object.
        """
        port_item = self._node_item.add_output(name, multi_output)
        return Port(port_item)

    def inputs(self):
        """
        Returns all the input port for the node.
        
        Returns:
            list[BlueprintNodeGraph.Port]: a list of port objects.
        """
        ports = []
        for port in self._node_item.inputs:
            ports.append(Port(port))
        return ports

    def outputs(self):
        """
        Returns all the output port for the node.

        Returns:
            list[BlueprintNodeGraph.Port]: a list of port objects.
        """
        ports = []
        for port in self._node_item.outputs:
            ports.append(Port(port))
        return ports

    def get_input(self, name):
        for port in self._node_item.inputs:
            if port.name == name:
                return Port(port)

    def get_output(self, name):
        for port in self._node_item.outputs:
            if port.name == name:
                return Port(port)

    def x_pos(self):
        return self._node_item.x()

    def y_pos(self):
        return self._node_item.y()

    def set_x_pos(self, pos_x=0.0):
        y = self._node_item.pos().y()
        self._node_item.setPos(pos_x, y)

    def set_y_pos(self, pos_y=0.0):
        x = self._node_item.pos().x()
        self._node_item.setPos(x, pos_y)

    def delete(self):
        self._node_item.delete()


class NodeGraph(QtGui.QWidget):

    def __init__(self, parent=None):
        super(NodeGraph, self).__init__(parent)
        self.setWindowTitle('Node Graph')
        self._scene = NodeScene()
        self._viewer = NodeViewer(self, self._scene)
        layout = QtGui.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._viewer)

    def keyPressEvent(self, event):
        # TODO remove this function.
        key = event.key()
        if key == QtCore.Qt.Key_Escape:
            self.close()

    def set_pipe_layout(self, layout='curved'):
        """
        Set node graph pipes to be drawn straight or curved by default 
        all pipes are set curved.
        
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

    def center_on(self, nodes=None):
        """
        Center the node graph on the given nodes or all nodes by default.

        Args:
            nodes (list[BlueprintNodeGraph.Node]): a list of nodes.
        """
        self._viewer.center_selection(nodes)

    def save(self, path):
        """
        Save out the current node graph session with a ".ngraph" file extension.
        
        Args:
            path (str): file path to be saved. 
        """
        self._viewer.save_session(path, False)

    def load(self, path):
        """
        Open node graph session file.

        Args:
            path (str): session file path. 
        """
        self._viewer.load_session(path, False)

    def add_node(self, node):
        """
        Add a node into the node graph.
        
        Args:
            node (BlueprintNodeGraph.Node): node object. 
        """
        assert isinstance(node, Node), 'node must be a Node() object'
        self._viewer.add_node(node._node_item)

    def delete_node(self, node):
        """
        Removes the node from the node graph.
    
        Args:
            node (BlueprintNodeGraph.Node): node object. 
        """
        assert isinstance(node, Node), 'node must be a Node() object'
        node.delete()

    def all_nodes(self):
        """
        Return all nodes that are in the node graph.
        
        Returns:
            list[BlueprintNodeGraph.Node]: list of nodes.
        """
        nodes = []
        for node in self._viewer.all_nodes():
            nodes.append(Node(node=node._node_item))
        return nodes

    def selected_nodes(self):
        """
        Return all selected nodes that are in the node graph.

        Returns:
            list[BlueprintNodeGraph.Node]: list of nodes.
        """
        nodes = []
        for node in self._viewer.selected_nodes():
            nodes.append(Node(node=node._node_item))
        return nodes

    def select_all(self):
        """
        Select all nodes in the current node graph.
        """
        self._viewer.select_all_nodes()

    def clear_selection(self):
        """
        Clears the selection in the node graph.
        """
        self._viewer.clear_selection()

    def get_node(self, name):
        """
        Returns a node object that matches the name.

        Args:
            name (str): name of the node. 
        Returns:
            BlueprintNodeGraph.Node: node object.
        """
        for node_item in self._viewer.all_nodes():
            if node_item.name == name:
                return Node(node=node_item)

    def connect_node_to_node(self, from_node, from_port, to_node, to_port):
        """
        Connects a node with a matching node name and port name to another
        node with matching node name and port name.
        
        Args:
            from_node (str): name of the node.
            from_port (str): name of the node port.
            to_node (str): name of the node.
            to_port (str): name of the node port.
        """
        connection = {}
        for node_item in self._viewer.all_nodes():
            if node_item.name == from_node:
                connection[from_node] = Node(node_item)
            elif node_item.name == to_port:
                connection[to_node] = Node(node_item)
            if connection.get(from_node) and connection.get(to_node):
                break
        if not connection.get(from_node):
            raise Exception('no node named {}'.format(from_node))
        if not connection.get(to_node):
            raise Exception('no node named {}'.format(to_node))
        ports = connection[from_node].inputs() + connection[from_node].outputs()
        for port in ports:
            if port.name() == from_port:
                connection[from_port] = port
                break
        ports = connection[to_node].inputs() + connection[to_node].outputs()
        for port in ports:
            if port.name() == to_port:
                connection[to_port] = port
                break
        if not connection.get(from_port):
            raise Exception('no port {}'.format(from_port))
        if not connection.get(to_port):
            raise Exception('no port {}'.format(to_node))
        connection[from_port].connect_to(connection[to_port])
