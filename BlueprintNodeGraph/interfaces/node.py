#!/usr/bin/python

from BlueprintNodeGraph.node import NodeItem

from .port import Port


class Node(object):

    def __init__(self, name='node', node=None):
        self._node_item = node if node else NodeItem()
        self._node_item.name = name

    def __str__(self):
        return '{}(name={}, if={})'.format(self.class_type, self.name, self.id())

    def class_type(self):
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
        port_item = self._node_item.add_input(name, multi_input, display_name)
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
        port_item = self._node_item.add_output(name, multi_output, display_name)
        return Port(port_item)

    def add_dropdown_menu(self, name='', label='', items=None):
        self._node_item.add_combobox(name, label, items)

    def add_text_input(self, name='', label='', text=''):
        self._node_item.add_lineedit(name, label, text)

    def dropdown_menus(self):
        return

    def text_inputs(self):
        return

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
        """
        Return the input port with the matching name.

        Args:
            name (str): name of the input port.

        Returns:
            BlueprintNodeGraph.Port: port object.
        """
        for port in self._node_item.inputs:
            if port.name == name:
                return Port(port)

    def get_output(self, name):
        """
        Return the output port with the matching name.

        Args:
            name (str): name of the output port.

        Returns:
            BlueprintNodeGraph.Port: port object.
        """
        for port in self._node_item.outputs:
            if port.name == name:
                return Port(port)

    def set_x_pos(self, x=0.0):
        y = self._node_item.pos().y()
        self._node_item.setPos(x, y)

    def set_y_pos(self, y=0.0):
        x = self._node_item.pos().x()
        self._node_item.setPos(x, y)

    def set_xy_pos(self, x=0.0, y=0.0):
        self._node_item.setPos(x, y)

    def x_pos(self):
        return self._node_item.x()

    def y_pos(self):
        return self._node_item.y()

    def delete(self):
        """
        Remove node from the Node Graph.
        """
        self._node_item.delete()
