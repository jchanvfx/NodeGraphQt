#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys

from NodeGraphQt import (NodeGraph,
                         BaseNode,
                         BackdropNode,
                         setup_context_menu)
from NodeGraphQt import QtWidgets, QtCore

# import example nodes from the "example_nodes" package
from example_nodes import basic_nodes, widget_nodes


class MyNode(BaseNode):
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
        self.add_input('in port', color=(200, 10, 0), display_name=False)
        self.add_output('out port', display_name=False)

        self.add_combo_menu('knobs', 'knobs', ['asdasd', '123'])

        self.add_button('refresh', '', 'refresh')
        self.add_button('refresh2', '', 'refresh')

        self.get_widget('knobs').clear()
        self.get_widget('knobs').add_items(["cycki", 'dupa'])
        # self.get_widget('knobs').addItem('dupa')

def test(a, b, c):
    print(a.name())
    print(b)
    print(c)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    # create node graph.
    graph = NodeGraph()

    # set up default menu and commands.
    setup_context_menu(graph)

    # viewer widget used for the node graph.
    viewer = graph.viewer()
    viewer.resize(1100, 800)
    viewer.show()


    # registered nodes.
    reg_nodes = [
        BackdropNode, MyNode,
        basic_nodes.FooNode,
        basic_nodes.BarNode,
        widget_nodes.DropdownMenuNode,
        widget_nodes.TextInputNode,
        widget_nodes.CheckboxNode
    ]
    for n in reg_nodes:
        graph.register_node(n)

    my_node = graph.create_node('com.chantasticvfx.MyNode',
                                name='chantastic!',
                                color='#0a1e20',
                                text_color='#feab20',
                                pos=[310, 10])

    foo_node = graph.create_node('com.chantasticvfx.FooNode',
                                 name='node',
                                 pos=[-480, 140])
    foo_node.set_disabled(True)

    # create example "TextInputNode".
    text_node = graph.create_node('com.chantasticvfx.TextInputNode',
                                  name='text node',
                                  pos=[-480, -160])

    # create example "TextInputNode".
    checkbox_node = graph.create_node('com.chantasticvfx.CheckboxNode',
                                  name='checkbox node',
                                  pos=[-480, -20])

    # create node with a combo box menu.
    menu_node = graph.create_node('com.chantasticvfx.DropdownMenuNode',
                                  name='menu node',
                                  pos=[280, -200])


    # change node icon.
    this_path = os.path.dirname(os.path.abspath(__file__))
    icon = os.path.join(this_path, 'example_nodes', 'pear.png')
    bar_node = graph.create_node('com.chantasticvfx.BarNode')
    bar_node.set_icon(icon)
    bar_node.set_name('icon node')
    bar_node.set_pos(-70, 10)

    # connect the nodes
    foo_node.set_output(0, bar_node.input(2))
    menu_node.set_input(0, bar_node.output(1))
    bar_node.set_input(0, text_node.output(0))

    graph.property_changed.connect(test)

    app.exec_()
