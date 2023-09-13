Node Overview
#############

Creating Nodes
**************

| Creating a node is done by calling the :func:`NodeGraphQt.NodeGraph.create_node` function.
| (`see example below` ``line: 23``)

.. code-block:: python
    :linenos:
    :emphasize-lines: 23

    from Qt import QtWidgets
    from NodeGraphQt import BaseNode, NodeGraph

    class MyNode(BaseNode):

        __identifier__ = 'io.github.jchanvfx'
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
        node_a = node_graph.create_node('io.github.jchanvfx.MyNode', name='node a')
        node_b = node_graph.create_node('io.github.jchanvfx.MyNode', name='node b', pos=[300, 100])

        app.exec_()

|

Creating Node Widgets
*********************

The :class:`NodeGraphQt.BaseNode` class allows you to embed some basic widgets inside a node here's a
example to simply embed a ``QComboBox`` widget when reimplementing the ``BaseNode``.

.. code-block:: python
    :linenos:

    from NodeGraphQt import BaseNode

    class MyListNode(BaseNode):

        __identifier__ = 'io.github.jchanvfx'
        NODE_NAME = 'node'

        def __init__(self):
            super(MyListNode, self).__init__()

            items = ['apples', 'bananas', 'pears', 'mangos', 'oranges']
            self.add_combo_menu('my_list', 'My List', items)

To you update the widget you can call the
:meth:`NodeGraphQt.NodeObject.set_property` function.

.. code-block:: python
    :linenos:

    node = MyListNode()
    node.set_property('my_list', 'mangos')


`functions for embedding widgets into a base node:`

 - ``QComboBox``: :meth:`NodeGraphQt.BaseNode.add_combo_menu`
 - ``QCheckBox``: :meth:`NodeGraphQt.BaseNode.add_checkbox`
 - ``QLineEdit``: :meth:`NodeGraphQt.BaseNode.add_text_input`

See: :ref:`Embedded Node Widgets` for more node widget types.

|

Embedding Custom Widgets
************************

Here's an example to embed a custom widget where we subclass the
:class:`NodeGraphQt.NodeBaseWidget` and then add to the node with the
:meth:`NodeGraphQt.BaseNode.add_custom_widget` function.

.. code-block:: python
    :linenos:
    :emphasize-lines: 38, 96, 97

    from Qt import QtCore, QtWidgets
    from NodeGraphQt import BaseNode, NodeBaseWidget

    class MyCustomWidget(QtWidgets.QWidget):
        """
        Custom widget to be embedded inside a node.
        """

        def __init__(self, parent=None):
            super(MyCustomWidget, self).__init__(parent)
            self.combo_1 = QtWidgets.QComboBox()
            self.combo_1.addItems(['a', 'b', 'c'])
            self.combo_2 = QtWidgets.QComboBox()
            self.combo_2.addItems(['a', 'b', 'c'])
            self.btn_go = QtWidgets.QPushButton('Go')

            layout = QtWidgets.QHBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(self.combo_1)
            layout.addWidget(self.combo_2)
            layout.addWidget(self.btn_go)


    class NodeWidgetWrapper(NodeBaseWidget):
        """
        Wrapper that allows the widget to be added in a node object.
        """

        def __init__(self, parent=None):
            super(NodeWidgetWrapper, self).__init__(parent)

            # set the name for node property.
            self.set_name('my_widget')

            # set the label above the widget.
            self.set_label('Custom Widget')

            # set the custom widget.
            self.set_custom_widget(MyCustomWidget())

            # connect up the signals & slots.
            self.wire_signals()

        def wire_signals(self):
            widget = self.get_custom_widget()

            # wire up the combo boxes.
            widget.combo_1.currentIndexChanged.connect(self.on_value_changed)
            widget.combo_2.currentIndexChanged.connect(self.on_value_changed)

            # wire up the button.
            widget.btn_go.clicked.connect(self.on_btn_go_clicked)

        def on_btn_go_clicked(self):
            print('Clicked on node: "{}"'.format(self.node.name()))

        def get_value(self):
            widget = self.get_custom_widget()
            return '{}/{}'.format(widget.combo_1.currentText(),
                                  widget.combo_2.currentText())

        def set_value(self, value):
            value = value.split('/')
            if len(value) < 2:
                combo1_val = value[0]
                combo2_val = ''
            else:
                combo1_val, combo2_val = value
            widget = self.get_custom_widget()

            cb1_index = widget.combo_1.findText(combo1_val, QtCore.Qt.MatchExactly)
            cb2_index = widget.combo_1.findText(combo2_val, QtCore.Qt.MatchExactly)

            widget.combo_1.setCurrentIndex(cb1_index)
            widget.combo_2.setCurrentIndex(cb2_index)


    class MyNode(BaseNode):
        """
        Example node.
        """

        # set a unique node identifier.
        __identifier__ = 'io.github.jchanvfx'

        # set the initial default node name.
        NODE_NAME = 'my node'

        def __init__(self):
            super(MyNode, self).__init__()

            # create input and output port.
            self.add_input('in')
            self.add_output('out')

            # add custom widget to node with "node.view" as the parent.
            node_widget = NodeWidgetWrapper(self.view)
            self.add_custom_widget(node_widget, tab='Custom')

To hide/show the embedded widget on a :class:`NodeGraphQt.BaseNode` checkout the
:meth:`NodeGraphQt.BaseNode.hide_widget` and :meth:`NodeGraphQt.BaseNode.show_widget`
functions.


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

|

Connecting a PropertiesBin
**************************

Here's an example where we subclass the ``NodeGraph`` and connect it up to a
``PropertiesBinWidget`` and have it show when a node is double clicked.

.. code-block:: python
    :linenos:

    from Qt import QtCore, QtWidgets
    from NodeGraphQt import BaseNode, NodeGraph, PropertiesBinWidget


    class MyNode(BaseNode):

        __identifier__ = 'io.github.jchanvfx'
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

        node_a = node_graph.create_node('io.github.jchanvfx.MyNode')

        app.exec_()

`more on the properties bin and node_double_clicked signal`

    - :class:`NodeGraphQt.PropertiesBinWidget`
    - :attr:`NodeGraphQt.NodeGraph.node_double_clicked`
