#!/usr/bin/python
from uuid import uuid4

from PySide import QtGui, QtCore

from .constants import Z_VAL_NODE


DEFAULT_PROPERTIES = ['id', 'icon', 'name',
                      'color', 'border_color', 'text_color',
                      'type', 'selected', 'disabled']


class NodeSkeletonItem(QtGui.QGraphicsItem):
    """
    The base skeleton of a Node.
    """

    def __init__(self, name='node', parent=None):
        super(NodeSkeletonItem, self).__init__(parent)
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
        super(NodeSkeletonItem, self).setSelected(selected)
        self._properties['selected'] = selected

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
        w, h = self.calc_size()
        self._width = width if width > w else w

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, height):
        w, h = self.calc_size()
        h = 70 if h < 70 else h
        self._height = height if height > h else h

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
        return self._properties

    def add_property(self, name, value):
        if name in DEFAULT_PROPERTIES:
            return
        self._properties[name] = value

    def get_property(self, name):
        return self._properties.get(name)

    def set_property(self, name, value):
        if not self._properties.get(name):
            raise KeyError('Node has no property "{}"'.format(name))
        if not isinstance(value, type(self._properties[name])):
            self._properties[name] = value

    def has_property(self, name):
        return name in self._properties.keys()

    def delete(self):
        if self.scene():
            self.scene().removeItem(self)
