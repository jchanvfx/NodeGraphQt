#!/usr/bin/python
from NodeGraphQt.constants import (NODE_LAYOUT_VERTICAL,
                                   NODE_LAYOUT_HORIZONTAL)

from NodeGraphQt.nodes.base_node import BaseNode
from NodeGraphQt.qgraphics.node_group import (GroupNodeItem,
                                              GroupNodeVerticalItem)


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
        self._input_port_nodes = {}
        self._output_port_nodes = {}

    @property
    def is_expanded(self):
        """
        Returns if the group node is expanded or collapsed.

        Returns:
            bool: true if the node is expanded.
        """
        return bool(self.id in self.graph.sub_graphs)

    def get_sub_graph(self):
        """
        Returns the initialized sub node graph controller to the group node.

        Returns:
            NodeGraphQt.SubGraph or None: sub graph controller.
        """
        return self.graph.sub_graphs.get(self.id)

    def get_sub_graph_session(self):
        """
        Returns the serialized sub graph session.

        Returns:
            dict: serialized sub graph session.
        """
        return self.model.subgraph_session

    def set_sub_graph_session(self, serialized_session):
        """
        Sets the sub graph session data to the group node.

        Args:
            serialized_session (dict): serialized session.
        """
        serialized_session = serialized_session or {}
        self.model.subgraph_session = serialized_session

    def expand(self):
        """
        Expand the group node session.

        See Also:
            :meth:`NodeGraph.expand_group_node`,
            :meth:`SubGraph.expand_group_node`.
        """
        self.graph.expand_group_node(self)

    def collapse(self):
        """
        Collapse the group node session it's expanded child sub graphs.

        See Also:
            :meth:`NodeGraph.collapse_group_node`,
            :meth:`SubGraph.collapse_group_node`.
        """
        self.graph.collapse_group_node(self)
