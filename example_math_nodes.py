#!/usr/bin/python
# -*- coding: utf-8 -*-
from Qt import QtWidgets, QtCore

from NodeGraphQt import (NodeGraph,
                         PropertiesBinWidget,
                         NodeTreeWidget,
                         update_nodes_by_down,
                         setup_context_menu)
from example_nodes import Nodes
from os.path import join

if __name__ == '__main__':
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
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
    [graph.register_node(n) for n in Nodes]

    # load preset session
    graph.load_session(join('example_nodes', 'networks', 'example.nodes'))

    # update nodes
    update_nodes_by_down(graph.all_nodes())

    app.exec_()
