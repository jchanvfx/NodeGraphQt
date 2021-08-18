#!/usr/bin/python
import re
from collections import OrderedDict

from Qt import QtCore, QtWidgets, QtGui

from .stylesheet import STYLE_TABSEARCH, STYLE_TABSEARCH_LIST, STYLE_QMENU


class TabSearchCompleter(QtWidgets.QCompleter):
    """
    QCompleter adapted from:
    https://stackoverflow.com/questions/5129211/qcompleter-custom-completion-rules
    """

    def __init__(self, nodes=None, parent=None):
        super(TabSearchCompleter, self).__init__(nodes, parent)
        self.setCompletionMode(self.PopupCompletion)
        self.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self._local_completion_prefix = ''
        self._using_orig_model = False
        self._source_model = None
        self._filter_model = None

    def splitPath(self, path):
        self._local_completion_prefix = path
        self.updateModel()

        if self._filter_model.rowCount() == 0:
            self._using_orig_model = False
            self._filter_model.setSourceModel(QtCore.QStringListModel([]))
            return []
        return []

    def updateModel(self):
        if not self._using_orig_model:
            self._filter_model.setSourceModel(self._source_model)

        pattern = QtCore.QRegExp(self._local_completion_prefix,
                                 QtCore.Qt.CaseInsensitive,
                                 QtCore.QRegExp.FixedString)
        self._filter_model.setFilterRegExp(pattern)

    def setModel(self, model):
        self._source_model = model
        self._filter_model = QtCore.QSortFilterProxyModel(self)
        self._filter_model.setSourceModel(self._source_model)
        super(TabSearchCompleter, self).setModel(self._filter_model)
        self._using_orig_model = True


class TabSearchWidget(QtWidgets.QLineEdit):

    search_submitted = QtCore.Signal(str)

    def __init__(self, parent=None, node_dict=None):
        super(TabSearchWidget, self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_MacShowFocusRect, 0)
        self.setStyleSheet(STYLE_TABSEARCH)
        self.setMinimumSize(200, 22)
        self.setTextMargins(2, 0, 2, 0)
        self.hide()

        self._node_dict = node_dict or {}

        node_names = sorted(self._node_dict.keys())
        self._model = QtCore.QStringListModel(node_names, self)

        self._completer = TabSearchCompleter()
        self._completer.setModel(self._model)
        self.setCompleter(self._completer)

        popup = self._completer.popup()
        popup.setStyleSheet(STYLE_TABSEARCH_LIST)
        popup.clicked.connect(self._on_search_submitted)
        self.returnPressed.connect(self._on_search_submitted)

    def __repr__(self):
        return '<{} at {}>'.format(self.__class__.__name__, hex(id(self)))

    def _on_search_submitted(self, index=0):
        node_type = self._node_dict.get(self.text())
        if not node_type:
            model = self._completer.popup().model()
            text = model.data(model.index(0, 0))
            node_type = self._node_dict.get(text)

        if node_type:
            self.search_submitted.emit(node_type)

        self.close()
        self.parentWidget().clearFocus()

    def showEvent(self, event):
        super(TabSearchWidget, self).showEvent(event)
        self.setFocus()
        self.setText("")
        self.completer().popup().show()
        self.completer().complete()

    def mousePressEvent(self, event):
        if not self.text():
            self.completer().complete()

    def set_nodes(self, node_dict=None):
        self._node_dict = {}
        for name, node_types in node_dict.items():
            if len(node_types) == 1:
                self._node_dict[name] = node_types[0]
                continue
            for node_id in node_types:
                self._node_dict['{} ({})'.format(name, node_id)] = node_id
        node_names = sorted(self._node_dict.keys())
        self._model.setStringList(node_names)
        self._completer.setModel(self._model)


class TabSearchMenuWidget(QtWidgets.QMenu):

    search_submitted = QtCore.Signal(str)

    def __init__(self, node_dict=None):
        super(TabSearchMenuWidget, self).__init__()

        self.line_edit = QtWidgets.QLineEdit()
        self.line_edit.setAttribute(QtCore.Qt.WA_MacShowFocusRect, 0)
        self.line_edit.setStyleSheet(STYLE_TABSEARCH)
        self.line_edit.setMinimumSize(200, 22)
        self.line_edit.setTextMargins(2, 0, 2, 0)

        self._node_dict = node_dict or {}
        if self._node_dict:
            self._generate_items_from_node_dict()

        search_widget = QtWidgets.QWidgetAction(self)
        search_widget.setDefaultWidget(self.line_edit)
        self.addAction(search_widget)
        self.setStyleSheet(STYLE_QMENU)

        self._actions = {}
        self._menus = {}
        self._searched_actions = []

        self._block_submit = False

        self.rebuild = False

        self._wire_signals()

    def __repr__(self):
        return '<{} at {}>'.format(self.__class__.__name__, hex(id(self)))

    def keyPressEvent(self, event):
        super(TabSearchMenuWidget, self).keyPressEvent(event)
        self.line_edit.keyPressEvent(event)

    @staticmethod
    def _fuzzy_finder(key, collection):
        suggestions = []
        pattern = '.*?'.join(key.lower())
        regex = re.compile(pattern)
        for item in collection:
            match = regex.search(item.lower())
            if match:
                suggestions.append((len(match.group()), match.start(), item))

        return [x for _, _, x in sorted(suggestions)]

    def _wire_signals(self):
        self.line_edit.returnPressed.connect(self._on_search_submitted)
        self.line_edit.textChanged.connect(self._on_text_changed)

    def _on_text_changed(self, text):
        self._clear_actions()

        if not text:
            self._set_menu_visible(True)
            return

        self._set_menu_visible(False)

        action_names = self._fuzzy_finder(text, self._actions.keys())

        self._searched_actions = [self._actions[name] for name in action_names]
        self.addActions(self._searched_actions)

        if self._searched_actions:
            self.setActiveAction(self._searched_actions[0])

    def _clear_actions(self):
        for action in self._searched_actions:
            self.removeAction(action)
            action.triggered.connect(self._on_search_submitted)
        del self._searched_actions[:]

    def _set_menu_visible(self, visible):
        [menu.menuAction().setVisible(visible) for menu in self._menus.values()]

    def _close(self):
        self._set_menu_visible(False)
        self.setVisible(False)
        self.menuAction().setVisible(False)
        self._block_submit = True

    def _show(self):
        self.line_edit.setText("")
        self.line_edit.setFocus()
        self._set_menu_visible(True)
        self._block_submit = False
        self.exec_(QtGui.QCursor.pos())

    def _on_search_submitted(self):
        if not self._block_submit:
            action = self.sender()
            if type(action) is not QtWidgets.QAction:
                if len(self._searched_actions) > 0:
                    action = self._searched_actions[0]
                else:
                    self._close()
                    return

            text = action.text()
            node_type = self._node_dict.get(text)
            if node_type:
                self.search_submitted.emit(node_type)

        self._close()

    def build_menu_tree(self):
        node_types = sorted(self._node_dict.values())
        node_names = sorted(self._node_dict.keys())
        menu_tree = OrderedDict()

        max_depth = 0
        for node_type in node_types:
            trees = ".".join(node_type.split(".")[:-1]).split("::")
            for depth, menu_name in enumerate(trees):
                menu_path = "::".join(trees[:depth+1])
                if depth in menu_tree.keys():
                    if menu_name not in menu_tree[depth].keys():
                        new_menu = QtWidgets.QMenu(menu_name)
                        new_menu.keyPressEvent = self.keyPressEvent
                        new_menu.setStyleSheet(STYLE_QMENU)
                        menu_tree[depth][menu_path] = new_menu
                else:
                    new_menu = QtWidgets.QMenu(menu_name)
                    new_menu.setStyleSheet(STYLE_QMENU)
                    menu_tree[depth] = {menu_path: new_menu}
                if depth > 0:
                    new_menu.parentPath = "::".join(trees[:depth])

                max_depth = max(max_depth,depth)

        for i in range(max_depth+1):
            menus = menu_tree[i]
            for menu_path, menu in menus.items():
                self._menus[menu_path] = menu
                if i == 0:
                    self.addMenu(menu)
                else:
                    parentMenu = self._menus[menu.parentPath]
                    parentMenu.addMenu(menu)

        for name in node_names:
            action = QtWidgets.QAction(name, self)
            action.setText(name)
            action.triggered.connect(self._on_search_submitted)
            self._actions[name] = action

            menu_name = self._node_dict[name]
            menu_path = ".".join(menu_name.split(".")[:-1])

            if menu_path in self._menus.keys():
                self._menus[menu_path].addAction(action)
            else:
                self.addAction(action)

    def set_nodes(self, node_dict=None):
        if not self._node_dict or self.rebuild:
            self._node_dict.clear()
            self._clear_actions()
            self._set_menu_visible(False)
            [self.removeAction(menu.menuAction()) for menu in self._menus.values()]
            self._actions.clear()
            self._menus.clear()
            for name, node_types in node_dict.items():
                if len(node_types) == 1:
                    self._node_dict[name] = node_types[0]
                    continue
                for node_id in node_types:
                    self._node_dict['{} ({})'.format(name, node_id)] = node_id
            self.build_menu_tree()
            self.rebuild = False

        self._show()

