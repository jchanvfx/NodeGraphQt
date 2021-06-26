#!/usr/bin/python
from NodeGraphQt.constants import (NODE_LAYOUT_VERTICAL,
                                   NODE_LAYOUT_HORIZONTAL)

from NodeGraphQt.nodes.base_node import BaseNode
from NodeGraphQt.qgraphics.node_group import (GroupNodeItem,
                                              GroupNodeVerticalItem)
from NodeGraphQt.qgraphics.node_group_port import (GroupPortNodeItem,
                                                   GroupPortNodeVerticalItem)


class GroupPortNode(BaseNode):

    NODE_NAME = 'GroupPort'

    def __init__(self, qgraphics_views=None):
        qgraphics_views = qgraphics_views or {
            NODE_LAYOUT_HORIZONTAL: GroupPortNodeItem,
            NODE_LAYOUT_VERTICAL: GroupPortNodeVerticalItem
        }
        super(GroupPortNode, self).__init__(qgraphics_views)


class GroupNode(BaseNode):
    """
    The ``NodeGraphQt.GroupNode`` class extends from the
    :class:``NodeGraphQt.BaseNode`` class with the ability to nest other nodes
    inside of it.

    **Inherited from:** :class:`NodeGraphQt.BaseNode`
    """

    NODE_NAME = 'Group'

    def __init__(self, qgraphics_views=None):
        qgraphics_views = qgraphics_views or {
            NODE_LAYOUT_HORIZONTAL: GroupNodeItem,
            NODE_LAYOUT_VERTICAL: GroupNodeVerticalItem
        }
        super(GroupNode, self).__init__(qgraphics_views)
        self._sub_graph = None
        self._input_port_nodes = {}
        self._output_port_nodes = {}

    @property
    def sub_graph(self):
        return self._sub_graph
