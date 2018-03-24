#!/usr/bin/python
from .port import Port
from ..base.node_plugin import NodePlugin
from ..widgets.node_widgets import NodeBaseWidget, NodeComboBox, NodeLineEdit


class Node(NodePlugin):

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
        self.NODE_NAME = self.item.name

    def set_icon(self, icon=None):
        """
        Set the node icon.

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

    def enable(self):
        """
        enables the node.
        """
        self.item.disabled = False

    def disable(self):
        """
        disables the node.
        """
        self.item.disabled = True

    def disabled(self):
        """
        returns weather the node is enabled or disabled.

        Returns:
            bool: true if the node is disabled.
        """
        return self.item.disabled

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
            NodeGraphQt.interfaces.Port: the created port object.
        """
        port_item = self.item.add_input(name, multi_input, display_name)
        return Port(self, port=port_item)

    def add_output(self, name='output', multi_output=True, display_name=True):
        """
        Adds a output port the the node.

        Args:
            name (str): name for the output port. 
            multi_output (bool): allow port to have more than one connection.
            display_name (bool): display the port name on the node.
             
        Returns:
            NodeGraphQt.interfaces.Port: the created port object.
        """
        port_item = self.item.add_output(name, multi_output, display_name)
        return Port(self, port=port_item)

    def add_combo_menu(self, name='', label='', items=None):
        """
        Embed a NodeComboBox widget into the node.

        Args:
            name (str): name of the widget.
            label (str): label to be displayed.
            items (list[str]): items to be added into the menu.
        """
        self.item.add_combo_menu(name, label, items)

    def add_text_input(self, name='', label='', text=''):
        """
        Embed a NodeLineEdit widget into the node.

        Args:
            name (str): name of the widget.
            label (str): label to be displayed.
            text (str): pre filled text.
        """
        self.item.add_text_input(name, label, text)

    def add_widget(self, widget):
        """
        Adds a widget into the node.

        Args:
            widget (NodeGraphQt.interfaces.NodeBaseWidget): node widget.
        """
        name = widget.name
        if not isinstance(widget, NodeBaseWidget):
            raise Exception('Object must be a instance of a NodeBaseWidget')
        if name in self.item.widgets.keys():
            raise Exception('widget name "{}" already exists'.format(name))
        self.item.add_widget(widget)

    def get_widget(self, name):
        """
        returns the node widget from the name.

        Args:
            name (str): name of the widget.

        Returns:
            NodeWidget: node widget.
        """
        if not self.item.widgets.get(name):
            raise Exception('node has no widget "{}"'.format(name))
        return self.item.all_widgets().get(name)

    def all_widgets(self):
        """
        return all node widgets.

        Returns:
            dict: {widget_name : node_widget}
        """
        return self.item.all_widgets().items()

    def add_property(self, name, value):
        """
        adds new property to the node.

        Args:
            name (str): name of the attribute.
            value (str, int, float): data
        """
        if not isinstance(value, (str, int, float)):
            raise ValueError('value must be of type (String, Integer, Float)')
        elif name in self.properties.keys():
            raise ValueError('"{}" property already exists.'.format(name))
        self.item.add_property(name, value)

    def properties(self):
        """
        Returns all the node properties.

        Returns:
            dict: a dictionary of node properties.
        """
        return self.item.properties

    def get_property(self, name):
        """
        Return the node property.

        Args:
            name (str): name of the property.

        Returns:
            str, int or float: value of the node property.
        """
        return self.item.get_property(name)

    def set_property(self, name, value):
        """
        Set the value on the node property.

        Args:
            name (str): name of the property.
            value: the new property value.
        """
        if not self.item.properties.get(name):
            raise AttributeError('node has not property "{}"'.format(name))
        if not isinstance(value, type(self.item.properties[name])):
            te = 'property "{}" value type must be of {}'
            raise TypeError(te.format(name, type(self.item.properties[name])))
        self.item.set_property(name, value)

    def has_property(self, name):
        """
        Check if node property exists.

        Args:
            name (str): name of the node.

        Returns:
            bool: true if property name exists in the Node.
        """
        return self.item.has_property(name)

    def inputs(self):
        """
        Returns all the input port for the node.
        
        Returns:
            dict: {port name: port object}
        """
        return {p.name: Port(self, p) for p in self.item.inputs}

    def outputs(self):
        """
        Returns all the output port for the node.

        Returns:
            dict: {port name: port object}
        """
        return {p.name: Port(self, p) for p in self.item.outputs}

    def input(self, index):
        """
        Return the input port with the matching name.

        Args:
            index (int): index of the input port.

        Returns:
            NodeGraphQt.interfaces.Port: port object.
        """
        return Port(self, port=self.item.inputs[index])

    def set_input(self, index, port):
        """
        Creates a connection pipe to the targeted output port.

        Args:
            index (int): index of the port.
            port (NodeGraphQt.interfaces.Port): port object.
        """
        src_port = Port(self, port=self.item.inputs[index])
        src_port.connect_to(port)

    def output(self, index):
        """
        Return the output port with the matching name.

        Args:
            index (int): index of the output port.

        Returns:
            NodeGraphQt.interfaces.Port: port object.
        """
        return Port(self, port=self.item.outputs[index])

    def set_output(self, index, port):
        """
        Creates a connection pipe to the targeted input port.

        Args:
            index (int): index of the port.
            port (NodeGraphQt.interfaces.Port): port object.
        """
        src_port = Port(self, port=self.item.outputs[index])
        src_port.connect_to(port)

    def set_x_pos(self, x=0.0):
        """
        Set the node horizontal X position in the node graph.

        Args:
            x (float): node x position:
        """
        y = self.item.pos().y()
        self.set_pos(x, y)

    def set_y_pos(self, y=0.0):
        """
        Set the node horizontal Y position in the node graph.

        Args:
            y (float): node x position:
        """
        x = self.item.pos().x()
        self.set_pos(x, y)

    def set_pos(self, x=0.0, y=0.0):
        """
        Set the node X and Y position in the node graph.
        Args:
            x (float): node X position.
            y (float): node Y position.
        """
        self.item.pos = (x, y)

    def x_pos(self):
        """
        Get the node X position in the node graph.

        Returns:
            float: x position.
        """
        return self.item.pos[0]

    def y_pos(self):
        """
        Get the node Y position in the node graph.

        Returns:
            float: y position.
        """
        return self.item.pos[1]

    def pos(self):
        """
        Get the node XY position in the node graph.

        Returns:
            tuple(float, float): x and y position.
        """
        return self.item.pos

    def delete(self):
        """
        Remove node from the Node Graph.
        """
        self.item.delete()
