PortNodes
#########

| Port nodes are the nodes in a expanded :class:`NodeGraphQt.SubGraph` that
  represent the ports from the parent :class:`NodeGraphQt.GroupNode` object.

.. autosummary::
    NodeGraphQt.nodes.port_node.PortInputNode
    NodeGraphQt.nodes.port_node.PortOutputNode

----

.. hint::

    To access a port node a :class:`NodeGraphQt.GroupNode` need to be expanded
    which can be done with one of the follow functions:

    :meth:`NodeGraphQt.NodeGraph.GroupNode.expand`,
    :meth:`NodeGraphQt.NodeGraph.expand_group_node`,
    :meth:`NodeGraphQt.SubGraph.expand_group_node`


    Port nodes object can accessed with:

    :meth:`NodeGraphQt.SubGraph.get_node_by_port`,
    :meth:`NodeGraphQt.SubGraph.get_input_port_nodes`,
    :meth:`NodeGraphQt.SubGraph.get_output_port_nodes`

|

PortInputNode
=============

.. autoclass:: NodeGraphQt.nodes.port_node.PortInputNode
    :members:
    :member-order: bysource
    :exclude-members: NODE_NAME

|

PortOutputNode
==============

.. autoclass:: NodeGraphQt.nodes.port_node.PortOutputNode
    :members:
    :member-order: bysource
    :exclude-members: NODE_NAME
