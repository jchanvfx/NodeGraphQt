#!/usr/bin/python

from .src.node import NodeItem
from .src.port import PortItem


class Port(object):
    def __init__(self, port=PortItem()):
        self._port_item = port

    def __str__(self):
        name = self.__class__.__name__
        return '{}(name={}, node={})'.format(
            name, self.name(), self.node().name()
        )

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.node().id() == other.node().id()
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.type(), self.node().id()))

    @property
    def item(self):
        return self._port_item

    def name(self):
        """
        name of the port.

        Returns:
            str: port name.
        """
        return self.item.name

    def node(self):
        """
        Return the parent node of the port.

        Returns:
            BlueprintNodeGraph.Node: node object.
        """
        return Node(self.item.node)

    def type(self):
        """
        Returns the port type.

        Returns:
            str: 'in' for input port or 'out' for output port.
        """
        return self.item.port_type

    def color(self):
        """
        Returns the default port color (red, green, blue).

        Returns:
            tuple: (r, g, b) from 0-255 range.
        """
        r, g, b, a = self.item.color
        return r, g, b

    def set_color(self, r=0, g=0, b=0):
        """
        Sets the default port color in (red, green, blur, alpha) value.

        Args:
            r (int): red value 0-255 range.
            g (int): green value 0-255 range.
            b (int): blue value 0-255 range.
        """

        self.item.color = (r, g, b, 255)

    def connected_ports(self):
        """
        Returns all connected ports.

        Returns:
            list[BlueprintNodeGraph.Port]: list pf connected ports.
        """
        return [Port(p) for p in self.item.connected_ports]

    def connect_to(self, port=None):
        """
        Creates a pipe and connects it to the port with a connection.

        Args:
            port (BlueprintNodeGraph.Port): port object.
        """
        if not port:
            for pipe in self.item.connected_pipes:
                pipe.delete()
            return

        if not isinstance(port.item, PortItem):
            return
        viewer = self.item.scene().viewer()
        viewer.connect_ports(self.item, port.item)


class Node(object):

    def __init__(self, name=None, node=None):
        self._node_item = node or NodeItem()
        self._node_item.type = self.type()
        self._node_item.name = name or 'node'

    def __str__(self):
        return '{}(name=\'{}\')'.format(self.type, self.name)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.id() == other.id()
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.type(), self.id()))

    @property
    def item(self):
        return self._node_item

    def type(self):
        """
        The class that the node belongs to.

        Returns:
            str: node class name.
        """
        return str(self.__class__.__name__)

    def id(self):
        """
        The node unique id.
        
        Returns:
            str: UUID of the node.
        """
        return self.item.id

    def name(self):
        """
        Name of the node.
        
        Returns:
            str: name of the node.
        """
        return self.item.name

    def set_name(self, name=''):
        """
        Set the name of the node.
        
        Args:
            name (str): name for the node.
        """
        self.item.name = name

    def set_icon(self, icon=None):
        """
        Set the nodes icon.

        Args:
            icon (str): path to the icon image. 
        """
        self.item.icon = icon

    def color(self):
        """
        Returns the node color in (red, green, blue) value.
        
        Returns:
            tuple: (r, g, b) from 0-255 range.
        """
        r, g, b, a = self.item.color
        return r, g, b

    def set_color(self, r=0, g=0, b=0):
        """
        Sets the color of the node in (red, green, blue) value.

        Args:
            r (int): red value 0-255 range.
            g (int): green value 0-255 range.
            b (int): blue value 0-255 range.

        """
        self.item.color = (r, g, b, 255)

    def selected(self):
        """
        Returns the selected state of the node.
        
        Returns:
            bool: True if the node is selected.
        """
        return self.item.isSelected()

    def set_selected(self, selected=True):
        """
        Set the node to be selected or not selected.

        Args:
            selected (bool): True to select the node.
        """
        self.item.setSelected(selected)

    def add_input(self, name='input', multi_input=False, display_name=True):
        """
        Adds a input port the the node.

        Args:
            name (str): name for the input port. 
            multi_input (bool): allow port to have more than one connection.
            display_name (bool): display the port name on the node.
            
        Returns:
            BlueprintNodeGraph.Port: the created port object.
        """
        port_item = self.item.add_input(name, multi_input, display_name)
        return Port(port_item)

    def add_output(self, name='output', multi_output=False, display_name=True):
        """
        Adds a output port the the node.

        Args:
            name (str): name for the output port. 
            multi_output (bool): allow port to have more than one connection.
            display_name (bool): display the port name on the node.
             
        Returns:
            BlueprintNodeGraph.Port: the created port object.
        """
        port_item = self.item.add_output(name, multi_output, display_name)
        return Port(port_item)

    def add_dropdown_menu(self, name='', label='', items=None):
        """
        (Convenience function) Adds a drop down menu into the node.

        Args:
            name (str): name of the widget.
            label (str): label to be displayed.
            items (list[str]): items to be added into the menu.
        """
        self.item.add_dropdown_menu(name, label, items)

    def add_text_input(self, name='', label='', text=''):
        """
        (Convenience function) a text input widget into the node.

        Args:
            name (str): name of the widget.
            label (str): label to be displayed.
            text (str): pre filled text.
        """
        self.item.add_text_input(name, label, text)

    def get_dropdown_menu(self, name):
        """
        Return the nodes drop down menu widget.

        Args:
            name (str): name of the node widget.

        Returns:
            DropdownMenuNodeWidget: drop down menu widget.
        """
        return self.item.dropdown_menus.get(name)

    def get_text_input(self, name):
        """
        Return the nodes text input widget.

        Args:
            name (str): name of the node widget.

        Returns:
            TextInputNodeWidget: text input widget.
        """
        return self.item.text_inputs.get(name)

    def get_widgets(self):
        """
        Returns all embedded node widgets.

        Returns:
            list[]: list of node widgets.
        """
        return self.item.widgets

    def inputs(self):
        """
        Returns all the input port for the node.
        
        Returns:
            dict: {port name: port object}
        """
        return {p.name: Port(p) for p in self.item.inputs}

    def outputs(self):
        """
        Returns all the output port for the node.

        Returns:
            dict: {port name: port object}
        """
        return {p.name: Port(p) for p in self.item.outputs}

    def input(self, index):
        """
        Return the input port with the matching name.

        Args:
            index (int): index of the input port.

        Returns:
            BlueprintNodeGraph.Port: port object.
        """
        return Port(self.item.inputs[index])

    def set_input(self, index, port):
        """
        Creates a connection pipe to the targeted output port.

        Args:
            index (int): index of the port.
            port (BlueprintNodeGraph.Port): port object.
        """
        if port.item == self.item.inputs[index]:
            return
        src_port = Port(self.item.inputs[index])
        src_port.connect_to(port)

    def output(self, index):
        """
        Return the output port with the matching name.

        Args:
            index (int): index of the output port.

        Returns:
            BlueprintNodeGraph.Port: port object.
        """
        return Port(self.item.outputs[index])

    def set_output(self, index, port):
        """
        Creates a connection pipe to the targeted input port.

        Args:
            index (int): index of the port.
            port (BlueprintNodeGraph.Port): port object.
        """
        if port.item == self.item.outputs[index]:
            return
        src_port = Port(self.item.outputs[index])
        src_port.connect_to(port)

    def set_x_pos(self, x=0.0):
        """
        Set the node horizontal X position in the node graph.

        Args:
            x (float): node x position:
        """
        y = self.item.pos().y()
        self.item.setPos(x, y)

    def set_y_pos(self, y=0.0):
        """
        Set the node horizontal Y position in the node graph.

        Args:
            y (float): node x position:
        """
        x = self.item.pos().x()
        self.item.setPos(x, y)

    def set_pos(self, x=0.0, y=0.0):
        """
        Set the node X and Y position in the node graph.
        Args:
            x (float): node X position.
            y (float): node Y position.
        """
        self.item.setPos(x, y)

    def x_pos(self):
        """
        Get the node X position in the node graph.

        Returns:
            float: x position.
        """
        return self.item.pos().x()

    def y_pos(self):
        """
        Get the node Y position in the node graph.

        Returns:
            float: y position.
        """
        return self.item.pos().y()

    def pos(self):
        """
        Get the node XY position in the node graph.

        Returns:
            tuple(float, float): x and y position.
        """
        return self.item.pos().x(), self.item.pos().y()

    def delete(self):
        """
        Remove node from the Node Graph.
        """
        self.item.delete()
