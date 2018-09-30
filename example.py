#!/usr/bin/python
import os
import sys

from PySide2 import QtWidgets

from NodeGraphQt import NodeGraph, Node, Backdrop

# import example nodes from the "example_nodes" package
from example_nodes import simple_nodes, menu_node, text_input_node


class MyNode(Node):
    """
    This is a example test node.
    """

    # set a unique node identifier.
    __identifier__ = 'com.chantasticvfx'

    # set the initial default node name.
    NODE_NAME = 'My Node'

    def __init__(self):
        super(MyNode, self).__init__()
        self.set_color(81, 54, 88)
        self.add_checkbox('cb_hello', '', 'Hello', True)
        self.add_checkbox('cb_world', '', 'World', False)
        self.add_input('in')
        self.add_output('out')


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    # create node graph.
    graph = NodeGraph()

    viewer = graph.viewer()
    viewer.setWindowTitle('My Node Graph')
    viewer.resize(1100, 800)
    viewer.show()

    # registered nodes.
    reg_nodes = [
        Backdrop,
        MyNode,
        menu_node.DropdownMenuNode,
        simple_nodes.FooNode,
        simple_nodes.BarNode, 
        text_input_node.TextInputNode
    ]
    [graph.register_node(n) for n in reg_nodes]


    my_node = graph.create_node('com.chantasticvfx.MyNode',
                                name='test',
                                pos=(310.0, 10.0))

    foo_node = graph.create_node('com.chantasticvfx.FooNode',
                                 name='Foo Node',
                                 pos=(-487.0, 141.0))

    # create example "TextInputNode".
    text_node = graph.create_node('com.chantasticvfx.TextInputNode',
                                  name='Text Node',
                                  color='#6b273f',
                                  pos=(-488.0, -158.0))
    text_node.set_disabled(True)

    # create node with a combo box menu.
    menu_node = graph.create_node('com.chantasticvfx.DropdownMenuNode',
                                  name='Menu Node',
                                  color='#005341',
                                  pos=(279.0, -209.0))

    # change node icon.
    this_path = os.path.dirname(os.path.abspath(__file__))
    icon = os.path.join(this_path, 'example', 'example_icon.png')
    bar_node = graph.create_node('com.chantasticvfx.BarNode')
    bar_node.set_icon(icon)
    bar_node.set_name('Bar Node')
    bar_node.set_pos(-77.0, 17.0)

    # connect the nodes
    foo_node.set_output(0, bar_node.input(2))
    menu_node.set_input(0, bar_node.output(1))
    bar_node.set_input(0, text_node.output(0))

    app.exec_()
