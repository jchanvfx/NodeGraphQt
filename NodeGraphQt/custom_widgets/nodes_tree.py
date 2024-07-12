#!/usr/bin/python
# -*- coding: utf-8 -*-
from Qt import QtWidgets, QtCore, QtGui

from NodeGraphQt.constants import MIME_TYPE, URN_SCHEME

TYPE_NODE = QtWidgets.QTreeWidgetItem.UserType + 1
TYPE_CATEGORY = QtWidgets.QTreeWidgetItem.UserType + 2


class _BaseNodeTreeItem(QtWidgets.QTreeWidgetItem):

    def __eq__(self, other):
        """
        Workaround fix for QTreeWidgetItem "operator not implemented error".
        see link: https://bugreports.qt.io/browse/PYSIDE-74
        """
        return id(self) == id(other)


class NodesTreeWidget(QtWidgets.QTreeWidget):
    """
    The :class:`NodeGraphQt.NodesTreeWidget` is a widget for displaying all
    registered nodes from the node graph with this widget a user can create
    nodes by dragging and dropping.

    .. inheritance-diagram:: NodeGraphQt.NodesTreeWidget
        :parts: 1
        :top-classes: PySide2.QtWidgets.QWidget

    .. image:: ../_images/nodes_tree.png
        :width: 300px

    .. code-block:: python
        :linenos:

        from NodeGraphQt import NodeGraph, NodesTreeWidget

        # create node graph.
        graph = NodeGraph()

        # create node tree widget.
        nodes_tree = NodesTreeWidget(parent=None, node_graph=graph)
        nodes_tree.show()

    Args:
        parent (QtWidgets.QWidget): parent of the new widget.
        node_graph (NodeGraphQt.NodeGraph): node graph.
    """

    def __init__(self, parent=None, node_graph=None):
        super(NodesTreeWidget, self).__init__(parent)
        self.setDragDropMode(QtWidgets.QAbstractItemView.DragOnly)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.setHeaderHidden(True)
        self.setWindowTitle('Nodes')

        self._factory = node_graph.node_factory if node_graph else None
        self._custom_labels = {}
        self._category_items = {}

        self._build_tree()

    def __repr__(self):
        return '<{} object at {}>'.format(
            self.__class__.__name__, hex(id(self))
        )

    def mimeData(self, items):
        node_ids = ['node:{}'.format(i.toolTip(0)) for i in items]
        node_urn = URN_SCHEME + ';'.join(node_ids)
        mime_data = QtCore.QMimeData()
        mime_data.setData(MIME_TYPE, QtCore.QByteArray(node_urn.encode()))
        return mime_data

    def _build_tree(self):
        """
        Populate the node tree.
        """
        self.clear()
        categories = set()
        node_types = {}
        for name, node_ids in self._factory.names.items():
            for nid in node_ids:
                categories.add('.'.join(nid.split('.')[:-1]))
                node_types[nid] = name

        self._category_items = {}
        for category in sorted(categories):
            if category in self._custom_labels.keys():
                label = self._custom_labels[category]
            else:
                label = '{}'.format(category)
            cat_item = _BaseNodeTreeItem(self, [label], type=TYPE_CATEGORY)
            cat_item.setFirstColumnSpanned(True)
            cat_item.setFlags(QtCore.Qt.ItemIsEnabled)
            cat_item.setSizeHint(0, QtCore.QSize(100, 26))
            self.addTopLevelItem(cat_item)
            cat_item.setExpanded(True)
            self._category_items[category] = cat_item

        for node_id, node_name in node_types.items():
            category = '.'.join(node_id.split('.')[:-1])
            category_item = self._category_items[category]

            item = _BaseNodeTreeItem(category_item, [node_name], type=TYPE_NODE)
            item.setToolTip(0, node_id)
            item.setSizeHint(0, QtCore.QSize(100, 26))

            category_item.addChild(item)

    def _set_node_factory(self, factory):
        """
        Set current node factory.

        Args:
            factory (NodeFactory): node factory.
        """
        self._factory = factory

    def set_category_label(self, category, label):
        """
        Override the label for a node category root item.

        .. image:: ../_images/nodes_tree_category_label.png
            :width: 70%

        Args:
            category (str): node identifier category eg. ``"nodes.widgets"``
            label (str): custom display label. eg. ``"Node Widgets"``
        """
        self._custom_labels[category] = label
        if category in self._category_items:
            item = self._category_items[category]
            item.setText(0, label)

    def update(self):
        """
        Update and refresh the node tree widget.
        """
        self._build_tree()
