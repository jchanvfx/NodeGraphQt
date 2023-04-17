Silhouette
##########

Creating a node graph widget in Silhouette FX.

.. note::
    Requires Silhouette ``7.x`` or above as previous versions don't
    come built-in with its own PySide2 build or provide access to the
    ``QMainWindow`` object.

.. image:: ../_images/app_silhouette_example.png
        :width: 800px

| Here is an example where the :attr:`NodeGraphQt.NodeGraph.widget` can be
 registered as a dockable panel in the application .

.. code-block:: python
    :linenos:

    import fx

    from Qt import QtWidgets, QtCore
    from NodeGraphQt import NodeGraph, BaseNode


    # create the widget wrapper that can be docked to the main window.
    class NodeGraphPanel(QtWidgets.QDockWidget):
        """
        Widget wrapper for the node graph that can be docked to
        the main window.
        """

        def __init__(self, graph, parent=None):
            super(NodeGraphPanel, self).__init__(parent)
            self.setObjectName('nodeGraphQt.NodeGraphPanel')
            self.setWindowTitle('Custom Node Graph')
            self.setWidget(graph.widget)


    # create a simple test node class.
    class TestNode(BaseNode):

        __identifier__ = 'nodes.silhouettefx'
        NODE_NAME = 'test node'

        def __init__(self):
            super(TestNode, self).__init__()
            self.add_input('in')
            self.add_output('out')


    # create the node graph controller and register our "TestNode"
    graph = NodeGraph()
    graph.register_node(TestNode)

    # create nodes.
    node_1 = graph.create_node('nodes.silhouette.TestNode')
    node_2 = graph.create_node('nodes.silhouette.TestNode')
    node_3 = graph.create_node('nodes.silhouette.TestNode')

    # create the node graph panel that can be docked.
    sfx_graph_panel = NodeGraphPanel(graph)

    # add the doc widget into the main silhouette window.
    sfx_window = fx.ui.mainWindow()
    sfx_window.addDockWidget(QtCore.Qt.RightDockWidgetArea, sfx_graph_panel)
