#!/usr/bin/python
from .. import QtCore, QtWidgets
from .stylesheet import STYLE_QMENU


class BaseMenu(QtWidgets.QMenu):

    def __init__(self, *args, **kwargs):
        super(BaseMenu, self).__init__(*args, **kwargs)
        self.setStyleSheet(STYLE_QMENU)
        self.node_class = None
        self.graph = None

    # disable for issue #142
    # def hideEvent(self, event):
    #     super(BaseMenu, self).hideEvent(event)
    #     for a in self.actions():
    #         if hasattr(a, 'node_id'):
    #             a.node_id = None

    def get_menu(self, name, node_id=None):
        for action in self.actions():
            menu = action.menu()
            if not menu:
                continue
            if menu.title() == name:
                return menu
            if node_id and menu.node_class:
                node = menu.graph.get_node_by_id(node_id)
                if isinstance(node, menu.node_class):
                    return menu

    def get_menus(self, node_class):
        menus = []
        for action in self.actions():
            menu = action.menu()
            if menu.node_class:
                if issubclass(menu.node_class, node_class):
                    menus.append(menu)
        return menus


class GraphAction(QtWidgets.QAction):

    executed = QtCore.Signal(object)

    def __init__(self, *args, **kwargs):
        super(GraphAction, self).__init__(*args, **kwargs)
        self.graph = None
        self.triggered.connect(self._on_triggered)

    def _on_triggered(self):
        self.executed.emit(self.graph)

    def get_action(self, name):
        for action in self.qmenu.actions():
            if not action.menu() and action.text() == name:
                return action


class NodeAction(GraphAction):

    executed = QtCore.Signal(object, object)

    def __init__(self, *args, **kwargs):
        super(NodeAction, self).__init__(*args, **kwargs)
        self.node_id = None

    def _on_triggered(self):
        node = self.graph.get_node_by_id(self.node_id)
        self.executed.emit(self.graph, node)
