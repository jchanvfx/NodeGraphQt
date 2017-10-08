import sys
import os
from PySide import QtGui, QtCore

import BlueprintNodeGraph as BpGraph


class TestNodeFoo(BpGraph.Node):
    """
    A node class with 2 inputs and 2 outputs.
    """

    def __init__(self, name=None):
        super(TestNodeFoo, self).__init__(name)
        # create node inputs
        self.add_input('foo')
        self.add_input('bar')
        # create node outputs
        self.add_output('apples')
        self.add_output('bananas')

BpGraph.register_node(TestNodeFoo)


class TestNodeBar(BpGraph.Node):
    """
    A node class with 3 inputs and 3 outputs.
    """

    def __init__(self, name=None):
        super(TestNodeBar, self).__init__(name)
        # create node inputs
        self.add_input('hello')
        self.add_input('world')
        self.add_input('foo bar')
        # create node outputs
        self.add_output('apples')
        self.add_output('bananas')
        self.add_output('orange')

BpGraph.register_node(TestNodeBar)


class TextInputNode(BpGraph.Node):
    """
    A example of a node with a added text input.
    """

    def __init__(self, name=None):
        super(TextInputNode, self).__init__(name)
        # create node inputs
        self.add_input('hello')
        # create node outputs
        self.add_output('world')
        # add text input field to node.
        self.add_text_input('my_input', 'Text Input')

BpGraph.register_node(TextInputNode)


class DropdownMenuNode(BpGraph.Node):
    """
    A example of a node with a added menu and a few input & outputs.
    """

    def __init__(self, name=None):
        super(DropdownMenuNode, self).__init__(name)
        # create node inputs
        self.add_input('hello')
        # create node outputs
        self.add_output('world')
        self.add_output('foo')
        # add text input field to node.
        items = ['item 1', 'item2', 'item3']
        self.add_dropdown_menu('my_menu_1', 'Menu Test', items=items)

BpGraph.register_node(DropdownMenuNode)


class NodeGraph(BpGraph.NodeGraph):

    def __init__(self, parent=None):
        super(NodeGraph, self).__init__(parent)
        self.setWindowTitle('Blueprint Node Graph')
        self.resize(1100, 800)

    def keyPressEvent(self, event):
        key = event.key()
        if key == QtCore.Qt.Key_Escape:
            self.close()


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)

    # create node graph.
    graph = NodeGraph()
    graph.show()

    # create the nodes.
    foo_node = graph.create_node(class_type='TestNodeFoo', name='Foo Node')
    bar_node = graph.create_node(class_type='TestNodeBar', name='Bar Node')
    text_node = graph.create_node(class_type='TextInputNode', name='Text Node')
    menu_node = graph.create_node(class_type='DropdownMenuNode', name='Menu Node')

    graph.create_node(class_type='TestNodeFoo', name='TEST')

    # change the color on "foo_node"
    foo_node.set_color(17, 52, 88)

    # chage icon on "bar_node"
    this_path = os.path.dirname(os.path.abspath(__file__))
    icon = os.path.join(this_path, 'example_icon.png')
    bar_node.set_icon(icon)

    # position nodes.
    foo_node.set_pos(-487.0, 141.0)
    bar_node.set_pos(-77.0, 17.0)
    text_node.set_pos(-488.0, -158.0)
    menu_node.set_pos(310.0, -97.0)

    # connect nodes
    foo_node.set_output(0, bar_node.input(2))
    menu_node.set_input(0, bar_node.output(1))
    bar_node.set_input(0, text_node.output(0))

    app.exec_()
