:hide-rtoc:

Port Nodes
##########

| Port nodes are the nodes in a expanded :class:`NodeGraphQt.SubGraph` that
  represent the ports from the parent :class:`NodeGraphQt.GroupNode` object.

**Classes:**

.. autosummary::
    NodeGraphQt.nodes.port_node.PortInputNode
    NodeGraphQt.nodes.port_node.PortOutputNode

----

.. hint::

    Port node objects can be accessed in a expanded
    :class:`NodeGraphQt.GroupNode` with:

    - :meth:`NodeGraphQt.SubGraph.get_node_by_port`,
    - :meth:`NodeGraphQt.SubGraph.get_input_port_nodes`,
    - :meth:`NodeGraphQt.SubGraph.get_output_port_nodes`

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
