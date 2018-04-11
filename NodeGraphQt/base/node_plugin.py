#!/usr/bin/python


class NodeMeta(type):
    """
    base meta class type for a NodePlugin
    """

    def __init__(cls, name, bases, attrs):
        """
        Called when a Plugin derived class is imported
        """
        module = str(cls.__module__) + '.' + str(cls.__name__)
        cls.NODE_TYPE = module
        if cls.NODE_NAME is None:
            cls.NODE_NAME = str(cls.__name__)


class NodePlugin(object):
    """
    Base interface for a node object.
    """
    __metaclass__ = NodeMeta
    NODE_NAME = None
    NODE_TYPE = None

    def __init__(self, node=None):
        assert node, 'node cannot be None.'
        self._item = node
        self._item.type = self.type()
        self._item.name = self.NODE_NAME

    def __repr__(self):
        return '{}(\'{}\')'.format(self.NODE_TYPE, self.NODE_NAME)

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
        """
        returns the item used in the scene.
        """
        return self._item

    def id(self):
        """
        The node unique id.

        Returns:
            str: UUID of the node.
        """
        return self.item.id

    def type(self):
        """
        returns the node type.

        Returns:
            str: node type.
        """
        return self.NODE_TYPE

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

    def add_property(self, name, value):
        """
        adds new property to the node.

        Args:
            name (str): name of the attribute.
            value (str, int, float): data
        """
        if not isinstance(value, (str, int, float)):
            raise TypeError('value must be of type (String, Integer, Float)')
        elif name in self.properties.keys():
            raise KeyError('"{}" property already exists.'.format(name))
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
            raise KeyError('node has no property "{}"'.format(name))
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
