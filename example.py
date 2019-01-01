#!/usr/bin/python
import os
import sys

from PySide2 import QtWidgets

from NodeGraphQt import NodeGraph, Node, Backdrop, setup_context_menu

# import example nodes from the "example_nodes" package
from example_nodes import basic_nodes, widget_nodes


class MyNode(Node):
    """
    example test node.
    """

    # set a unique node identifier.
    __identifier__ = 'com.chantasticvfx'

    # set the initial default node name.
    NODE_NAME = 'my node'

    def __init__(self):
        super(MyNode, self).__init__()
        self.set_color(25, 58, 51)

        # create input and output port.
        self.add_input('in port')
        self.add_output('out port')


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    # create node graph.
    graph = NodeGraph()

    # set up default menu and commands.
    setup_context_menu(graph)

    viewer = graph.viewer()
    viewer.setWindowTitle('My Node Graph')
    viewer.resize(1100, 800)
    viewer.show()

    # registered nodes.
    reg_nodes = [
        Backdrop, MyNode,
        basic_nodes.FooNode,
        basic_nodes.BarNode,
        widget_nodes.DropdownMenuNode,
        widget_nodes.TextInputNode
    ]
    for n in reg_nodes:
        graph.register_node(n)

    my_node = graph.create_node('com.chantasticvfx.MyNode',
                                name='portal',
                                color='#193a33',
                                pos=(310.0, 10.0))

    foo_node = graph.create_node('com.chantasticvfx.FooNode',
                                 name='chantastic!',
                                 pos=(-487.0, 141.0))
    foo_node.set_disabled(True)

    # create example "TextInputNode".
    text_node = graph.create_node('com.chantasticvfx.TextInputNode',
                                  name='rick',
                                  pos=(-488.0, -158.0))

    # create node with a combo box menu.
    menu_node = graph.create_node('com.chantasticvfx.DropdownMenuNode',
                                  name='morty',
                                  pos=(279.0, -209.0))

    # change node icon.
    this_path = os.path.dirname(os.path.abspath(__file__))
    icon = os.path.join(this_path, 'example_nodes', 'pear.png')
    bar_node = graph.create_node('com.chantasticvfx.BarNode')
    bar_node.set_icon(icon)
    bar_node.set_name('schwifty')
    bar_node.set_pos(-77.0, 17.0)

    # connect the nodes
    foo_node.set_output(0, bar_node.input(2))
    menu_node.set_input(0, bar_node.output(1))
    bar_node.set_input(0, text_node.output(0))

    app.exec_()
