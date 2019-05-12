Widgets
*******


PropertiesBinWidget
===================

.. image:: _images/prop_bin.png
    :width: 950px

.. code-block:: python
    :linenos:

    from NodeGraphQt import NodeGraph

    graph = NodeGraph()

    # create properties bin widget.
    properties_bin = graph.properties_bin()
    properties_bin.show()

----

.. autoclass:: NodeGraphQt.widgets.properties_bin.PropertiesBinWidget
    :members:

NodeTreeWidget
==============

.. image:: _images/nodes_tree.png
    :width: 300px

.. code-block:: python
    :linenos:

    from NodeGraphQt import NodeGraph

    graph = NodeGraph()

    # create node tree widget.
    nodes_tree = graph.nodes_tree()
    nodes_tree.show()

----

.. autoclass:: NodeGraphQt.widgets.node_tree.NodeTreeWidget
    :members: