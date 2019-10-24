from NodeGraphQt import BaseNode


class FooNode(BaseNode):
    """
    A node class with 2 inputs and 2 outputs.
    """

    # unique node identifier.
    __identifier__ = 'com.chantasticvfx'

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


class BarNode(BaseNode):
    """
    A node class with 3 inputs and 3 outputs.
    The last input and last output can take in multiple pipes.
    """

    # unique node identifier.
    __identifier__ = 'com.chantasticvfx'

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
