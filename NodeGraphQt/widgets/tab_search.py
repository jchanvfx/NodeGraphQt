#!/usr/bin/python
from .. import QtCore, QtWidgets, QtGui

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


class TabSearchMenuWidget(QtWidgets.QLineEdit):
    search_submitted = QtCore.Signal(str)

    def __init__(self, parent=None, node_dict=None):
        super(TabSearchMenuWidget, self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_MacShowFocusRect, 0)
        self.setStyleSheet(STYLE_TABSEARCH)
        self.setMinimumSize(200, 22)
        self.setTextMargins(2, 0, 2, 0)

        self._node_dict = node_dict or {}
        if self._node_dict:
            self._generate_items_from_node_dict()

        self.SearchMenu = QtWidgets.QMenu()
        searchWidget = QtWidgets.QWidgetAction(self)
        searchWidget.setDefaultWidget(self)
        self.SearchMenu.addAction(searchWidget)
        self.SearchMenu.setStyleSheet(STYLE_QMENU)

        self._actions = []
        self._menus = {}
        self._searched_actions = []

        self.returnPressed.connect(self._on_search_submitted)
        self.textChanged.connect(self._on_text_changed)

    def __repr__(self):
        return '<{} at {}>'.format(self.__class__.__name__, hex(id(self)))

    def _on_text_changed(self,text):
        self._clear_actions()

        if not text:
            self._set_menu_visible(True)
            return

        self._set_menu_visible(False)

        self._searched_actions = [action for action in self._actions\
                                 if text.lower() in action.text().lower()]

        self.SearchMenu.addActions(self._searched_actions)

    def _clear_actions(self):
        for action in self._searched_actions:
            self.SearchMenu.removeAction(action)
        self._searched_actions = []

    def _set_menu_visible(self,visible):
        for menu in self._menus.values():
            menu.menuAction().setVisible(visible)

    def _close(self):
        self._set_menu_visible(False)
        self.SearchMenu.setVisible(False)
        self.SearchMenu.menuAction().setVisible(False)

    def _show(self):
        self.SearchMenu.exec_(QtGui.QCursor.pos())
        self.setText("")
        self.setFocus()
        self._set_menu_visible(True)

    def _on_search_submitted(self):
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

    def _generate_items_from_node_dict(self):
        node_names = sorted(self._node_dict.keys())
        node_types = sorted(self._node_dict.values())

        self._menus.clear()
        self._actions.clear()
        self._searched_actions.clear()

        for node_type in node_types:
            menu_name = ".".join(node_type.split(".")[:-1])
            if menu_name not in self._menus.keys():
                new_menu = QtWidgets.QMenu(menu_name)
                new_menu.setStyleSheet(STYLE_QMENU)
                self._menus[menu_name] = new_menu
                self.SearchMenu.addMenu(new_menu)

        for name in node_names:
            action = QtWidgets.QAction(name, self)
            action.setText(name)
            action.triggered.connect(self._on_search_submitted)
            self._actions.append(action)

            menu_name = self._node_dict[name]
            menu_name = ".".join(menu_name.split(".")[:-1])

            if menu_name in self._menus.keys():
                self._menus[menu_name].addAction(action)
            else:
                self.SearchMenu.addAction(action)

    def set_nodes(self, node_dict=None):
        if not self._node_dict:
            self._node_dict.clear()
            for name, node_types in node_dict.items():
                if len(node_types) == 1:
                    self._node_dict[name] = node_types[0]
                    continue
                for node_id in node_types:
                    self._node_dict['{} ({})'.format(name, node_id)] = node_id
            self._generate_items_from_node_dict()

        self._show()

