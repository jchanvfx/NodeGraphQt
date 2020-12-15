#!/usr/bin/python
# -*- coding: utf-8 -*-
from NodeGraphQt import NodeGraph, setup_context_menu, \
    QtWidgets, QtCore, PropertiesBinWidget, BackdropNode
from example_auto_nodes import Publish, RootNode, update_nodes, setup_node_menu
import importlib
import inspect
import sys
import os


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


if __name__ == '__main__':
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    app = QtWidgets.QApplication()

    # create node graph.
    graph = NodeGraph()
    graph.use_OpenGL()

    # set up default menu and commands.
    setup_context_menu(graph)
    setup_node_menu(graph, Publish)

    # show the properties bin when a node is "double clicked" in the graph.
    properties_bin = PropertiesBinWidget(node_graph=graph)
    properties_bin.setWindowFlags(QtCore.Qt.Tool)

    def show_prop_bin(node):
        if not properties_bin.isVisible():
            properties_bin.show()
    graph.node_double_clicked.connect(show_prop_bin)

    # register nodes
    reg_nodes = get_nodes_from_folder(os.getcwd() + "/example_auto_nodes")
    BackdropNode.__identifier__ = 'Utility::Backdrop'
    reg_nodes.append(BackdropNode)
    reg_nodes.extend(get_published_nodes_from_folder(os.getcwd() + "/example_auto_nodes/published_nodes"))
    [graph.register_node(n) for n in reg_nodes]

    # create root node
    # if we want to use sub graph system, root node is must.
    graph.add_node(RootNode())

    # create test nodes
    graph.load_session(r'example_auto_nodes/networks/example_SubGraph.json')
    update_nodes(graph.root_node().children())

    # widget used for the node graph.
    graph_widget = graph.widget
    graph_widget.resize(1100, 800)
    graph_widget.show()

    sys.exit(app.exec_())
