#!/usr/bin/python

from NodeGraphQt import QtWidgets, QtCore


class NodesListWidget(QtWidgets.QTreeWidget):

    def __init__(self, parent=None):
        self.setColumnCount(1)

    def add_category(self, name, label):
        return
