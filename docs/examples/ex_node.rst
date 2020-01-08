Node Examples
#############

Creating Nodes
**************

| Creating is done simply by calling the :func:`NodeGraphQt.NodeGraph.create_node` function.
| (`see example below` ``line22``)

.. code-block:: python
    :linenos:

    from NodeGraphQt import BaseNode, NodeGraph, QtWidgets

    class MyNode(BaseNode):

        __identifier__ = 'com.chantasticvfx'
        NODE_NAME = 'my node'

        def __init__(self):
            super(MyNode, self).__init__()
            self.add_input('foo')
            self.add_input('hello')
            self.add_output('bar')
            self.add_output('world')

    if __name__ == '__main__':
        app = QtWidgets.QApplication([])

        node_graph = NodeGraph()
        node_graph.register_node(MyNode)
        node_graph.widget.show()

        # here we create a couple nodes in the node graph.
        node_a = node_graph.create_node('com.chantasticvfx.MyNode', name='node a')
        node_b = node_graph.create_node('com.chantasticvfx.MyNode', name='node b', pos=[300, 100])

        app.exec_()


Connecting Nodes
****************

There a multiple ways for connecting node ports here are a few examples below.

connecting nodes by the port index:

.. code-block:: python

    node_b.set_input(0, node_a.output(0))

connect nodes by the port name:

.. code-block:: python

    node_a.outputs()['bar'].connect_to(node_b.inputs()['foo'])

connecting nodes with the port objects:

.. code-block:: python

    # node_a "bar" output port.
    port_a = node_a.output(0)
    # node_b "foo" input port.
    port_b = node_b.inputs()['foo']
    # make the connection.
    port_a.connect_to(port_b)


See functions:
    - :func:`NodeGraphQt.BaseNode.input`,
    - :func:`NodeGraphQt.BaseNode.output`
    - :func:`NodeGraphQt.BaseNode.set_input`,
    - :func:`NodeGraphQt.BaseNode.set_output`,
    - :func:`NodeGraphQt.BaseNode.inputs`,
    - :func:`NodeGraphQt.BaseNode.outputs`
    - :func:`NodeGraphQt.Port.connect_to`,
    - :func:`NodeGraphQt.Port.disconnect_from`


Properties Bin Setup
********************

