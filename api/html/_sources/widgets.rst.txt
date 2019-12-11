Widgets
*******


PropertiesBinWidget
===================

The ``PropertiesBinWidget`` is a list widget for displaying and editing a
nodes properties.

.. image:: _images/prop_bin.png
    :width: 950px

example

.. code-block:: python
    :linenos:

    from NodeGraphQt import NodeGraph, PropertiesBinWidget

    # create node graph.
    graph = NodeGraph()

    # create properties bin widget.
    properties_bin = PropertiesBinWidget(parent=None, node_graph=graph)
    properties_bin.show()

----

.. autoclass:: NodeGraphQt.PropertiesBinWidget
    :members:
    :exclude-members: property_changed

NodeTreeWidget
==============

The ``NodeTreeWidget`` is a widget for displaying all registered nodes from the
node graph with this widget a user can create nodes by dragging and dropping.

.. image:: _images/nodes_tree.png
    :width: 300px

example

.. code-block:: python
    :linenos:

    from NodeGraphQt import NodeGraph, NodeTreeWidget

    # create node graph.
    graph = NodeGraph()

    # create node tree widget.
    nodes_tree = NodeTreeWidget(parent=None, node_graph=graph)
    nodes_tree.show()

----

.. autoclass:: NodeGraphQt.widgets.node_tree.NodeTreeWidget
    :members:
    :exclude-members: mimeData, set_node_factory, property_changed
