import os
import sys
from PySide import QtGui, QtCore
from NodeGraphQt import NodeGraphWidget, Node
from NodeGraphQt.nodes import simple_nodes
from NodeGraphQt.nodes import text_input_node
from NodeGraphQt.nodes import menu_node


class NodeGraph(NodeGraphWidget):
    """
    Example node graph widget.
    """

    def __init__(self, parent=None):
        super(NodeGraph, self).__init__(parent)
        self.setWindowTitle('My Node Graph')
        self.resize(1100, 800)

    def keyPressEvent(self, event):
        key = event.key()
        if key == QtCore.Qt.Key_Escape:
            self.close()


class MyNode(Node):
    """
    This is a example test node.
    """
    NODE_NAME = 'my test node'

    def __init__(self):
        super(MyNode, self).__init__()
        self.set_name('my test node')
        self.set_color(81, 54, 88)
        self.add_input('in')
        self.add_output('out')


# gather nodes to be registered
NODES_TO_REGISTER = [MyNode,
                     menu_node.DropdownMenuNode,
                     simple_nodes.FooNode,
                     simple_nodes.BarNode,
                     text_input_node.TextInputNode]


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)

    # create node graph.
    graph = NodeGraph()

    # register the nodes.
    for node in NODES_TO_REGISTER:
        graph.register_node(node)

    # show the node graph.
    graph.show()

    # create the nodes from the "nodes" package dir.

    # create FooNode and change the color.
    foo_node = graph.create_node(
        'NodeGraphQt.nodes.simple_nodes.FooNode', name='Foo Node')
    foo_node.set_color(2, 67, 81)
    foo_node.set_pos(-487.0, 141.0)

    # create BarNode and change the node icon.
    bar_node = graph.create_node(
        'NodeGraphQt.nodes.simple_nodes.BarNode', name='Bar Node')
    this_path = os.path.dirname(os.path.abspath(__file__))
    icon = os.path.join(this_path, 'example', 'example_icon.png')
    bar_node.set_icon(icon)
    bar_node.set_pos(-77.0, 17.0)

    # create a nodes and disable it.
    text_node = graph.create_node(
        'NodeGraphQt.nodes.text_input_node.TextInputNode', name='Text Node')
    text_node.disable()
    text_node.set_pos(-488.0, -158.0)

    # create a node with a combobox menu.
    menu_node = graph.create_node(
        'NodeGraphQt.nodes.menu_node.DropdownMenuNode', name='Menu Node')

    # add a node manually.
    my_node = MyNode()
    graph.add_node(my_node)
    my_node.set_pos(310.0, 10.0)

    # connect the nodes
    foo_node.set_output(0, bar_node.input(2))
    menu_node.set_input(0, bar_node.output(1))
    bar_node.set_input(0, text_node.output(0))

    app.exec_()
