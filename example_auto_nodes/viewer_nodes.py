from .node_base.auto_node import AutoNode


class DataViewerNode(AutoNode):
    __identifier__ = 'Viewers'
    NODE_NAME = 'Result View'

    def __init__(self):
        super(DataViewerNode, self).__init__()
        self.add_input('in data')
        self.add_text_input('data', 'Data Viewer',multi_line=True)
        self.add_output("out")
        self.create_property("out",None)

    def run(self):
        """Evaluate input to show it."""
        value = self.getInputData(0)
        if type(value) == float:
            self.set_property('data', "{:.10f}".format(value))
        else:
            self.set_property('data', str(value))
        self.set_property('out', value)
