Node Graph Qt
*************

Welcome to the NodeGraphQt api documentation this project is still in a work in progress stage,
so you might find not everything is fully documented.

.. image:: _images/screenshot.png
    :width: 95%

Project: https://github.com/jchanvfx/NodeGraphQt


Contents
========

.. toctree::
   :maxdepth: 3

   overview
   constants
   graph
   nodes
   port


Example
=======

A basic example snippet.

.. code-block:: python
    :linenos:

    import sys
    from PySide2 import QtWidgets

    from NodeGraphQt import NodeGraph, Node


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


