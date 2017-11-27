from BlueprintNodeGraph.interfaces import Node


class FooNode(Node):
    """
    A node class with 2 inputs and 2 outputs.
    """
    NODE_NAME = 'Foo'
    NODE_TYPE = 'FooNode'

    def __init__(self):
        super(FooNode, self).__init__()

        # create node inputs
        self.add_input('foo')
        self.add_input('bar')

        # create node outputs
        self.add_output('apples')
        self.add_output('bananas')


class BarNode(Node):
    """
    A node class with 3 inputs and 3 outputs.
    """
    NODE_NAME = 'Bar'
    NODE_TYPE = 'BarNode'

    def __init__(self):
        super(BarNode, self).__init__()

        # create node inputs
        self.add_input('hello')
        self.add_input('world')
        self.add_input('foo bar')

        # create node outputs
        self.add_output('apples')
        self.add_output('bananas')
        self.add_output('orange')
