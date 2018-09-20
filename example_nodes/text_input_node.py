from NodeGraphQt import Node


class TextInputNode(Node):
    """
    A example of a node with a added text input.
    """

    # set unique node identifier.
    __identifier__ = 'com.chantasticvfx'

    # set initial default node name.
    NODE_NAME = 'Input text node'

    def __init__(self):
        super(TextInputNode, self).__init__()

        # create input & output ports
        self.add_input('hello')
        self.add_output('world')

        # create text input field to node.
        self.add_text_input('my_input', 'Text Input')
