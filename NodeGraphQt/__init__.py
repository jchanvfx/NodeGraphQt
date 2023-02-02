#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
**NodeGraphQt** is a node graph framework that can be implemented and re purposed
into applications that supports **PySide2**.

project: https://github.com/jchanvfx/NodeGraphQt
documentation: https://jchanvfx.github.io/NodeGraphQt/api/html/index.html

example code:

.. code-block:: python
    :linenos:

    from NodeGraphQt import QtWidgets, NodeGraph, BaseNode


    class MyNode(BaseNode):

        __identifier__ = 'io.github.jchanvfx'
        NODE_NAME = 'My Node'

        def __init__(self):
            super(MyNode, self).__init__()
            self.add_input('foo', color=(180, 80, 0))
            self.add_output('bar')

    if __name__ == '__main__':
        app = QtWidgets.QApplication([])
        graph = NodeGraph()

        graph.register_node(BaseNode)
        graph.register_node(BackdropNode)

        backdrop = graph.create_node('nodeGraphQt.nodes.Backdrop', name='Backdrop')
        node_a = graph.create_node('io.github.jchanvfx.MyNode', name='Node A')
        node_b = graph.create_node('io.github.jchanvfx.MyNode', name='Node B', color='#5b162f')

        node_a.set_input(0, node_b.output(0))

        viewer = graph.viewer()
        viewer.show()

        app.exec_()
"""
from .pkg_info import __version__ as VERSION
from .pkg_info import __license__ as LICENSE

# node graph
from .base.graph import NodeGraph, SubGraph
from .base.menu import NodesMenu, NodeGraphMenu, NodeGraphCommand

# nodes & ports
from .base.port import Port
from .base.node import NodeObject
from .nodes.base_node import BaseNode
from .nodes.base_node_circle import BaseNodeCircle
from .nodes.backdrop_node import BackdropNode
from .nodes.group_node import GroupNode

# widgets
from .widgets.node_widgets import NodeBaseWidget
from .custom_widgets.nodes_tree import NodesTreeWidget
from .custom_widgets.nodes_palette import NodesPaletteWidget
from .custom_widgets.properties_bin.node_property_widgets import PropertiesBinWidget


__version__ = VERSION
__all__ = [
    'BackdropNode',
    'BaseNode',
    'BaseNodeCircle',
    'GroupNode',
    'LICENSE',
    'NodeBaseWidget',
    'NodeGraph',
    'NodeGraphCommand',
    'NodeGraphMenu',
    'NodeObject',
    'NodesPaletteWidget',
    'NodesTreeWidget',
    'NodesMenu',
    'Port',
    'PropertiesBinWidget',
    'SubGraph',
    'VERSION',
    'constants',
    'custom_widgets'
]
