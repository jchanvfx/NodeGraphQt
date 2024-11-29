#!/usr/bin/python
from NodeGraphQt.nodes.base_node import BaseNode
from NodeGraphQt.nodes.port_node import PortInputNode, PortOutputNode
from NodeGraphQt.qgraphics.node_group import GroupNodeItem


class GroupNode(BaseNode):
    """
    `Implemented in` ``v0.2.0``

    The ``NodeGraphQt.GroupNode`` class extends from the :class:`NodeGraphQt.BaseNode`
    class with the ability to nest other nodes inside of it.

    .. inheritance-diagram:: NodeGraphQt.GroupNode

    .. image:: ../_images/group_node.png
        :width: 250px

    -
    """

    NODE_NAME = 'Group'

    def __init__(self, qgraphics_item=None):
        super(GroupNode, self).__init__(qgraphics_item or GroupNodeItem)
        self._input_port_nodes = {}
        self._output_port_nodes = {}

    @property
    def is_expanded(self):
        """
        Returns if the group node is expanded or collapsed.

        Returns:
            bool: true if the node is expanded.
        """
        if not self.graph:
            return False
        return bool(self.id in self.graph.sub_graphs)

    def get_sub_graph(self):
        """
        Returns the sub graph controller to the group node if initialized
        or returns None.

        Returns:
            SubGraph: sub graph controller.
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

        Returns:
            SubGraph: node graph used to manage the nodes expaneded session.
        """
        sub_graph = self.graph.expand_group_node(self)
        return sub_graph

    def collapse(self):
        """
        Collapse the group node session it's expanded child sub graphs.

        See Also:
            :meth:`NodeGraph.collapse_group_node`,
            :meth:`SubGraph.collapse_group_node`.
        """
        self.graph.collapse_group_node(self)

    def set_name(self, name=''):
        super(GroupNode, self).set_name(name)
        # update the tab bar and navigation labels.
        sub_graph = self.get_sub_graph()
        if sub_graph:
            nav_widget = sub_graph.navigation_widget
            nav_widget.update_label_item(self.name(), self.id)

            if sub_graph.parent_graph.is_root:
                root_graph = sub_graph.parent_graph
                tab_bar = root_graph.widget.tabBar()
                for idx in range(tab_bar.count()):
                    if tab_bar.tabToolTip(idx) == self.id:
                        tab_bar.setTabText(idx, self.name())
                        break

    def add_input(self, name='input', multi_input=False, display_name=True,
                  color=None, locked=False, painter_func=None):
        port = super(GroupNode, self).add_input(
            name=name,
            multi_input=multi_input,
            display_name=display_name,
            color=color,
            locked=locked,
            painter_func=painter_func
        )
        if self.is_expanded:
            input_node = PortInputNode(parent_port=port)
            input_node.NODE_NAME = port.name()
            input_node.model.set_property('name', port.name())
            input_node.add_output(port.name())
            sub_graph = self.get_sub_graph()
            sub_graph.add_node(input_node, selected=False, push_undo=False)

        return port

    def add_output(self, name='output', multi_output=True, display_name=True,
                   color=None, locked=False, painter_func=None):
        port = super(GroupNode, self).add_output(
            name=name,
            multi_output=multi_output,
            display_name=display_name,
            color=color,
            locked=locked,
            painter_func=painter_func
        )
        if self.is_expanded:
            output_port = PortOutputNode(parent_port=port)
            output_port.NODE_NAME = port.name()
            output_port.model.set_property('name', port.name())
            output_port.add_input(port.name())
            sub_graph = self.get_sub_graph()
            sub_graph.add_node(output_port, selected=False, push_undo=False)

        return port

    def delete_input(self, port):
        if type(port) in [int, str]:
            port = self.get_input(port)
            if port is None:
                return

        if self.is_expanded:
            sub_graph = self.get_sub_graph()
            port_node = sub_graph.get_node_by_port(port)
            if port_node:
                sub_graph.remove_node(port_node, push_undo=False)

        super(GroupNode, self).delete_input(port)

    def delete_output(self, port):
        if type(port) in [int, str]:
            port = self.get_output(port)
            if port is None:
                return

        if self.is_expanded:
            sub_graph = self.get_sub_graph()
            port_node = sub_graph.get_node_by_port(port)
            if port_node:
                sub_graph.remove_node(port_node, push_undo=False)

        super(GroupNode, self).delete_output(port)
