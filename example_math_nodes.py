#!/usr/bin/python
# -*- coding: utf-8 -*-
from example_nodes import Nodes
from NodeGraphQt import (NodeGraph,
                         BaseNode,
                         setup_context_menu)
from NodeGraphQt import QtWidgets, QtCore, PropertiesBinWidget, NodeTreeWidget


if __name__ == '__main__':
    app = QtWidgets.QApplication([])

    # create node graph.
    graph = NodeGraph()

    # set up default menu and commands.
    setup_context_menu(graph)

    # widget used for the node graph.
    graph_widget = graph.widget
    graph_widget.resize(1100, 800)
    graph_widget.show()

    # show the properties bin when a node is "double clicked" in the graph.
    properties_bin = PropertiesBinWidget(node_graph=graph)
    properties_bin.setWindowFlags(QtCore.Qt.Tool)

    def show_prop_bin(node):
        if not properties_bin.isVisible():
            properties_bin.show()
    graph.node_double_clicked.connect(show_prop_bin)

    # show the nodes list when a node is "double clicked" in the graph.
    node_tree = NodeTreeWidget(node_graph=graph)

    def show_nodes_list(node):
        if not node_tree.isVisible():
            node_tree.update()
            node_tree.show()
    graph.node_double_clicked.connect(show_nodes_list)

    # registered nodes.
    for n in Nodes:
        graph.register_node(n)

    mathNodeA = graph.create_node('Math.MathFunctionsNode',
                                name='Math Functions A',
                                color='#0a1e20',
                                text_color='#feab20',
                                pos=[-250, 70])

    mathNodeB = graph.create_node('Math.MathFunctionsNode',
                                name='Math Functions B',
                                color='#0a1e20',
                                text_color='#feab20',
                                pos=[-250, -70])

    mathNodeC = graph.create_node('Math.MathFunctionsNode',
                                  name='Math Functions C',
                                  color='#0a1e20',
                                  text_color='#feab20',
                                  pos=[0, 0])

    inputANode = graph.create_node('Inputs.DataInputNode',
                                   name='Input A',
                                   pos=[-500, -50])

    inputBNode = graph.create_node('Inputs.DataInputNode',
                                   name='Input B',
                                   pos=[-500, 50])

    outputNode = graph.create_node('Viewers.DataViewerNode',
                                   name='Output',
                                   pos=[250, 0])

    app.exec_()
