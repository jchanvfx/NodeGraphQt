import sys

from PySide import QtGui, QtCore

import BlueprintNodeGraph as bpng


class TestNodeFoo(bpng.Node):
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


class TestNodeBar(bpng.Node):
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


class TextInputNode(bpng.Node):
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


class DropdownMenuNode(bpng.Node):
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
        items = ['item1', 'item2', 'item3']
        self.add_dropdown_menu('my_menu_1', 'Menu Test', items=items)


# register the nodes.
bpng.register_node(TestNodeFoo)
bpng.register_node(TestNodeBar)
bpng.register_node(TextInputNode)
bpng.register_node(DropdownMenuNode)


class NodeGraph(bpng.NodeGraph):

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

    node_graph = NodeGraph()

    # create the nodes.
    node1 = TestNodeFoo('Foo Node')
    node2 = TestNodeBar('Bar Node')
    node3 = TextInputNode('Test Node 1')
    node4 = DropdownMenuNode('Test Node 2')

    # add nodes into the scene.
    node_graph.add_node(node1)
    node_graph.add_node(node2)
    node_graph.add_node(node3)
    node_graph.add_node(node4)

    # position the nodes.
    node1.set_xy_pos(-250.0, 250.0)
    node2.set_xy_pos(-250.0, -150.0)
    node3.set_xy_pos(250.0, 50.0)
    node4.set_xy_pos(300.0, 80.0)

    # connect "node_1" to "node_3"
    node1.output('apples').connect_to(node3.input('hello'))

    # show node graph.
    node_graph.show()
    app.exec_()
