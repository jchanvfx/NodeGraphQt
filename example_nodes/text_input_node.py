from NodeGraphQt import Node


class TextInputNode(Node):
    """
    A example of a node with a embedded QlineEdit.
    """

    # unique node identifier.
    __identifier__ = 'com.chantasticvfx'

    # initial default node name.
    NODE_NAME = 'text'

    def __init__(self):
        super(TextInputNode, self).__init__()

        # create input & output ports
        self.add_input('in port')
        self.add_output('out port')

        # create QLineEdit text input widget.
        self.add_text_input('my_input', 'Text Input')
