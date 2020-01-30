from NodeGraphQt import BaseNode, QtCore


class ifNode(BaseNode):
    """
    if node.
    """

    __identifier__ = 'Logics'
    NODE_NAME = 'If'

    def __init__(self):
        super(ifNode, self).__init__()
        self.condition = self.add_input('condition')
        self.create_property('condition', None)
        self._then = self.add_input('then')
        self._else = self.add_input('else')
        self.add_output('out')
        self.create_property('out',  None)

    def run(self):
        for port in self.condition.connected_ports():
            port.node().run()
            if port.node().get_property(port.name()):
                result = self._then
            else:
                result = self._else

        for port in result.connected_ports():
            port.node().run()
            self.set_property('out', port.node().get_property(port.name()))
            break

    def on_input_connected(self, to_port, from_port):
        """Override node callback method."""
        from_port.node().run()
        self.set_property(to_port.name(), from_port.node().get_property(from_port.name()))
        self.update_streams()

    def on_input_disconnected(self, to_port, from_port):
        """Override node callback method."""
        self.set_property('out', None)
