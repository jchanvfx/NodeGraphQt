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
            'pos': [0.0, 0.0],
            'width': NodeEnum.WIDTH.value,
            'height': NodeEnum.HEIGHT.value,
        }

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
        width = self._properties['width']
        height = self._properties['height']
        return QtCore.QRectF(0.0, 0.0, width, height)

    def mousePressEvent(self, event):
        """
        Re-implemented to update "self._properties" attribute value.
        """
        self._properties['selected'] = True
        super(NodeGraphicsItem, self).mousePressEvent(event)

    def setSelected(self, selected):
        """
        Re-implemented to update "self._properties" attribute value.
        """
        self._properties['selected'] = selected
        super(NodeGraphicsItem, self).setSelected(selected)

    def setVisible(self, visible):
        """
        Re-implemented to update "self._properties" attribute value.
        """
        self._properties['visible'] = visible
        self.setVisible(visible)

    def setPos(self, x, y):
        """
        Re-implemented to update "self._properties" attribute value.
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
        Creates a new node property for storing certain node states.

        Args:
            name (str): property name.
            value (object): property value
        """
        if name in self._properties:
            raise KeyError(
                'Can\'t add property "{}"! already defined in properties.'
            )
        self._properties[name] = None

        # this ensures we update the QGraphicsItem and set the proper value.
        self.set_property(name, value)

    def get_property(self, name):
        """
        Get the node property value.

        Args:
            name (str): property name.

        Returns:
            node property value.
        """
        return self._properties.get(name)

    def set_property(self, name, value):
        """
        Updates the node property and also the QGraphicsItem methods.

        Args:
            name (str): property name.
            value (object): property value.
        """
        if name not in self._properties.keys():
            raise KeyError('node property "{}" doesn\'t exist')

        if name == 'selected':
            self.setSelected(value)
            return
        elif name == 'visible':
            self.setVisible(value)
            return
        elif name == 'pos':
            self.setPos(*value)
            return
        elif name == 'name':
            self.setToolTip('node: {}'.format(name))

        self._properties[name] = value

    def properties(self):
        """
        return all the node property values.

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
        Deserialize a dictionary of node properties and update the node.

        Args:
            node_dict (dict): serialized node dict.
        """
        for name, property_value in node_dict.items():
            self.set_property(name, property_value)
