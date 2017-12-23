from bpNodeGraph.interfaces import Node


class TextInputNode(Node):
    """
    A example of a node with a added text input.
    """

    NODE_NAME = 'input node'
    NODE_TYPE = 'TextInputNode'

    def __init__(self):
        super(TextInputNode, self).__init__()

        # create input & output ports
        self.add_input('hello')
        self.add_output('world')

        # create text input field to node.
        self.add_text_input('my_input', 'Text Input')


class DropdownMenuNode(Node):
    """
    A example of a node with a added menu and a few input & outputs.
    """

    NODE_NAME = 'menu node'
    NODE_TYPE = 'DropdownMenuNode'

    def __init__(self):
        super(DropdownMenuNode, self).__init__()

        # create input & output ports
        self.add_input('hello')
        self.add_output('world')
        self.add_output('foo')

        # create menu to node.
        items = ['item 1', 'item2', 'item3']
        self.add_menu('my_menu_1', 'Menu Test', items=items)
