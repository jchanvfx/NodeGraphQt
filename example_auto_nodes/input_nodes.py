from NodeGraphQt import QtCore
from NodeGraphQt.constants import (NODE_PROP_VECTOR2,
                                   NODE_PROP_VECTOR3,
                                   NODE_PROP_VECTOR4)

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
        self.output = self.add_output('out', float)
        self.add_float_input('out', 'Float Value', value=0.0, range=(-10, 10))


class IntInputNode(AutoNode):
    """
    Input int data.
    """

    __identifier__ = 'Inputs'
    NODE_NAME = 'Int'

    def __init__(self):
        super(IntInputNode, self).__init__()
        self.output = self.add_output('out', int)
        self.add_int_input('out', 'Int Value', value=0)


class Vector2InputNode(AutoNode):
    __identifier__ = 'Inputs'
    NODE_NAME = 'Vector2'

    def __init__(self):
        super(Vector2InputNode, self).__init__()
        self.output = self.add_output('out', list)
        self.create_property(
            "out", [0.0, 0.0], widget_type=NODE_PROP_VECTOR2)


class Vector3InputNode(AutoNode):
    __identifier__ = 'Inputs'
    NODE_NAME = 'Vector3'

    def __init__(self):
        super(Vector3InputNode, self).__init__()
        self.output = self.add_output('out', list)
        self.create_property(
            "out", [0.0, 0.0, 0.0], widget_type=NODE_PROP_VECTOR3)


class Vector4InputNode(AutoNode):
    __identifier__ = 'Inputs'
    NODE_NAME = 'Vector4'

    def __init__(self):
        super(Vector4InputNode, self).__init__()
        self.output = self.add_output('out', list)
        self.create_property(
            "out", [0.0, 0.0, 0.0, 0.0], widget_type=NODE_PROP_VECTOR4)


class TickTimeNode(AutoNode):
    """
    Every second that passes adds a tick.
    """

    __identifier__ = 'Inputs'
    NODE_NAME = 'Tick Time'

    def __init__(self):
        super(TickTimeNode, self).__init__()
        self.add_output('out', float)
        self.add_float_input('out', 'Data Input', value=0.0)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.tick)
        self.timer.start(1000)

    def tick(self):
        if not self.disabled():
            current = self.get_property('out')
            current += 1
            self.set_property("out", current)


class TextFileInputNode(AutoNode):
    """
    Text File Input node data.
    """

    __identifier__ = 'Inputs'
    NODE_NAME = 'File'

    def __init__(self):
        super(TextFileInputNode, self).__init__()
        self.add_output('file content', str)
        self.create_property('file content', "")
        self.add_output('file path', str)
        self.add_file_input('file path', 'File Path')

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
            self.error('No exist %s' % path)
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


class BoolInputNode(AutoNode):
    """
    Input Bool data.
    """

    __identifier__ = 'Inputs'
    NODE_NAME = 'Bool'

    def __init__(self):
        super(BoolInputNode, self).__init__()
        self.add_output('out', bool)
        self.create_property('out', True)
        self.add_combo_menu('combo', 'Bool value', items=['True', 'False'])

    def run(self):
        self.set_property('out', eval(self.get_property('combo')))
