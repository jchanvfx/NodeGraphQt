#!/usr/bin/python
# -*- coding: utf-8 -*-
from collections import defaultdict

from Qt import QtWidgets, QtCore, QtGui

from NodeGraphQt.constants import MIME_TYPE, URN_SCHEME


class _NodesGridDelegate(QtWidgets.QStyledItemDelegate):

    def paint(self, painter, option, index):
        """
        Args:
            painter (QtGui.QPainter):
            option (QtGui.QStyleOptionViewItem):
            index (QtCore.QModelIndex):
        """
        if index.column() != 0:
            super(_NodesGridDelegate, self).paint(painter, option, index)
            return

        model = index.model().sourceModel()
        item = model.item(index.row(), index.column())

        sub_margin = 2
        radius = 5

        base_rect = QtCore.QRectF(
            option.rect.x() + sub_margin,
            option.rect.y() + sub_margin,
            option.rect.width() - (sub_margin * 2),
            option.rect.height() - (sub_margin * 2)
        )

        painter.save()
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)

        # background.
        bg_color = option.palette.window().color()
        pen_color = option.palette.midlight().color().lighter(120)
        if option.state & QtWidgets.QStyle.State_Selected:
            bg_color = bg_color.lighter(120)
            pen_color = pen_color.lighter(160)

        pen = QtGui.QPen(pen_color, 3.0)
        pen.setCapStyle(QtCore.Qt.RoundCap)
        painter.setPen(pen)
        painter.setBrush(QtGui.QBrush(bg_color))
        painter.drawRoundedRect(base_rect,
                              int(base_rect.height()/radius),
                              int(base_rect.width()/radius))

        if option.state & QtWidgets.QStyle.State_Selected:
            pen_color = option.palette.highlight().color()
        else:
            pen_color = option.palette.midlight().color().darker(130)
        pen = QtGui.QPen(pen_color, 1.0)
        pen.setCapStyle(QtCore.Qt.RoundCap)
        painter.setPen(pen)
        painter.setBrush(QtCore.Qt.NoBrush)

        sub_margin = 6
        sub_rect = QtCore.QRectF(
            base_rect.x() + sub_margin,
            base_rect.y() + sub_margin,
            base_rect.width() - (sub_margin * 2),
            base_rect.height() - (sub_margin * 2)
        )
        painter.drawRoundedRect(sub_rect,
                              int(sub_rect.height() / radius),
                              int(sub_rect.width() / radius))

        painter.setBrush(QtGui.QBrush(pen_color))
        edge_size = 2, sub_rect.height() - 6
        left_x = sub_rect.left()
        right_x = sub_rect.right() - edge_size[0]
        pos_y = sub_rect.center().y() - (edge_size[1] / 2)

        for pos_x in [left_x, right_x]:
            painter.drawRect(QtCore.QRectF(
                pos_x, pos_y, edge_size[0], edge_size[1]
            ))

        # painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtGui.QBrush(bg_color))
        dot_size = 4
        left_x = sub_rect.left() - 1
        right_x = sub_rect.right() - (dot_size - 1)
        pos_y = sub_rect.center().y() - (dot_size / 2)
        for pos_x in [left_x, right_x]:
            painter.drawEllipse(QtCore.QRectF(
                pos_x, pos_y, dot_size, dot_size
            ))
            pos_x -= dot_size + 2

        # text
        pen_color = option.palette.text().color()
        pen = QtGui.QPen(pen_color, 0.5)
        pen.setCapStyle(QtCore.Qt.RoundCap)
        painter.setPen(pen)

        font = painter.font()
        font_metrics = QtGui.QFontMetrics(font)
        item_text = item.text().replace(' ', '_')
        if hasattr(font_metrics, 'horizontalAdvance'):
            font_width = font_metrics.horizontalAdvance(item_text)
        else:
            font_width = font_metrics.width(item_text)
        font_height = font_metrics.height()
        text_rect = QtCore.QRectF(
            sub_rect.center().x() - (font_width / 2),
            sub_rect.center().y() - (font_height * 0.55),
            font_width, font_height)
        painter.drawText(text_rect, item.text())
        painter.restore()


class _NodesGridProxyModel(QtCore.QSortFilterProxyModel):

    def __init__(self, parent=None):
        super(_NodesGridProxyModel, self).__init__(parent)
        
    def mimeData(self, indexes, p_int=None):
        node_ids = [
            'node:{}'.format(i.data(QtCore.Qt.ToolTipRole))
            for i in indexes
        ]
        node_urn = URN_SCHEME + ';'.join(node_ids)
        mime_data = QtCore.QMimeData()
        mime_data.setData(MIME_TYPE, QtCore.QByteArray(node_urn.encode()))
        return mime_data


class NodesGridView(QtWidgets.QListView):

    def __init__(self, parent=None):
        super(NodesGridView, self).__init__(parent)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.setUniformItemSizes(True)
        self.setResizeMode(QtWidgets.QListView.Adjust)
        self.setViewMode(QtWidgets.QListView.IconMode)
        self.setDragDropMode(QtWidgets.QListView.DragOnly)
        self.setDragEnabled(True)
        self.setMinimumSize(300, 100)
        self.setSpacing(4)

        model = QtGui.QStandardItemModel()
        proxy_model = _NodesGridProxyModel()
        proxy_model.setSourceModel(model)
        self.setModel(proxy_model)
        self.setItemDelegate(_NodesGridDelegate(self))

    def clear(self):
        self.model().sourceModel().clear()

    def add_item(self, label, tooltip=''):
        item = QtGui.QStandardItem(label)
        item.setSizeHint(QtCore.QSize(130, 40))
        item.setToolTip(tooltip)
        model = self.model().sourceModel()
        model.appendRow(item)


class NodesPaletteWidget(QtWidgets.QWidget):
    """
    The :class:`NodeGraphQt.NodesPaletteWidget` is a widget for displaying all
    registered nodes from the node graph in a grid layout with this widget a
    user can create nodes by dragging and dropping.

    | *Implemented on NodeGraphQt:* ``v0.1.7``

    .. inheritance-diagram:: NodeGraphQt.NodesPaletteWidget
        :parts: 1

    .. image:: ../_images/nodes_palette.png
        :width: 400px

    .. code-block:: python
        :linenos:

        from NodeGraphQt import NodeGraph, NodesPaletteWidget

        # create node graph.
        graph = NodeGraph()

        # create nodes palette widget.
        nodes_palette = NodesPaletteWidget(parent=None, node_graph=graph)
        nodes_palette.show()

    Args:
        parent (QtWidgets.QWidget): parent of the new widget.
        node_graph (NodeGraphQt.NodeGraph): node graph.
    """

    def __init__(self, parent=None, node_graph=None):
        super(NodesPaletteWidget, self).__init__(parent)
        self.setWindowTitle('Nodes')

        self._category_tabs = {}
        self._custom_labels = {}
        self._factory = node_graph.node_factory if node_graph else None

        self._tab_widget = QtWidgets.QTabWidget()
        self._tab_widget.setMovable(True)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self._tab_widget)

        self._build_ui()

        # update the ui if new nodes are registered post init.
        node_graph.nodes_registered.connect(self._on_nodes_registered)

    def __repr__(self):
        return '<{} object at {}>'.format(
            self.__class__.__name__, hex(id(self))
        )

    def _on_nodes_registered(self, nodes):
        """
        Slot function when a new node has been registered into the node graph.

        Args:
            nodes (list[NodeObject]): node objects.
        """
        node_types = defaultdict(list)
        for node in nodes:
            name = node.NODE_NAME
            node_type = node.type_
            category = '.'.join(node_type.split('.')[:-1])
            node_types[category].append((node_type, name))

        update_tabs = False
        for category, nodes_list in node_types.items():
            if not update_tabs and category not in self._category_tabs:
                update_tabs = True
            grid_view = self._add_category_tab(category)
            for node_id, node_name in nodes_list:
                grid_view.add_item(node_name, node_id)

        if update_tabs:
            self._update_tab_labels()

    def _update_tab_labels(self):
        """
        Update the tab labels.
        """
        tabs_idx = {self._tab_widget.tabText(x): x
                    for x in range(self._tab_widget.count())}
        for category, label in self._custom_labels.items():
            if category in tabs_idx:
                idx = tabs_idx[category]
                self._tab_widget.setTabText(idx, label)

    def _build_ui(self):
        """
        populate the ui
        """
        node_types = defaultdict(list)
        for name, node_ids in self._factory.names.items():
            for nid in node_ids:
                category = '.'.join(nid.split('.')[:-1])
                node_types[category].append((nid, name))

        for category, nodes_list in node_types.items():
            grid_view = self._add_category_tab(category)
            for node_id, node_name in nodes_list:
                grid_view.add_item(node_name, node_id)

    def _set_node_factory(self, factory):
        """
        Set current node factory.

        Args:
            factory (NodeFactory): node factory.
        """
        self._factory = factory

    def _add_category_tab(self, category):
        """
        Adds a new tab to the node palette widget.

        Args:
            category (str): node identifier category eg. ``"nodes.widgets"``

        Returns:
            NodesGridView: nodes grid view widget.
        """
        if category not in self._category_tabs:
            grid_widget = NodesGridView(self)
            self._tab_widget.addTab(grid_widget, category)
            self._category_tabs[category] = grid_widget
        return self._category_tabs[category]

    def set_category_label(self, category, label):
        """
        Override tab label for a node category tab.

        Args:
            category (str): node identifier category eg. ``"nodes.widgets"``
            label (str): custom display label. eg. ``"Node Widgets"``
        """
        if label in self._custom_labels.values():
            labels = {v: k for k, v in self._custom_labels.items()}
            raise ValueError('label "{}" already in use for "{}"'
                             .format(label, labels[label]))
        previous_label = self._custom_labels.get(category, '')
        for idx in range(self._tab_widget.count()):
            tab_text = self._tab_widget.tabText(idx)
            if tab_text in [category, previous_label]:
                self._tab_widget.setTabText(idx, label)
                break
        self._custom_labels[category] = label

    def tab_widget(self):
        """
        Get the tab widget.

        Returns:
            QtWidgets.QTabWidget: tab widget.
        """
        return self._tab_widget

    def update(self):
        """
        Update and refresh the node palette widget.
        """
        for category, grid_view in self._category_tabs.items():
            grid_view.clear()

        node_types = defaultdict(list)
        for name, node_ids in self._factory.names.items():
            for nid in node_ids:
                category = '.'.join(nid.split('.')[:-1])
                node_types[category].append((nid, name))

        for category, nodes_list in node_types.items():
            grid_view = self._category_tabs.get(category)
            if not grid_view:
                grid_view = self._add_category_tab(category)

            for node_id, node_name in nodes_list:
                grid_view.add_item(node_name, node_id)

        self._update_tab_labels()
