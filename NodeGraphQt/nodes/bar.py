from NodeGraphQt.interfaces import Node


class BarNode(Node):
    """
    A node class with 3 inputs and 3 outputs.
    """
    NODE_TYPE = 'BarNode'

    def __init__(self):
        super(BarNode, self).__init__()
        self.set_name('Bar')

        # create node inputs
        self.add_input('hello')
        self.add_input('world')
        self.add_input('foo bar')

        # create node outputs
        self.add_output('apples', multi_output=False)
        self.add_output('bananas', multi_output=False)
        self.add_output('orange', display_name=False)
