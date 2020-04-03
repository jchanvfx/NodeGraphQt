#!/usr/bin/python
# -*- coding: utf-8 -*-
import example_auto_nodes
from NodeGraphQt import NodeGraph, setup_context_menu
from NodeGraphQt import QtWidgets, QtCore, PropertiesBinWidget, \
    NodeTreeWidget, BackdropNode, NodePublishWidget
import os
import sys
import inspect
import importlib
from example_auto_nodes import AutoNode, ModuleNode, \
    SubGraphNode, Publish, RootNode, update_nodes


def get_nodes_from_folder(folder_path):
    path, folder_name = os.path.split(folder_path)
    if path not in sys.path:
        sys.path.append(path)

    nodes = []
    for i in os.listdir(folder_path):
        if not i.endswith(".py") or i.startswith("_"):
            continue

        filename = i[:-3]
        module_name = folder_name + "." + filename

        for name, obj in inspect.getmembers(importlib.import_module(module_name)):
            if inspect.isclass(obj) and filename in str(obj):
                if len(inspect.getmembers(obj)) > 0 and obj.__identifier__ != '__None':
                    nodes.append(obj)
    return nodes


def get_published_nodes_from_folder(folder_path):
    path, folder_name = os.path.split(folder_path)
    if path not in sys.path:
        sys.path.append(path)

    nodes = []
    for i in os.listdir(folder_path):
        if not i.endswith(".node") and not i.endswith(".json"):
            continue
        file_name = os.path.join(folder_path, i)
        node = Publish.create_node_class(file_name)
        if node is not None:
            nodes.append(node)

    return nodes


def cook_node(graph, node):
    node.update_stream(forceCook=True)


def print_functions(graph, node):
    for func in node.module_functions:
        print(func)


def toggle_auto_cook(graph, node):
    node.autoCook = not node.autoCook


def enter_node(graph, node):
    graph.set_node_space(node)


def print_path(graph, node):
    print(node.path())


def find_node_by_path(graph, node):
    print(graph.get_node_by_path(node.path()))


def print_children(graph, node):
    children = node.children()
    print(len(children), children)


def publish_node(graph, node):
    wid = NodePublishWidget(node=node)
    wid.show()


def cook_nodes(nodes):
    update_nodes(nodes)


if __name__ == '__main__':
    app = QtWidgets.QApplication([])

    # create node graph.
    graph = NodeGraph()
    graph.use_opengl()

    # set up default menu and commands.
    setup_context_menu(graph)

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

    # register nodes
    reg_nodes = get_nodes_from_folder(os.getcwd() + "/example_auto_nodes")
    BackdropNode.__identifier__ = 'Utility'
    reg_nodes.append(BackdropNode)
    reg_nodes.extend(get_published_nodes_from_folder(os.getcwd() + "/example_auto_nodes/published_nodes"))
    [graph.register_node(n) for n in reg_nodes]

    # setup node menu
    node_menu = graph.context_nodes_menu()
    node_menu.add_command('Enter Node', enter_node, node_class=SubGraphNode)
    node_menu.add_command('Publish Node', publish_node, node_class=SubGraphNode)
    node_menu.add_command('Print Children', print_children, node_class=SubGraphNode)
    node_menu.add_command('Print Functions', print_functions, node_class=ModuleNode)
    node_menu.add_command('Cook Node', cook_node, node_class=AutoNode)
    node_menu.add_command('Toggle Auto Cook', toggle_auto_cook, node_class=AutoNode)
    node_menu.add_command('Print Path', print_path, node_class=AutoNode)
    node_menu.add_command('Find Node By Path', find_node_by_path, node_class=AutoNode)

    # create root node
    graph.add_node(RootNode())

    # create test nodes
    graph.load_session(r'example_auto_nodes/networks/example_SubGraph.json')
    cook_nodes(graph.root_node().children())

    # widget used for the node graph.
    graph_widget = graph.widget
    graph_widget.resize(1100, 800)
    graph_widget.show()

    sys.exit(app.exec_())
