import sys

from PySide import QtGui, QtCore

import BlueprintNodeGraph as bpng


class FooNode(bpng.Node):
    """
    A node class with 2 input ports and 2 output ports.
    """

    def __init__(self, name):
        super(FooNode, self).__init__(name)
        # create node inputs
        self.add_input('foo')
        self.add_input('bar')
        # create node outputs
        self.add_output('apples')
        self.add_output('bananas')


class BarNode(bpng.Node):
    """
    A node class with 3 input ports and 3 output ports.
    """

    def __init__(self, name):
        super(BarNode, self).__init__(name)
        # create node inputs
        self.add_input('hello')
        self.add_input('world')
        self.add_input('foo bar')
        # create node outputs
        self.add_output('apples')
        self.add_output('bananas')
        self.add_output('orange')


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
    node_1 = FooNode('Foo Node')
    node_2 = BarNode('Bar Node')

    node_3 = BarNode('Test Node 1')
    node_3.add_text_input('Text Input', 'Text Foo')

    node_4 = FooNode('Test Node 2')
    node_4.add_dropdown_menu('Combo Test', items=['foo', 'bar', 'test'])

    # add nodes into the scene.
    node_graph.add_node(node_1)
    node_graph.add_node(node_2)
    node_graph.add_node(node_3)
    node_graph.add_node(node_4)

    # position the nodes.
    node_1.set_xy_pos(-250.0, 250.0)
    node_2.set_xy_pos(-250.0, -150.0)
    node_3.set_xy_pos(250.0, 50.0)

    # connect "node_1" to "node_3"
    node1_output = node_1.get_output('apples')
    node3_input = node_3.get_input('world')

    node1_output.connect_to(node3_input)

    # show node graph.
    node_graph.show()
    app.exec_()
