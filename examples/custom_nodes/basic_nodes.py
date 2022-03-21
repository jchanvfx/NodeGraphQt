from NodeGraphQt import BaseNode


class BasicNodeA(BaseNode):
    """
    A node class with 2 inputs and 2 outputs.
    """

    # unique node identifier.
    __identifier__ = 'nodes.basic'

    # initial default node name.
    NODE_NAME = 'node A'

    def __init__(self):
        super(BasicNodeA, self).__init__()

        # create node inputs.
        self.add_input('in A')
        self.add_input('in B')

        # create node outputs.
        self.add_output('out A')
        self.add_output('out B')


class BasicNodeB(BaseNode):
    """
    A node class with 3 inputs and 3 outputs.
    The last input and last output can take in multiple pipes.
    """

    # unique node identifier.
    __identifier__ = 'nodes.basic'

    # initial default node name.
    NODE_NAME = 'node B'

    def __init__(self):
        super(BasicNodeB, self).__init__()

        # create node inputs
        self.add_input('single 1')
        self.add_input('single 2')
        self.add_input('multi in', multi_input=True)

        # create node outputs
        self.add_output('single 1', multi_output=False)
        self.add_output('single 2', multi_output=False)
        self.add_output('multi out')
