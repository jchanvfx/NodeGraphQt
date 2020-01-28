from NodeGraphQt import QtCore
from .node_base.auto_node import AutoNode
import os

class FloatInputNode(AutoNode):
    """
    Input float data.
    """

    __identifier__ = 'Inputs'
    NODE_NAME = 'Float'

    def __init__(self):
        super(FloatInputNode, self).__init__()
        self.defaultValue = 0.0

        self.output = self.add_output('out',float)
        self.add_float_input('out', 'Float Value', value=self.defaultValue)
        self.view.widgets['out'].value_changed.connect(self.cook)


class TickTimeNode(AutoNode):
    """
    Every second that passes adds a tick.
    """

    __identifier__ = 'Inputs'
    NODE_NAME = 'Tick Time'

    def __init__(self):
        super(TickTimeNode, self).__init__()
        self.add_output('out',float)
        self.add_float_input('out', 'Data Input', value=0.0)
        self.view.widgets['out'].value_changed.connect(self.cook)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.tick)
        self.timer.start(1000)

    def tick(self):
        if not self.disabled():
            current = self.get_property('out')
            current += 1
            self.set_property("out",current)


class TextFileInputNode(AutoNode):
    """
    Text File Input node data.
    """

    __identifier__ = 'Inputs'
    NODE_NAME = 'File'

    def __init__(self):
        super(TextFileInputNode, self).__init__()
        self.add_output('file content',str)
        self.create_property('file content', "")
        self.add_output('file path', str)

        self.add_file_input('file path', 'File Path')
        self.view.widgets['file path'].value_changed.connect(self.cook)

    def run(self):
        path = self.get_property('file path')
        if os.path.exists(path):
            try:
                with open(path, 'r') as fread:
                    data = fread.read()
                    self.set_property('file content', data)
            except Exception as e:
                self.error(e)
        else:
            self.error('No existe %s' % path)
            self.set_property('file content', '')


class TextInputNode(AutoNode):
    """
    An example of a node with a embedded QLineEdit.
    """

    # unique node identifier.
    __identifier__ = 'Inputs'

    # initial default node name.
    NODE_NAME = 'Text'

    def __init__(self):
        super(TextInputNode, self).__init__()

        # create input & output ports
        self.add_output('out')

        # create QLineEdit text input widget.
        self.add_text_input('out', 'Text Input')
        self.view.widgets['out'].value_changed.connect(self.cook)
