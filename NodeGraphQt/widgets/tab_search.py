#!/usr/bin/python
from PySide import QtGui, QtCore

from .stylesheet import STYLE_TABSEARCH, STYLE_TABSEARCH_LIST


class TabSearchCompleter(QtGui.QCompleter):
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
            self._filter_model.setSourceModel(QtGui.QStringListModel([path]))
            return [path]
        return []

    def updateModel(self):
        if not self._using_orig_model:
            self._filter_model.setSourceModel(self.source_model)

        pattern = QtCore.QRegExp(self._local_completion_prefix,
                                 QtCore.Qt.CaseInsensitive,
                                 QtCore.QRegExp.FixedString)
        self._filter_model.setFilterRegExp(pattern)

    def setModel(self, model):
        self._source_model = model
        self._filter_model = QtGui.QSortFilterProxyModel(self)
        self._filter_model.setSourceModel(self._source_model)
        super(TabSearchCompleter, self).setModel(self._filter_model)
        self.popup().setStyleSheet(STYLE_TABSEARCH_LIST)
        self._using_orig_model = True


class TabSearchWidget(QtGui.QLineEdit):

    search_submitted = QtCore.Signal(str)

    def __init__(self, parent=None, node_names=None):
        super(TabSearchWidget, self).__init__(parent)
        self.setStyleSheet(STYLE_TABSEARCH)
        self.setMinimumSize(200, 22)
        self.setTextMargins(5, 0, 5, 0)

        self._node_names = node_names or []

        self._model = QtGui.QStringListModel(self._node_names, self)

        self._completer = TabSearchCompleter()
        self._completer.setModel(self._model)
        self.setCompleter(self._completer)

        self.returnPressed.connect(self._on_search_submitted)

    def _on_search_submitted(self):
        text = self.text()
        if text:
            self.search_submitted.emit(text)
        self.close()
        self.parentWidget().clearFocus()

    def showEvent(self, event):
        super(TabSearchWidget, self).showEvent(event)
        self.setSelection(0, len(self.text()))
        self.setFocus()
