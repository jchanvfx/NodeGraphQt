from NodeGraphQt import Node


class DropdownMenuNode(Node):
    """
    A example node with a embedded added QCombobox menu.
    """

    # unique node identifier.
    __identifier__ = 'com.chantasticvfx'

    # initial default node name.
    NODE_NAME = 'menu'

    def __init__(self):
        super(DropdownMenuNode, self).__init__()

        # create input & output ports
        self.add_input('hello')
        self.add_output('world')
        self.add_output('foo')

        # create the QComboBox menu.
        items = ['item 1', 'item2', 'item3']
        self.add_combo_menu('my_menu', 'Menu Test', items=items)
