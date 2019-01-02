Overview
********

NodeGraphQt is a node graph framework that can be implemented and repurposed into applications that supports ``PySide2``.

.. image:: _images/overview.png
    :width: 60%

Navigation
==========

+---------------+----------------------------------------------+
| action        | controls                                     |
+===============+==============================================+
| Zoom in/out   | *Alt + MMB + Drag* or *Mouse Scroll Up/Down* |
+---------------+----------------------------------------------+
| Pan           | *Alt + LMB + Drag* or *MMB + Drag*           |
+---------------+----------------------------------------------+

Tab Search
==========

.. image:: _images/node_search.png
    :width: 269px

Node can be created with the tab node search widget.

+-------------+--------+
| action      | hotkey |
+=============+========+
| Show Search | *Tab*  |
+-------------+--------+

.. note::
    To override the tab search widget hotkey see :class:`NodeGraphQt.NodeGraph` class for the tab_search_key argument.

Menu Setup
==========

The NodeGraphQt module has a built in :meth:`NodeGraphQt.setup_context_menu` method that'll help setup the node graphs
context menu some default menus and commands.


see also: :ref:`Menu & Commands`

.. image:: _images/menu_hotkeys.png
    :width: 50%

----

.. autofunction:: NodeGraphQt.setup_context_menu


Example
=======

A basic example snippet.

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
        node_b = graph.create_node('com.chantasticvfx.FooNode', name='node B')

        # connect node_a to node_b
        node_a.set_output(0, node_b.input(2))

        app.exec_()
