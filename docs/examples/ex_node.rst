Node Examples
#############

Creating Nodes
**************

| Creating a node is done by calling the :func:`NodeGraphQt.NodeGraph.create_node` function.
| (`see example below` ``line: 22``)

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


Embedding Widgets
*****************

The :meth:`NodeGraphQt.BaseNode` class allows you to embed widgets inside a node here's a
example to simply embed a ``QComboBox`` widget when reimplementing the ``BaseNode``.

.. code-block:: python
    :linenos:

    from NodeGraphQt import BaseNode

    class MyListNode(BaseNode):

        __identifier__ = 'com.chantasticvfx'
        NODE_NAME = 'node'

        def __init__(self):
            super(MyListNode, self).__init__()

            items = ['apples', 'bananas', 'pears', 'mangos', 'oranges']
            self.add_combo_menu('my_list', 'My List', items)

To you update the widget you can call the :meth:`NodeGraphQt.NodeObject.set_property` function.

.. code-block:: python
    :linenos:

    node = MyListNode()
    node.set_property('my_list', 'mangos')


`functions for embedding widgets into a base node:`

 - ``QComboBox``: :meth:`NodeGraphQt.BaseNode.add_combo_menu`
 - ``QCheckBox``: :meth:`NodeGraphQt.BaseNode.add_checkbox`
 - ``QLineEdit``: :meth:`NodeGraphQt.BaseNode.add_text_input`


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

`more on ports and connections.`

        - :func:`NodeGraphQt.BaseNode.input`
        - :func:`NodeGraphQt.BaseNode.output`
        - :func:`NodeGraphQt.BaseNode.set_input`
        - :func:`NodeGraphQt.BaseNode.set_output`
        - :func:`NodeGraphQt.BaseNode.inputs`
        - :func:`NodeGraphQt.BaseNode.outputs`
        - :func:`NodeGraphQt.Port.connect_to`
        - :func:`NodeGraphQt.Port.disconnect_from`


Connecting a PropertiesBin
**************************

Here's an example where we subclass the ``NodeGraph`` and connect it up to a
``PropertiesBinWidget`` and have it show when a node is double clicked.

.. code-block:: python
    :linenos:

    from NodeGraphQt import BaseNode, NodeGraph, PropertiesBinWidget, QtCore, QtWidgets


    class MyNode(BaseNode):

        __identifier__ = 'com.chantasticvfx'
        NODE_NAME = 'my node'

        def __init__(self):
            super(MyNode, self).__init__()
            self.add_input('in')
            self.add_output('out')


    class MyNodeGraph(NodeGraph):

        def __init__(self, parent=None):
            super(MyNodeGraph, self).__init__(parent)

            # properties bin widget.
            self._prop_bin = PropertiesBinWidget(node_graph=self)
            self._prop_bin.setWindowFlags(QtCore.Qt.Tool)

            # wire signal.
            self.node_double_clicked.connect(self.display_prop_bin)

        def display_prop_bin(self, node):
            """
            function for displaying the properties bin when a node
            is double clicked
            """
            if not self._prop_bin.isVisible():
                self._prop_bin.show()


    if __name__ == '__main__':
        app = QtWidgets.QApplication([])

        node_graph = MyNodeGraph()
        node_graph.register_node(MyNode)
        node_graph.widget.show()

        node_a = node_graph.create_node('com.chantasticvfx.MyNode')

        app.exec_()

`more on the properties bin and node_double_clicked signal`

    - :class:`NodeGraphQt.PropertiesBinWidget`
    - :attr:`NodeGraphQt.NodeGraph.node_double_clicked`