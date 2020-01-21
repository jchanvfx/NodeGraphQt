#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import inspect
from functools import partial

from NodeGraphQt import (NodeGraph,
                         BaseNode,
                         setup_context_menu)
from NodeGraphQt import QtWidgets, QtCore, PropertiesBinWidget, NodeTreeWidget

def updateNextNode(node):
    for nodeList in node.connected_output_nodes().values():
        for n in nodeList:
            n.run()

def getData(node,port):
    try:
        if type(port) is int:
            to_port = node.input(port)
        else:
            to_port = node.inputs()[port]
    except:
        print(node.inputs().keys())
        return 0.0

    from_ports = to_port.connected_ports()
    if not from_ports:
        return 0.0
    
    for from_port in from_ports:
        data = from_port.node().get_property(from_port.name())
        return float(data)

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
        #self.view.widgets['out'].value_changed.connect(partial(update_streams, self))
        self.view.widgets['out'].value_changed.connect(lambda: self.run())

    def result(self):
        return self.get_property("out")

    def run(self):
        updateNextNode(self)

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
        # self.view.widgets['functions'].value_changed.connect(
        #     partial(update_streams, self))
        self.view.widgets['functions'].value_changed.connect(lambda: self.run())
        self.output = self.add_output('output')
        self.create_property(self.output.name(), None)

        self.add_input("a")
        self.create_property("a", 0)
        self.add_input("b")
        self.create_property("b", 0)

    def addFunction(self, prop, func):
        """
        Create inputs based on math functions arguments.
        """
        self.func = funcs[func]   # add, sub, mul, div

    def run(self):
        """
        Evaluate all entries, pass them as arguments of the
        chosen mathematical function.
        """

        try:
            a = getData(self,0)
            b = getData(self,1)
            #print(a,b)
            # Execute math function with arguments.
            output = self.func(a,b)
            self.set_property('output', output)
        except Exception as e:
            self.set_property('output', 0)

        updateNextNode(self)

    def result(self):
        return self.get_property('output')

    def on_input_connected(self, to_port, from_port):
        """Override node callback method."""
        #self.set_property(to_port.name(), None)
        self.run()

    def on_input_disconnected(self, to_port, from_port):
        """Override node callback method."""
        self.run()

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
            value = from_node.get_property(source.name())
            self.set_property('data', str(value))

    def result(self):
        return self.get_property('data')

    def on_input_connected(self, to_port, from_port):
        """Override node callback method"""
        self.run()

    def on_input_disconnected(self, to_port, from_port):
        """Override node callback method"""
        self.set_property('data', "0")


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
    properties_bin.setStyleSheet("background-color: rgb(50,50,50);color:rgb(200,200,200)")

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
