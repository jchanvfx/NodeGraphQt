Nuke
####

Creating a node graph widget in Nuke.

.. image:: ../_images/app_nuke_example.png
        :width: 800px

| Here is an example where the :attr:`NodeGraphQt.NodeGraph.widget` can be
 registered as a panel in the compositing application NUKE.

.. code-block:: python
    :linenos:

    from nukescripts import panels

    from Qt import QtWidgets, QtCore
    from NodeGraphQt import NodeGraph, BaseNode


    # create a simple test node class.
    class TestNode(BaseNode):

        __identifier__ = 'nodes.nuke'
        NODE_NAME = 'test node'

        def __init__(self):
            super(TestNode, self).__init__()
            self.add_input('in')
            self.add_output('out 1')
            self.add_output('out 2')


    # create the node graph controller and register our "TestNode".
    graph = NodeGraph()
    graph.register_node(TestNode)

    # create nodes.
    node_1 = graph.create_node('nodes.nuke.TestNode')
    node_2 = graph.create_node('nodes.nuke.TestNode')
    node_3 = graph.create_node('nodes.nuke.TestNode')

    # connect the nodes.
    node_1.set_output(0, node_2.input(0))
    node_2.set_output(1, node_3.input(0))

    # auto layout the nodes.
    graph.auto_layout_nodes()

    # create a backdrop node and wrap it to node_1 and node_2.
    backdrop = graph.create_node('Backdrop')
    backdrop.wrap_nodes([node_1, node_2])


    # create the wrapper widget.
    class CustomNodeGraph(QtWidgets.QWidget):

        def __init__(self, parent=None):
            super(CustomNodeGraph, self).__init__(parent)
            layout = QtWidgets.QVBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(graph.widget)

        @staticmethod
        def _set_nuke_zero_margin(widget_object):
            """
            Foundry Nuke hack for "nukescripts.panels.registerWidgetAsPanel" to
            remove the widget contents margin.

            sourced from: https://gist.github.com/maty974/4739917

            Args:
                widget_object (QtWidgets.QWidget): widget object.
            """
            if widget_object:
                parent_widget = widget_object.parentWidget().parentWidget()
                target_widgets = set()
                target_widgets.add(parent_widget)
                target_widgets.add(parent_widget.parentWidget().parentWidget())
                for widget_layout in target_widgets:
                    widget_layout.layout().setContentsMargins(0, 0, 0, 0)

        def event(self, event):
            if event.type() == QtCore.QEvent.Type.Show:
                try:
                    self._set_nuke_zero_margin(self)
                except Exception:
                    pass
            return super(CustomNodeGraph, self).event(event)

    # register the wrapper widget as a panel in Nuke.
    panels.registerWidgetAsPanel(
        widget='CustomNodeGraph',
        name='Custom Node Graph',
        id='nodegraphqt.graph.CustomNodeGraph'
    )
