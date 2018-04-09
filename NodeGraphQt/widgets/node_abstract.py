#!/usr/bin/python
from uuid import uuid4

from PySide import QtGui, QtCore

from .constants import Z_VAL_NODE


DEFAULT_PROPERTIES = ['id', 'icon', 'name',
                      'color', 'border_color', 'text_color',
                      'type', 'selected', 'disabled']


class AbstractNodeItem(QtGui.QGraphicsItem):
    """
    The abstract base class of a node.
    """

    def __init__(self, name='node', parent=None):
        super(AbstractNodeItem, self).__init__(parent)
        self.setFlags(self.ItemIsSelectable | self.ItemIsMovable)
        self.setZValue(Z_VAL_NODE)
        self._properties = {
            'id': str(uuid4()),
            'icon': None,
            'name': name.strip(),
            'color': (48, 58, 69, 255),
            'border_color': (85, 100, 100, 255),
            'text_color': (255, 255, 255, 180),
            'type': 'NodeSkeleton',
            'selected': False,
            'disabled': False,
        }
        self._width = 120
        self._height = 80
        self.prev_pos = self.pos

    def __str__(self):
        return '{}.{}(\'{}\')'.format(
            self.__module__, self.__class__.__name__, self.name)

    def __repr__(self):
        return '{}.{}(\'{}\')'.format(
            self.__module__, self.__class__.__name__, self.name)

    def boundingRect(self):
        return QtCore.QRectF(0.0, 0.0, self._width, self._height)

    def setSelected(self, selected):
        super(AbstractNodeItem, self).setSelected(selected)
        self._properties['selected'] = selected

    def pre_init(self, viewer):
        """
        Called before node has been added into the scene.

        Args:
            viewer (NodeGraphQt.widgets.viewer.NodeViewer): main viewer
        """
        pass

    def post_init(self, viewer):
        """
        Called after node has been added into the scene.

        Args:
            viewer (NodeGraphQt.widgets.viewer.NodeViewer): main viewer
        """
        pass

    @property
    def id(self):
        return self._properties['id']

    @id.setter
    def id(self, unique_id=''):
        self._properties['id'] = unique_id

    @property
    def type(self):
        return self._properties['type']

    @type.setter
    def type(self, node_type='NODE'):
        self._properties['type'] = node_type

    @property
    def size(self):
        return self._width, self._height

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, width=0.0):
        self._width = width

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, height=0.0):
        self._height = height

    @property
    def color(self):
        return self._properties['color']

    @color.setter
    def color(self, color=(0, 0, 0, 255)):
        self._properties['color'] = color

    @property
    def text_color(self):
        return self._properties['text_color']

    @text_color.setter
    def text_color(self, color=(100, 100, 100, 255)):
        self._properties['text_color'] = color

    @property
    def border_color(self):
        return self._properties['border_color']

    @border_color.setter
    def border_color(self, color=(0, 0, 0, 255)):
        self._properties['border_color'] = color

    @property
    def disabled(self):
        return self._properties['disabled']

    @disabled.setter
    def disabled(self, state=False):
        self._properties['disabled'] = state

    @property
    def selected(self):
        return self.isSelected()

    @selected.setter
    def selected(self, selected=False):
        self.setSelected(selected)

    @property
    def pos(self):
        return float(self.scenePos().x()), float(self.scenePos().y())

    @pos.setter
    def pos(self, pos=(0, 0)):
        self.prev_pos = self.scenePos().x(), self.scenePos().y()
        self.setPos(pos[0], pos[1])

    @property
    def name(self):
        return self._properties['name']

    @name.setter
    def name(self, name=''):
        if self.scene():
            viewer = self.scene().viewer()
            name = viewer.get_unique_node_name(name)
        self._properties['name'] = name
        self.setToolTip('node: {}'.format(name))

    @property
    def properties(self):
        """
        Returns:
            dict: {property_name: property_value}
        """
        return self._properties

    def add_property(self, name, value):
        if name in DEFAULT_PROPERTIES:
            raise AssertionError('cannot override default properties.')
        elif name in self._properties.keys():
            raise AssertionError('property already exists.')
        self._properties[name] = value

    def get_property(self, name):
        return self._properties.get(name)

    def set_property(self, name, value):
        if not self._properties.get(name):
            raise AssertionError('Node has no property "{}"'.format(name))
        if not isinstance(value, type(self._properties[name])):
            self._properties[name] = value

    def has_property(self, name):
        return name in self._properties.keys()

    def viewer(self):
        if self.scene():
            return self.scene().viewer()

    def delete(self):
        if self.scene():
            self.scene().removeItem(self)
