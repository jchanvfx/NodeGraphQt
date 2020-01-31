#!/usr/bin/python
# -*- coding: utf-8 -*-
import example_auto_nodes

from NodeGraphQt import (NodeGraph,
                         BaseNode,
                         setup_context_menu)
from NodeGraphQt import QtWidgets, QtCore, PropertiesBinWidget, NodeTreeWidget
import os
import sys
import inspect
import importlib
from example_auto_nodes.node_base.auto_node import AutoNode
from example_auto_nodes.node_base.module_node import ModuleNode


def GetNodesFromFolder(FolderPath):
    path, FolderName = os.path.split(FolderPath)
    if path not in sys.path:
        sys.path.append(path)

    nodes = []
    for i in os.listdir(FolderPath):
        if not i.endswith(".py") or i.startswith("_"):
            continue

        filename = i[:-3]
        module_name = FolderName + "." + filename

        for name, obj in inspect.getmembers(importlib.import_module(module_name)):
            if inspect.isclass(obj) and filename in str(obj):
                if len(inspect.getmembers(obj)) > 0:
                    nodes.append(obj)
    return nodes


def cook_node(graph, node):
    node.cook()


def print_functions(graph, node):
    for func in node.module_functions:
        print(func)


def toggle_auto_cook(graph, node):
    node.autoCook = not node.autoCook


if __name__ == '__main__':
    app = QtWidgets.QApplication([])

    # create node graph.
    graph = NodeGraph()
    graph.use_opengl()

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

    reg_nodes = GetNodesFromFolder(os.getcwd() + "/example_auto_nodes")

    for n in reg_nodes:
        graph.register_node(n)

    node_menu = graph.context_nodes_menu()
    node_menu.add_command('Print Functions', print_functions, node_class=ModuleNode)
    node_menu.add_command('Cook Node', cook_node, node_class=AutoNode)
    node_menu.add_command('Toggle Auto Cook', toggle_auto_cook, node_class=AutoNode)

    mathNodeA = graph.create_node('Module.MathModuleNode',
                                name='Math Functions A',
                                color='#0a1e20',
                                text_color='#feab20',
                                pos=[-250, 70])

    mathNodeB = graph.create_node('Module.MathModuleNode',
                                name='Math Functions B',
                                color='#0a1e20',
                                text_color='#feab20',
                                pos=[-250, -70])

    mathNodeC = graph.create_node('Module.MathModuleNode',
                                  name='Math Functions C',
                                  color='#0a1e20',
                                  text_color='#feab20',
                                  pos=[0, 0])

    inputANode = graph.create_node('Inputs.FloatInputNode',
                                   name='Input A',
                                   pos=[-500, -50])

    inputBNode = graph.create_node('Inputs.FloatInputNode',
                                   name='Input B',
                                   pos=[-500, 50])

    outputNode = graph.create_node('Viewers.DataViewerNode',
                                   name='Output',
                                   pos=[250, 0])

    sys.exit(app.exec_())
