#!/usr/bin/python
from NodeGraphQt import QtCore, QtWidgets

from NodeGraphQt.constants import Z_VAL_NODE, NODE_WIDTH, NODE_HEIGHT


class AbstractNodeItem(QtWidgets.QGraphicsItem):
    """
    The base class of all node qgraphics item.
    """

    def __init__(self, name='node', parent=None):
        super(AbstractNodeItem, self).__init__(parent)
        self.setFlags(self.ItemIsSelectable | self.ItemIsMovable)
        self.setZValue(Z_VAL_NODE)
        self._properties = {
            'id': None,
            'name': name.strip(),
            'color': (13, 18, 23, 255),
            'border_color': (46, 57, 66, 255),
            'text_color': (255, 255, 255, 180),
            'type_': 'AbstractBaseNode',
            'selected': False,
            'disabled': False,
        }
        self._width = NODE_WIDTH
        self._height = NODE_HEIGHT

    def __repr__(self):
        return '{}.{}(\'{}\')'.format(
            self.__module__, self.__class__.__name__, self.name)

    def boundingRect(self):
        return QtCore.QRectF(0.0, 0.0, self._width, self._height)

    def mousePressEvent(self, event):
        self._properties['selected'] = True
        super(AbstractNodeItem, self).mousePressEvent(event)

    def setSelected(self, selected):
        self._properties['selected'] = selected
        super(AbstractNodeItem, self).setSelected(selected)

    def pre_init(self, viewer, pos=None):
        """
        Called before node has been added into the scene.

        Args:
            viewer (NodeGraphQt.widgets.viewer.NodeViewer): main viewer.
            pos (tuple): the cursor pos if node is called with tab search.
        """
        pass

    def post_init(self, viewer, pos=None):
        """
        Called after node has been added into the scene.

        Args:
            viewer (NodeGraphQt.widgets.viewer.NodeViewer): main viewer
            pos (tuple): the cursor pos if node is called with tab search.
        """
        pass

    @property
    def id(self):
        return self._properties['id']

    @id.setter
    def id(self, unique_id=''):
        self._properties['id'] = unique_id

    @property
    def type_(self):
        return self._properties['type_']

    @type_.setter
    def type_(self, node_type='NODE'):
        self._properties['type_'] = node_type

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
    def xy_pos(self):
        return [float(self.scenePos().x()), float(self.scenePos().y())]

    @xy_pos.setter
    def xy_pos(self, pos=None):
        pos = pos or [0.0, 0.0]
        self.setPos(pos[0], pos[1])

    @property
    def name(self):
        return self._properties['name']

    @name.setter
    def name(self, name=''):
        self._properties['name'] = name
        self.setToolTip('node: {}'.format(name))

    @property
    def properties(self):
        """
        return the node view attributes.

        Returns:
            dict: {property_name: property_value}
        """
        props = {'width': self.width,
                 'height': self.height,
                 'pos':  self.xy_pos}
        props.update(self._properties)
        return props

    def viewer(self):
        """
        return the main viewer.

        Returns:
            NodeGraphQt.widgets.viewer.NodeViewer: viewer object.
        """
        if self.scene():
            return self.scene().viewer()

    def delete(self):
        """
        remove node view from the scene.
        """
        if self.scene():
            self.scene().removeItem(self)

    def from_dict(self, node_dict):
        """
        set the node view attributes from the dictionary.

        Args:
            node_dict (dict): serialized node dict.
        """
        node_attrs = list(self._properties.keys()) + ['width', 'height', 'pos']
        for name, value in node_dict.items():
            if name in node_attrs:
                if name == 'pos':
                    name = 'xy_pos'
                setattr(self, name, value)
