#!/usr/bin/python
from NodeGraphQt.constants import (NODE_LAYOUT_VERTICAL,
                                   NODE_LAYOUT_HORIZONTAL)

from NodeGraphQt.errors import PortRegistrationError
from NodeGraphQt.nodes.base_node import BaseNode
from NodeGraphQt.qgraphics.node_port_in import (PortInputNodeItem,
                                                PortInputNodeVerticalItem)
from NodeGraphQt.qgraphics.node_port_out import (PortOutputNodeItem,
                                                 PortOutputNodeVerticalItem)


class PortInputNode(BaseNode):
    """
    The ``PortInputNode`` class is the node object that represents a port from a
    :class:`NodeGraphQt.GroupNode` when expanded in a
    :class:`NodeGraphQt.SubGraph`.

    **Inherited from:** :class:`NodeGraphQt.BaseNode`

    .. image:: ../_images/port_in_node.png
        :width: 150px

    -
    """

    NODE_NAME = 'InputPort'

    def __init__(self, qgraphics_views=None, parent_port=None):
        qgraphics_views = qgraphics_views or {
            NODE_LAYOUT_HORIZONTAL: PortInputNodeItem,
            NODE_LAYOUT_VERTICAL: PortInputNodeVerticalItem
        }
        super(PortInputNode, self).__init__(qgraphics_views)
        self._parent_port = parent_port

    @property
    def parent_port(self):
        """
        The parent group node port representing this node.

        Returns:
            NodeGraphQt.Port: port object.
        """
        return self._parent_port

    def add_input(self, name='input', multi_input=False, display_name=True,
                  color=None, locked=False, painter_func=None):
        """
        This is not available for the `PortInputNode` class.
        """
        raise PortRegistrationError(
            '"{}.add_input()" is not available for {}.'
            .format(self.__class__.__name__, self)
        )

    def add_output(self, name='output', multi_output=True, display_name=True,
                   color=None, locked=False, painter_func=None):
        if self._outputs:
            raise PortRegistrationError(
                '"{}.add_output()" only ONE output is allowed for this node.'
                .format(self.__class__.__name__, self)
            )
        super(PortInputNode, self).add_output(
            name=name,
            multi_output=multi_output,
            display_name=False,
            color=color,
            locked=locked,
            painter_func=None
        )


class PortOutputNode(BaseNode):
    """
    The ``PortOutputNode`` class is the node object that represents a port from a
    :class:`NodeGraphQt.GroupNode` when expanded in a
    :class:`NodeGraphQt.SubGraph`.

    **Inherited from:** :class:`NodeGraphQt.BaseNode`

    .. image:: ../_images/port_out_node.png
        :width: 150px

    -
    """

    NODE_NAME = 'OutputPort'

    def __init__(self, qgraphics_views=None, parent_port=None):
        qgraphics_views = qgraphics_views or {
            NODE_LAYOUT_HORIZONTAL: PortOutputNodeItem,
            NODE_LAYOUT_VERTICAL: PortOutputNodeVerticalItem
        }
        super(PortOutputNode, self).__init__(qgraphics_views)
        self._parent_port = parent_port

    @property
    def parent_port(self):
        """
        The parent group node port representing this node.

        Returns:
            NodeGraphQt.Port: port object.
        """
        return self._parent_port

    def add_input(self, name='input', multi_input=False, display_name=True,
                  color=None, locked=False, painter_func=None):
        if self._inputs:
            raise PortRegistrationError(
                '"{}.add_input()" only ONE input is allowed for this node.'
                .format(self.__class__.__name__, self)
            )
        super(PortOutputNode, self).add_input(
            name=name,
            multi_input=multi_input,
            display_name=False,
            color=color,
            locked=locked,
            painter_func=None
        )

    def add_output(self, name='output', multi_output=True, display_name=True,
                   color=None, locked=False, painter_func=None):
        """
        This is not available for the `PortOutputNode` class.
        """
        raise PortRegistrationError(
            '"{}.add_output()" is not available for {}.'
            .format(self.__class__.__name__, self)
        )
