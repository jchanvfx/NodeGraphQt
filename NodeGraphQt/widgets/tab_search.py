#!/usr/bin/python
from PySide import QtGui, QtCore

from .stylesheet import STYLE_TABSEARCH, STYLE_TABSEARCH_LIST


class TabSearchCompleter(QtGui.QCompleter):

    def __init__(self, parent=None, nodes=None):
        super(TabSearchCompleter, self).__init__(nodes, parent)


class TabSearchWidget(QtGui.QLineEdit):

    search_submitted = QtCore.Signal(str)

    def __init__(self, parent=None, node_list=None):
        super(TabSearchWidget, self).__init__(parent)
        self.setStyleSheet(STYLE_TABSEARCH)
        self.setMinimumSize(140, 24)
        self.setTextMargins(5, 0, 5, 0)
        self._node_list = node_list or []


        # #TODO wip continue from here.
        self._node_list = ['foo node', 'foo bar', 'bar', 'test', 'appleFoo']



        self._completer = QtGui.QCompleter(self._node_list)
        self._completer.setCompletionMode(QtGui.QCompleter.PopupCompletion)
        self._completer.popup().setStyleSheet(STYLE_TABSEARCH_LIST)
        self.setCompleter(self._completer)

        self.returnPressed.connect(self._on_search_submitted)

    def _on_search_submitted(self):
        text = self.text()
        if text:
            self.search_submitted.emit(text)
        self.close()
        self.parentWidget().clearFocus()

    def text_changed(self):
        pass

    def showEvent(self, event):
        super(TabSearchWidget, self).showEvent(event)
        self.setSelection(0, len(self.text()))
        self.setFocus()
