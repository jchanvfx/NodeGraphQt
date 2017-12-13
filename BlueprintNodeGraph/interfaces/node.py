#!/usr/bin/python
from BlueprintNodeGraph.plugins.node_plugin import NodePlugin
from .port import Port


class Node(NodePlugin):

    NODE_NAME = 'node'
    NODE_TYPE = 'Node'

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
            BlueprintNodeGraph.interfaces.Port: the created port object.
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
            BlueprintNodeGraph.interfaces.Port: the created port object.
        """
        port_item = self.item.add_output(name, multi_output, display_name)
        return Port(self, port=port_item)

    def add_menu(self, name='', label='', items=None):
        """
        Embed a menu knob widget into the node.

        Args:
            name (str): name of the widget.
            label (str): label to be displayed.
            items (list[str]): items to be added into the menu.
        """
        self.item.add_dropdown_menu(name, label, items)

    def add_text_input(self, name='', label='', text=''):
        """
        Embed a text input knob widget into the node.

        Args:
            name (str): name of the widget.
            label (str): label to be displayed.
            text (str): pre filled text.
        """
        self.item.add_text_input(name, label, text)

    def get_widget_values(self):
        """
        return the widget values.

        Returns:
            dict: {widget_name : widget_value}
        """
        return {k: w.value for k, w in self.item.all_widgets().items()}

    def add_data(self, name, data):
        """
        add node data to the node.

        Args:
            name (str): name of the attribute.
            data (str, int, float):
        """
        if not isinstance(data, (str, int, float)):
            error = '"data" must be of type (String, Integer, Float)'
            raise ValueError(error)
        self.item.set_data(name, data)

    def has_data(self, name):
        """
        Check if node has data for name.

        Args:
            name (str): name of the node.

        Returns:
            bool: true if data name exists in the Node.
        """
        return self.item.has_data(name)

    def all_data(self):
        """
        Returns all the node data names and values.

        Returns:
            dict: a dictionary of node knob data.
        """
        return self.item.all_data()

    def get_data(self, name):
        """
        Return the node data.

        Args:
            name (str): name of the knob.

        Returns:
            str, int or float: knob data.
        """
        return self.item.get_data(name)

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
            BlueprintNodeGraph.interfaces.Port: port object.
        """
        return Port(self, port=self.item.inputs[index])

    def set_input(self, index, port):
        """
        Creates a connection pipe to the targeted output port.

        Args:
            index (int): index of the port.
            port (BlueprintNodeGraph.interfaces.Port): port object.
        """
        src_port = Port(self, port=self.item.inputs[index])
        src_port.connect_to(port)

    def output(self, index):
        """
        Return the output port with the matching name.

        Args:
            index (int): index of the output port.

        Returns:
            BlueprintNodeGraph.interfaces.Port: port object.
        """
        return Port(self, port=self.item.outputs[index])

    def set_output(self, index, port):
        """
        Creates a connection pipe to the targeted input port.

        Args:
            index (int): index of the port.
            port (BlueprintNodeGraph.interfaces.Port): port object.
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
