Overview
********

NodeGraphQt is a node graph framework that can be implemented and repurposed into applications that supports ``PySide2``.

.. image:: _images/overview.png
    :width: 70%

Navigation
==========

+---------------+----------------------------------------------+
| action        | controls                                     |
+===============+==============================================+
| Zoom in/out   | *Alt + MMB + Drag* or *Mouse Scroll Up/Down* |
+---------------+----------------------------------------------+
| Pan           | *Alt + LMB + Drag* or *MMB + Drag*           |
+---------------+----------------------------------------------+

Node Search
===========

.. image:: _images/node_search.png
    :width: 269px

Node can be created with the tab node search widget.

+-------------------+--------+
| action            | hotkey |
+===================+========+
| Toggle Visibility | *Tab*  |
+-------------------+--------+


Properties Bin
==============

.. image:: _images/prop_bin.png
    :width: 950px

.. code-block:: python
    :linenos:

    from NodeGraphQt import NodeGraph

    graph = NodeGraph()

    properties_bin = graph.properties_bin()
    properties_bin.show()


Menu Setup
==========

The NodeGraphQt has a ``setup_context_menu`` method that'll setup the node graphs with basic menus and commands.

`(see line:32 in the example code below)`

see also: :ref:`Menus`


Example
=======

Here's a basic example for creating two nodes and connecting them together.

.. image:: _images/example_result.png
    :width: 60%

example code:

.. code-block:: python
    :linenos:

    import sys
    from PySide2 import QtWidgets

    from NodeGraphQt import NodeGraph, Node, setup_context_menu


    class FooNode(Node):

        # unique node identifier domain.
        __identifier__ = 'com.chantasticvfx'

        # initial default node name.
        NODE_NAME = 'Foo Node'

        def __init__(self):
            super(FooNode, self).__init__()

            # create an input port.
            self.add_input('in')

            # create an output port.
            self.add_output('out')


    if __name__ == '__main__':
        app = QtWidgets.QApplication(sys.argv)

        # create node graph controller.
        graph = NodeGraph()

        # set up default menu and commands.
        setup_context_menu(graph)

        # register the FooNode node class.
        graph.register_node(FooNode)

        # show the node graph widget.
        viewer = graph.viewer()
        viewer.show()

        # create two nodes.
        node_a = graph.create_node('com.chantasticvfx.FooNode', name='node A')
        node_b = graph.create_node('com.chantasticvfx.FooNode', name='node B', pos=(300, 50))

        # connect node_a to node_b
        node_a.set_output(0, node_b.input(2))

        app.exec_()
