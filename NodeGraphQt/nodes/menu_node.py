from NodeGraphQt import Node


class DropdownMenuNode(Node):
    """
    A example of a node with a added menu and a few input & outputs.
    """
    NODE_NAME = 'Menu node'

    def __init__(self):
        super(DropdownMenuNode, self).__init__()

        # create input & output ports
        self.add_input('hello')
        self.add_output('world')
        self.add_output('foo')

        # create menu to node.
        items = ['item 1', 'item2', 'item3']
        self.add_combo_menu('my_menu_1', 'Menu Test', items=items)
