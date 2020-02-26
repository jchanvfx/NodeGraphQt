#!/usr/bin/python
# -*- coding: utf-8 -*-
from .. import QtWidgets, QtCore
from ..constants import DRAG_DROP_ID


TYPE_NODE = QtWidgets.QTreeWidgetItem.UserType + 1
TYPE_CATEGORY = QtWidgets.QTreeWidgetItem.UserType + 2


class BaseNodeTreeItem(QtWidgets.QTreeWidgetItem):

    def __eq__(self, other):
        """
        Workaround fix for QTreeWidgetItem "operator not implemented error".
        see link: https://bugreports.qt.io/browse/PYSIDE-74
        """
        return id(self) == id(other)


class NodeTreeWidget(QtWidgets.QTreeWidget):
    """
    Node tree for displaying node types.

    Args:
        parent (QtWidgets.QWidget): parent of the new widget.
        node_graph (NodeGraphQt.NodeGraph): node graph.
    """

    def __init__(self, parent=None, node_graph=None):
        super(NodeTreeWidget, self).__init__(parent)
        self.setDragDropMode(QtWidgets.QAbstractItemView.DragOnly)
        self.setHeaderHidden(True)
        self._factory = None
        self._custom_labels = {}
        self._set_node_factory(node_graph._node_factory)

    def __repr__(self):
        return '<{} object at {}>'.format(self.__class__.__name__, hex(id(self)))

    def mimeData(self, items):
        node_ids = ','.join(i.toolTip(0) for i in items)
        mime_data = super(NodeTreeWidget, self).mimeData(items)
        mime_data.setText('<${}>:{}'.format(DRAG_DROP_ID, node_ids))
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

        category_items = {}
        for category in sorted(categories):
            if category in self._custom_labels.keys():
                label = self._custom_labels[category]
            else:
                label = '- {}'.format(category)
            cat_item = BaseNodeTreeItem(self, [label], type=TYPE_CATEGORY)
            cat_item.setFirstColumnSpanned(True)
            cat_item.setFlags(QtCore.Qt.ItemIsEnabled)
            self.addTopLevelItem(cat_item)
            cat_item.setExpanded(True)
            category_items[category] = cat_item

        for node_id, node_name in node_types.items():
            category = '.'.join(node_id.split('.')[:-1])
            category_item = category_items[category]

            item = BaseNodeTreeItem(category_item, [node_name], type=TYPE_NODE)
            item.setToolTip(0, node_id)

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
        Set custom display label for a node category.

        Args:
            category (str): node identifier category eg. "nodeGraphQt.nodes"
            label (str): custom display label.
        """
        self._custom_labels[category] = label

    def update(self):
        """
        Update and refresh the node tree widget.
        """
        self._build_tree()
