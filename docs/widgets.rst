Widgets
*******


PropertiesBinWidget
===================

.. image:: _images/prop_bin.png
    :width: 950px

.. code-block:: python
    :linenos:

    from NodeGraphQt import NodeGraph, PropertiesBinWidget

    # create node graph.
    graph = NodeGraph()

    # create properties bin widget.
    properties_bin = PropertiesBinWidget(node_graph=graph)
    properties_bin.show()

----

.. autoclass:: NodeGraphQt.PropertiesBinWidget
    :members:
    :exclude-members: property_changed

NodeTreeWidget
==============

.. image:: _images/nodes_tree.png
    :width: 300px

.. code-block:: python
    :linenos:

    from NodeGraphQt import NodeGraph, NodeTreeWidget

    # create node graph.
    graph = NodeGraph()

    # create node tree widget.
    nodes_tree = NodeTreeWidget(node_graph=graph)
    nodes_tree.show()

----

.. autoclass:: NodeGraphQt.widgets.node_tree.NodeTreeWidget
    :members:
    :exclude-members: mimeData, set_node_factory, property_changed
