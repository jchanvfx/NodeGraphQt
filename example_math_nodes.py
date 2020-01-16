#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import inspect
from functools import partial

from NodeGraphQt import (NodeGraph,
                         BaseNode,
                         setup_context_menu)
from NodeGraphQt import QtWidgets, QtCore, PropertiesBinWidget, NodeTreeWidget


def update_streams(node):
    """
    Update all nodes joined by pipes
    """
    nodes = []
    trash = []

    for port, nodeList in node.connected_output_nodes().items():
        nodes.extend(nodeList)

    while nodes:
        node = nodes.pop()
        if node not in trash:
            trash.append(node)

        for port, nodeList in node.connected_output_nodes().items():
            nodes.extend(nodeList)

        if not nodes:
            try:
                node.run()
            except Exception as error:
                print("Error Update Streams: %s" % str(error))


class DataInputNode(BaseNode):
    """
    Input node data.
    """

    __identifier__ = 'com.chantasticvfx'
    NODE_NAME = 'Input Numbers'

    def __init__(self):
        super(DataInputNode, self).__init__()
        self.output = self.add_output('out')
        self.add_text_input('out', 'Data Input', text='4', tab='widgets')
        self.view.widgets['out'].value_changed.connect(partial(update_streams, self))
        
    def run(self):
        return


def add(a, b):
    return a + b


def sub(a, b):
    return a - b


def mul(a, b):
    return a * b


def div(a, b):
    return a / b


# create a dict with all function
funcs = {'add': add, 'sub': sub, 'mul': mul, 'div': div}


class MathFunctionsNode(BaseNode):
    """
    Math functions node.

    """

    # set a unique node identifier.
    __identifier__ = 'com.chantasticvfx'

    # set the initial default node name.
    NODE_NAME = 'Functions node'

    def __init__(self):
        super(MathFunctionsNode, self).__init__()
        self.set_color(25, 58, 51)
        self.add_combo_menu('functions', 'Functions',
                            items=funcs.keys(), tab='widgets')
        # switch math function type
        self.view.widgets['functions'].value_changed.connect(self.addFunction)
        self.set_property('functions', 'add')
        self.view.widgets['functions'].value_changed.connect(
            partial(update_streams, self))
        self.output = self.add_output('output')
        self.create_property(self.output.name(), None)

    def addFunction(self, prop, func):
        """
        Create inputs based on math functions arguments.
        """
        self.func = funcs[func]   # add, sub, mul, div

        dataFunc = inspect.getargspec(self.func)

        for arg in dataFunc.args:
            if not self.has_property(arg):
                self.add_input(arg)
                self.create_property(arg, None)

    def run(self):
        """
        Evaluate all entries, pass them as arguments of the
        chosen mathematical function.
        """
        for to_port in self.input_ports():
            from_ports = to_port.connected_ports()
            if not from_ports:
                raise Exception('Port %s not connected!' % to_port.name())

            for from_port in from_ports:
                from_port.node().run()
                data = from_port.node().get_property(from_port.name())
                self.set_property(to_port.name(), int(data))

        try:
            # Execute math function with arguments.
            output = self.func(*[self.get_property(prop)
                                 for prop in self.properties()['inputs']])
            self.set_property('output', output)
        except KeyError as error:
            print("An input is missing! %s" % str(error))
        except TypeError as error:
            print("Error evaluating function: %s" % str(error))

    def on_input_connected(self, to_port, from_port):
        """Override node callback method."""
        self.set_property(to_port.name(), from_port.node().run())
        update_streams(self)

    def on_input_disconnected(self, to_port, from_port):
        """Override node callback method."""
        self.set_property('output', None)
        update_streams(self)


class DataViewerNode(BaseNode):
    __identifier__ = 'com.chantasticvfx'
    NODE_NAME = 'Result View'

    def __init__(self):
        super(DataViewerNode, self).__init__()
        self.input = self.add_input('in data')
        self.add_text_input('data', 'Data Viewer', tab='widgets')

    def run(self):
        """Evaluate input to show it."""
        for source in self.input.connected_ports():
            from_node = source.node()
            try:
                from_node.run()
            except Exception as error:
                print("%s no inputs connected: %s" % (from_node.name(), str(error)))
                self.set_property('data', None)
                return
            value = from_node.get_property(source.name())
            self.set_property('data', str(value))

    def on_input_connected(self, to_port, from_port):
        """Override node callback method"""
        self.run()

    def on_input_disconnected(self, to_port, from_port):
        """Override node callback method"""
        self.set_property('data', None)


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
    reg_nodes = [DataInputNode, DataViewerNode, MathFunctionsNode]

    for n in reg_nodes:
        graph.register_node(n)

    my_node = graph.create_node('com.chantasticvfx.MathFunctionsNode',
                                name='Math Functions A',
                                color='#0a1e20',
                                text_color='#feab20',
                                pos=[-250, 70])

    my_node = graph.create_node('com.chantasticvfx.MathFunctionsNode',
                                name='Math Functions B',
                                color='#0a1e20',
                                text_color='#feab20',
                                pos=[-250, -70])

    my_node = graph.create_node('com.chantasticvfx.MathFunctionsNode',
                                name='Math Functions C',
                                color='#0a1e20',
                                text_color='#feab20',
                                pos=[0, 0])

    inputANode = graph.create_node('com.chantasticvfx.DataInputNode',
                                   name='Input A',
                                   pos=[-500, -50])

    inputBNode = graph.create_node('com.chantasticvfx.DataInputNode',
                                   name='Input B',
                                   pos=[-500, 50])

    outputNode = graph.create_node('com.chantasticvfx.DataViewerNode',
                                   name='Output',
                                   pos=[250, 0])

    app.exec_()
