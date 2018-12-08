Node Graph Qt
*************

Project: https://github.com/jchanvfx/NodeGraphQt

.. image:: _images/screenshot.png
    :width: 95%

NodeGraphQt is a node graph framework that can be implemented and repurposed into applications that supports ``PySide2``.


Module Classes
==============

.. toctree::
   :maxdepth: 3

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

        # unique node identifier.
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

        # create node graph.
        graph = NodeGraph()

        # register the FooNode node.
        graph.register_node(FooNode)

        # show the node graph widget.
        viewer = graph.viewer()
        viewer.show()

        # create a couple nodes.
        node_a = graph.create_node('com.chantasticvfx.FooNode', name='hello')
        node_b = graph.create_node('com.chantasticvfx.FooNode', name='world')

        # connect node_a to node_b
        node_a.set_output(0, node_b.input(2))

        app.exec_()


