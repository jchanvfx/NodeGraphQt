import sys

from PySide2 import QtWidgets

from NodeGraphQt import NodeGraph, Node
# import example nodes from the "example_nodes" package
from example_nodes import simple_nodes, menu_node, text_input_node


class MyNode(Node):
    """
    This is a example test node.
    """
    # set a unique node identifier.
    __identifier__ = 'com.chantasticvfx'

    # set the initial default node name.
    NODE_NAME = 'my test node'

    def __init__(self):
        super(MyNode, self).__init__()
        self.set_color(81, 54, 88)
        self.add_checkbox('cb_hello', '', 'Hello', True)
        self.add_checkbox('cb_world', '', 'World', False)
        self.add_input('in')
        self.add_output('out')


# gather nodes to be registered to the node graph.
NODES_TO_REGISTER = [MyNode,
                     menu_node.DropdownMenuNode,
                     simple_nodes.FooNode,
                     simple_nodes.BarNode,
                     text_input_node.TextInputNode
                     ]


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    # create node graph.
    graph = NodeGraph()
    viewer = graph.viewer()
    viewer.setWindowTitle('My Node Graph')
    viewer.resize(1100, 800)

    # register the nodes.
    for node in NODES_TO_REGISTER:
        graph.register_node(node)

    # show the node graph.
    graph.show()

    # create "FooNode" and change the color.
    foo_node = graph.create_node(
        'com.chantasticvfx.FooNode', name='Foo Node')
    foo_node.set_color(2, 67, 81)
    foo_node.set_pos(-487.0, 141.0)

    # create "BarNode" and change the node icon.
    bar_node = graph.create_node(
        'com.chantasticvfx.BarNode', name='Bar Node')
    import os
    this_path = os.path.dirname(os.path.abspath(__file__))
    icon = os.path.join(this_path, 'example', 'example_icon.png')
    bar_node.set_icon(icon)
    bar_node.set_pos(-77.0, 17.0)

    # create "TextInputNode" node and disable it.
    text_node = graph.create_node(
        'com.chantasticvfx.TextInputNode', name='Text Node')
    text_node.set_disabled(True)
    text_node.set_pos(-488.0, -158.0)

    # create a node with a combobox menu.
    menu_node = graph.create_node(
        'com.chantasticvfx.DropdownMenuNode', name='Menu Node')
    menu_node.set_pos(279.0, -209.0)

    # add a node manually.
    my_node = MyNode()
    graph.add_node(my_node)
    my_node.set_pos(310.0, 10.0)

    # # connect the nodes
    foo_node.set_output(0, bar_node.input(2))
    menu_node.set_input(0, bar_node.output(1))
    bar_node.set_input(0, text_node.output(0))

    app.exec_()
