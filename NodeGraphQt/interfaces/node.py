#!/usr/bin/python
from .port import Port
from ..base.node_plugin import NodePlugin
from ..widgets.node_base import NodeItem
from ..widgets.node_backdrop import BackdropNodeItem
from ..widgets.node_widgets import NodeBaseWidget


class Node(NodePlugin):
    """
    Base class of a Node
    """

    NODE_NAME = 'Base node'

    def __init__(self):
        super(Node, self).__init__(NodeItem())

    def set_icon(self, icon=None):
        """
        Set the node icon.

        Args:
            icon (str): path to the icon image. 
        """
        self.item.icon = icon

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

    def add_checkbox(self, name='', label='', text='', state=False):
        """
        Embed a NodeCheckBox widget into the node.

        Args:
            name (str): name of the widget.
            label (str): label to be displayed.
            text (str): QCheckBox text.
            state (bool): pre-check.
        """
        self.item.add_checkbox(name, label, text, state)

    def add_widget(self, widget):
        """
        Embed a custom widget into the node.

        Args:
            widget (NodeGraphQt.NodeBaseWidget): node widget.
        """
        name = widget.name
        if not isinstance(widget, NodeBaseWidget):
            raise TypeError('Object must be a instance of a NodeBaseWidget')
        if name in self.item.widgets.keys():
            raise KeyError('widget name "{}" already exists'.format(name))
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
            raise KeyError('node has no widget "{}"'.format(name))
        return self.item.widgets.get(name)

    def all_widgets(self):
        """
        return all node widgets.

        Returns:
            dict: {widget_name : node_widget}
        """
        return self.item.widgets

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
        Return the input port with the matching index.

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
        Return the output port with the matching index.

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


class Backdrop(NodePlugin):
    """
    Base class of a Backdrop.
    """

    NODE_NAME = 'Backdrop'

    def __init__(self):
        super(Backdrop, self).__init__(BackdropNodeItem())

    def set_text(self, text):
        """
        Sets the text to be displayed in the backdrop node.

        Args:
            text (str): text string.
        """
        self.item.text = text

    def text(self):
        """
        returns the text on the backdrop node.

        Returns:
            str: text string.
        """
        return self.item.text

    def width(self):
        """
        Returns the width of the backdrop.

        Returns:
            float: backdrop width.
        """
        return self.item.width

    def set_width(self, width):
        """
        Sets the backdrop width.

        Args:
            width (float): width size.
        """
        self.item.width = width

    def height(self):
        """
        Returns the height of the backdrop.

        Returns:
            float: backdrop height.
        """
        return self.item.height

    def set_height(self, height):
        """
        Sets the backdrop height.

        Args:
            height (float): width size.
        """
        self.item.height = height
