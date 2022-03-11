import os

from .properties import PropFileSavePath
from Qt import QtWidgets


class _element_widget(QtWidgets.QWidget):

    def __init__(self):
        super(_element_widget, self).__init__()
        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)


class NodePublishWidget(QtWidgets.QDialog):
    """
    Node publish dialog widget for publishing nodes.

    Args:
        node (NodeGraphQt.BaseNode): node object.
    """

    def __init__(self, node):
        super(NodePublishWidget, self).__init__()
        self.setWindowTitle('Publish Node')
        self.published = False

        self.node = node
        self.node_name = QtWidgets.QLineEdit(node.name())
        self.node_class_name = QtWidgets.QLineEdit(
            node.name().replace(' ', '_'))
        self.node_identifier = QtWidgets.QLineEdit('Custom')

        path = os.getcwd() + '/example_auto_nodes/published_nodes'
        if not os.path.exists(path):
            path = os.getcwd()
        path += '/' + self.node_class_name.text() + '.node'
        path = path.replace('\\', '/')

        self.file_path_widget = PropFileSavePath()
        self.file_path_widget.set_file_dir(path)
        self.file_path_widget.set_ext('*.json;*.node')
        self.file_path_widget.set_value(path)

        publish_btn = QtWidgets.QPushButton('Publish')
        publish_btn.pressed.connect(lambda: self.publish())

        cancel_btn = QtWidgets.QPushButton('Cancel')
        cancel_btn.pressed.connect(lambda: self.close())

        label = QtWidgets.QLabel('Node Name')
        label.setMinimumWidth(120)
        name_widget = _element_widget()
        name_widget.layout.addWidget(label)
        name_widget.layout.addWidget(self.node_name)

        label = QtWidgets.QLabel('Node Identifier')
        label.setMinimumWidth(120)
        identifier_widget = _element_widget()
        identifier_widget.layout.addWidget(label)
        identifier_widget.layout.addWidget(self.node_identifier)

        label = QtWidgets.QLabel('Node Class Name')
        label.setMinimumWidth(120)
        class_name_widget = _element_widget()
        class_name_widget.layout.addWidget(label)
        class_name_widget.layout.addWidget(self.node_class_name)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(4)
        layout.addWidget(name_widget)
        layout.addWidget(class_name_widget)
        layout.addWidget(identifier_widget)
        layout.addWidget(self.file_path_widget)
        layout.addWidget(publish_btn)
        layout.addWidget(cancel_btn)

        layout.addStretch()

    def publish(self):
        if self.published:
            return
        file_path = self.file_path_widget.get_value()
        node_name = self.node_name.text()
        node_identifier = self.node_identifier.text()
        node_class_name = self.node_class_name.text()
        self.node.publish(
            file_path, node_name, node_identifier, node_class_name)
        self.published = True
        self.close()

