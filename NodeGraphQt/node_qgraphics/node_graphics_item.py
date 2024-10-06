#!/usr/bin/python
from Qt import QtCore, QtWidgets

from NodeGraphQt.constants import (
    Z_VAL_NODE,
    ITEM_CACHE_MODE,
    LayoutDirectionEnum,
    NodeEnum
)


class NodeGraphicsItem(QtWidgets.QGraphicsItem):
    """
    The base QGraphics item with Node properties and no paint logic.
    """

    def __init__(self, name='node', parent=None):
        super().__init__(parent)
        self.setFlags(
            QtWidgets.QGraphicsItem.ItemIsSelectable |
            QtWidgets.QGraphicsItem.ItemIsMovable
        )
        self.setCacheMode(ITEM_CACHE_MODE)
        self.setZValue(Z_VAL_NODE)
        self._properties = {
            'id': None,
            'name': name.strip(),
            'color': (13, 18, 23, 255),
            'border_color': (46, 57, 66, 255),
            'text_color': (255, 255, 255, 180),
            'type_': 'NodeGraphicsItem',
            'selected': False,
            'disabled': False,
            'visible': False,
            'layout_direction': LayoutDirectionEnum.HORIZONTAL.value,
            'pos': [0.0, 0.0]
        }
        self._width = NodeEnum.WIDTH.value
        self._height = NodeEnum.HEIGHT.value

    def __repr__(self):
        return '{}.{}(\'{}\')'.format(
            self.__module__,
            self.__class__.__name__,
            self._properties['name']
        )

    # re-implemented functions.
    # --------------------------------------------------------------------------

    def boundingRect(self):
        """
        Returns:
            QtCore.QRectF: node bounding rect.
        """
        return QtCore.QRectF(0.0, 0.0, self._width, self._height)

    def mousePressEvent(self, event):
        """
        Re-implemented to update "self._properties['selected']" attribute.

        Args:
            event (QtWidgets.QGraphicsSceneMouseEvent): mouse event.
        """
        self._properties['selected'] = True
        super(NodeGraphicsItem, self).mousePressEvent(event)

    def setSelected(self, selected):
        """
        Args:
            selected (bool):
        """
        self._properties['selected'] = selected
        super(NodeGraphicsItem, self).setSelected(selected)

    def setVisible(self, visible):
        """
        Args:
            visible (bool):
        """
        self._properties['visible'] = visible
        self.setVisible(visible)

    def setPos(self, x, y):
        """
        Args:
            x (float or int):
            y (float or int):
        """
        super().setPos(x, y)
        self._properties['pos'] = [
            float(self.scenePos().x()),
            float(self.scenePos().y())
        ]

    # NodeGraphicsItem functions.
    # --------------------------------------------------------------------------

    def draw_node(self):
        """
        Re-draw the node item in the scene with proper
        calculated size and widgets aligned.

        (this is called from the builtin custom widgets.)
        """
        return

    def pre_init(self, viewer, pos=None):
        """
        Called before node has been added into the scene.

        Args:
            viewer (NodeGraphQt.widgets.viewer.NodeViewer): main viewer.
            pos (tuple): the cursor pos if node is called with tab search.
        """
        return

    def post_init(self, viewer, pos=None):
        """
        Called after node has been added into the scene.

        Args:
            viewer (NodeGraphQt.widgets.viewer.NodeViewer): main viewer
            pos (tuple): the cursor pos if node is called with tab search.
        """
        return

    def add_property(self, name, value):
        """
        Args:
            name:
            value:
        """
        if name in self._properties:
            raise KeyError(
                'Can\'t add property "{}"! already defined in properties.'
            )
        self._properties[name] = value

    def get_property(self, name):
        """
        Args:
            name (str):

        Returns:
            node property value.
        """
        if name == 'pos':
            self._properties['pos'] = [self.pos().x(), self.pos().y()]
        elif name in ['width', 'height']:
            self._properties[name] = getattr(self.boundingRect(), name)()
        elif name == 'selected':
            self._properties[name] = self.isSelected()
        elif name == 'visible':
            self._properties[name] = self.isVisible()
        return self._properties.get(name)

    def set_property(self, name, value):
        """
        Args:
            name (str):
            value (object):
        """
        if name == 'selected':
            self.setSelected(value)
            return
        elif name == 'visible':
            self.setVisible(value)
            return

        if name == 'name':
            self.setToolTip('node: {}'.format(name))
        elif name in ['width', 'height']:
            if name == 'width':
                self._width = value
            else:
                self._height = value

        self._properties[name] = value

    def properties(self):
        """
        return the node view attributes.

        Returns:
            dict: {property_name: property_value}
        """
        refresh_properties = ['width', 'height', 'pos']
        for property_name in refresh_properties:
            self.get_property(property_name)
        return self._properties

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
        for name, property_value in node_dict.items():
            self.set_property(name, property_value)
