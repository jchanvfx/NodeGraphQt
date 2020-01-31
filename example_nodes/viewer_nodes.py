from NodeGraphQt import BaseNode


class DataViewerNode(BaseNode):
    __identifier__ = 'Viewers'
    NODE_NAME = 'Result View'

    def __init__(self):
        super(DataViewerNode, self).__init__()
        self.inPort = self.add_input('data')
        self.add_text_input('data', 'Data Viewer', tab='widgets')

    def run(self):
        """Evaluate input to show it."""
        for source in self.inPort.connected_ports():
            from_node = source.node()
            try:
                from_node.run()
            except Exception as error:
                print("%s no inputs connected: %s" %
                      (from_node.name(), str(error)))
                self.set_property('data', None)
                return
            value = from_node.get_property(source.name())
            self.set_property('data', str(value))

    def on_input_connected(self, to_port, from_port):
        """Override node callback method"""
        self.run()

    def on_input_disconnected(self, to_port, from_port):
        """Override node callback method"""
        self.set_property('data', None)