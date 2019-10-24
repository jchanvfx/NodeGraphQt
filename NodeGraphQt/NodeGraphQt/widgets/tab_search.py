#!/usr/bin/python
from NodeGraphQt import QtCore, QtWidgets

from NodeGraphQt.widgets.stylesheet import STYLE_TABSEARCH, STYLE_TABSEARCH_LIST


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
            self._filter_model.setSourceModel(QtCore.QStringListModel([path]))
            return [path]
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
        if node_type:
            self.search_submitted.emit(node_type)
        self.close()
        self.parentWidget().clearFocus()

    def showEvent(self, event):
        super(TabSearchWidget, self).showEvent(event)
        self.setSelection(0, len(self.text()))
        self.setFocus()
        if not self.text():
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
