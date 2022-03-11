from Qt import QtWidgets, QtCore

from .stylesheet import STYLE_SLASH_BUTTON, STYLE_NODE_BUTTON


class node_space_bar(QtWidgets.QWidget):

    def __init__(self, graph):
        super(node_space_bar, self).__init__()
        self.setMaximumHeight(20)
        self._layout = QtWidgets.QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)
        self.graph = graph
        self.update_path()

    def update_path(self):
        self.set_node(self.graph.get_node_space())

    def add_slash(self):
        btn_slash = QtWidgets.QPushButton("/")
        btn_slash.setFixedWidth(7)
        btn_slash.setStyleSheet(STYLE_SLASH_BUTTON)
        btn_slash.setFixedHeight(20)
        self._layout.addWidget(btn_slash, QtCore.Qt.AlignLeft)

    def add_node(self, node):
        node_name = node.name()
        btn_node = QtWidgets.QPushButton(node_name)
        btn_node.setFixedWidth(len(node_name)*8)
        btn_node.setStyleSheet(STYLE_NODE_BUTTON)
        btn_node.setFixedHeight(20)
        btn_node.clicked.connect(lambda: self.graph.set_node_space(node))
        self._layout.addWidget(btn_node, QtCore.Qt.AlignLeft)

    def clear(self):
        while self._layout.count():
            child = self._layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def set_node(self, node):
        self.clear()
        if node is None:
            self.add_slash()
        else:
            nodes = [node]
            while True:
                parent_node = node.parent()
                if parent_node is None:
                    break
                nodes.append(parent_node)
                node = parent_node

            for node in reversed(nodes):
                self.add_slash()
                self.add_node(node)

        self._layout.addStretch()
        self.update()
