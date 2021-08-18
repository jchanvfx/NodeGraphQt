#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2017, Johnny Chan and some awesome contributors (^_^)
# https://github.com/jchanvfx/NodeGraphQt/graphs/contributors

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# * Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.

# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.

# * Neither the name Johnny Chan nor the names of its contributors
#   may be used to endorse or promote products derived from this software
#   without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
# OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT
# OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
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

        __identifier__ = 'com.chantasticvfx'
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
        node_a = graph.create_node('com.chantasticvfx.MyNode', name='Node A')
        node_b = graph.create_node('com.chantasticvfx.MyNode', name='Node B', color='#5b162f')

        node_a.set_input(0, node_b.output(0))

        viewer = graph.viewer()
        viewer.show()

        app.exec_()
"""

from .base.graph import NodeGraph, SubGraph
from .base.menu import NodesMenu, NodeGraphMenu, NodeGraphCommand
from .base.node import NodeObject, BaseNode, BackdropNode
from .base.port import Port
from .pkg_info import __version__ as VERSION
from .pkg_info import __license__ as LICENSE

# functions
from .base.utils import setup_context_menu, \
    topological_sort_by_up, topological_sort_by_down, \
    update_node_down_stream, update_node_up_stream,\
    update_nodes_by_up, update_nodes_by_down

# widgets
from .widgets.nodes_tree import NodeTreeWidget
from .widgets.nodes_palette import NodesPaletteWidget
from .widgets.properties_bin import PropertiesBinWidget
from .widgets.node_publish_widget import NodePublishWidget
from .widgets.node_widgets import NodeBaseWidget


__version__ = VERSION
__all__ = [
    'BackdropNode',
    'BaseNode',
    'LICENSE',
    'NodeBaseWidget',
    'NodeGraph',
    'NodeGraphCommand',
    'NodeGraphMenu',
    'NodeObject',
    'NodesPaletteWidget',
    'NodeTreeWidget',
    'NodesMenu',
    'Port',
    'PropertiesBinWidget',
    'VERSION',
    'constants',
    'setup_context_menu',
    'NodePublishWidget',
    'SubGraph',
    'topological_sort_by_up',
    'topological_sort_by_down',
    'update_node_up_stream',
    'update_node_down_stream',
    'update_nodes_by_up',
    'update_nodes_by_down',
]
