from NodeGraphQt import QtWidgets, QtCore


class BaseListWidgetItem(QtWidgets.QListWidgetItem):

    def __eq__(self, other):
        return id(self) == id(other)


class NodeListWidget(QtWidgets.QTreeWidget):

    def __init__(self, parent=None):
        super(NodeListWidget, self).__init__(parent)
        self.setHeaderHidden(True)
        self._factory = None
        self._custom_labels = {}

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
            item = QtWidgets.QTreeWidgetItem(self, [label])
            item.setFirstColumnSpanned(True)
            item.setFlags(QtCore.Qt.ItemIsEnabled)
            self.addTopLevelItem(item)
            item.setExpanded(True)
            category_items[category] = item

        for node_id, node_name in node_types.items():
            category = '.'.join(node_id.split('.')[:-1])
            category_item = category_items[category]

            item = QtWidgets.QTreeWidgetItem(category_item, [node_name])
            item.setToolTip(0, node_id)

            category_item.addChild(item)

    def set_node_factory(self, factory):
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
        Update and refresh the node list widget.
        """
        self._build_tree()
