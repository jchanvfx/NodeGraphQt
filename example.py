import sys

from PySide import QtGui

from BlueprintNodeGraph import NodeGraph, Node


class FooNode(Node):

    def __init__(self, name):
        super(FooNode, self).__init__(name)
        # create node inputs
        self.add_input('foo')
        self.add_input('bar')
        # create node outputs
        self.add_output('apples')
        self.add_output('bananas')
        self.add_output('orange')


class BarNode(Node):

    def __init__(self, name):
        super(BarNode, self).__init__(name)
        # create node inputs
        self.add_input('hello')
        self.add_input('world')
        self.add_input('test')
        # create node outputs
        self.add_output('apples')
        self.add_output('bananas')
        self.add_output('orange')


class TestNodeGraph(NodeGraph):

    def __init__(self, parent=None):
        super(TestNodeGraph, self).__init__(parent)
        self.setWindowTitle('Blueprint Node Graph')
        self.resize(1100, 800)


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)

    node_graph = TestNodeGraph()

    # create the nodes.
    node_1 = FooNode('Foo Node')
    node_2 = BarNode('Bar Node')
    node_3 = BarNode('Test Node 1')

    # add nodes into the scene.
    node_graph.add_node(node_1)
    node_graph.add_node(node_2)
    node_graph.add_node(node_3)
    node_graph.add_node(FooNode('Test Node 2'))

    # position the nodes.
    node_1.set_x_pos(-250.0)
    node_1.set_y_pos(250.0)
    node_2.set_x_pos(-250.0)
    node_2.set_y_pos(-150.0)
    node_3.set_x_pos(250.0)
    node_3.set_y_pos(50.0)

    # connect "node_1" to "node_3"
    node1_output = node_1.get_output('apples')
    node3_input = node_3.get_input('world')

    node1_output.connect_to(node3_input)

    # show node graph.
    node_graph.show()
    app.exec_()
