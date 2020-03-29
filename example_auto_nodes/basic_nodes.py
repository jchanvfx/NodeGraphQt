from .node_base.auto_node import AutoNode
from .node_base.subgraph_node import SubGraphNode, BindInputNode, BindOutputNode


class SubGraph(SubGraphNode):
    __identifier__ = 'Utility'

    # initial default node name.
    NODE_NAME = 'Sub Graph'

    def __init__(self):
        super(SubGraph, self).__init__()

    def set_graph(self, graph):
        super(SubGraph, self).set_graph(graph)
        input = graph.create_node('Utility.BindInput',  pos=[-400, 0])
        output = graph.create_node('Utility.BindOutput', pos=[400, 0])
        input.set_parent(self)
        output.set_parent(self)


class RootGraph(SubGraphNode):
    __identifier__ = 'Utility'

    # initial default node name.
    NODE_NAME = 'Root Graph'

    def __init__(self):
        super(RootGraph, self).__init__()

    def set_graph(self, graph):
        super(RootGraph, self).set_graph(graph)
        graph.set_node_space(self)


class BindInput(BindInputNode):
    __identifier__ = 'Utility'

    # initial default node name.
    NODE_NAME = 'Bind Input'

    def __init__(self):
        super(BindInput, self).__init__()


class BindOutput(BindOutputNode):
    __identifier__ = 'Utility'

    # initial default node name.
    NODE_NAME = 'Bind Output'

    def __init__(self):
        super(BindOutput, self).__init__()


class FooNode(AutoNode):
    """
    A node class with 2 inputs and 2 outputs.
    """

    # unique node identifier.
    __identifier__ = 'examples'

    # initial default node name.
    NODE_NAME = 'foo node'

    def __init__(self):
        super(FooNode, self).__init__()

        # create node inputs.
        self.add_input('in A')
        self.add_input('in B')

        # create node outputs.
        self.add_output('out A')
        self.add_output('out B')
        self.set_icon("example_auto_nodes/icons/pear.png")


class BarNode(AutoNode):
    """
    A node class with 3 inputs and 3 outputs.
    The last input and last output can take in multiple pipes.
    """

    # unique node identifier.
    __identifier__ = 'examples'

    # initial default node name.
    NODE_NAME = 'bar'

    def __init__(self):
        super(BarNode, self).__init__()

        # create node inputs
        self.add_input('single in 1')
        self.add_input('single in 2')
        self.add_input('multi in', multi_input=True)

        # create node outputs
        self.add_output('single out 1', multi_output=False)
        self.add_output('single out 2', multi_output=False)
        self.add_output('multi out')
