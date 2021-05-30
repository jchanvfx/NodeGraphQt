#!/usr/bin/python
# -*- coding: utf-8 -*-
from collections import defaultdict

from Qt import QtWidgets, QtCore, QtGui

from NodeGraphQt.constants import URN_SCHEME


class NodesGridDelagate(QtWidgets.QStyledItemDelegate):

    def paint(self, painter, option, index):
        """
        Args:
            painter (QtGui.QPainter):
            option (QtGui.QStyleOptionViewItem):
            index (QtCore.QModelIndex):
        """
        if index.column() != 0:
            super(NodesGridDelagate, self).paint(painter, option, index)
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
        painter.drawRoundRect(base_rect,
                              int(base_rect.height()/radius),
                              int(base_rect.width()/radius))

        pen_color = option.palette.midlight().color().darker(130)
        if option.state & QtWidgets.QStyle.State_Selected:
            pen_color = option.palette.highlight().color()
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
        painter.drawRoundRect(sub_rect,
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
        font_width = font_metrics.width(item.text().replace(' ', '_'))
        font_height = font_metrics.height()
        text_rect = QtCore.QRectF(
            sub_rect.center().x() - (font_width / 2),
            sub_rect.center().y() - (font_height * 0.55),
            font_width, font_height)
        painter.drawText(text_rect, item.text())
        painter.restore()


class NodesGridProxyModel(QtCore.QSortFilterProxyModel):

    def __init__(self, parent=None):
        super(NodesGridProxyModel, self).__init__(parent)
        
    def mimeData(self, indexes):
        node_ids = ['node:{}'.format(i.data(QtCore.Qt.ToolTipRole))
                    for i in indexes]
        node_urn = URN_SCHEME + ';'.join(node_ids)
        mime_data = super(NodesGridProxyModel, self).mimeData(indexes)
        mime_data.setUrls([node_urn])
        return mime_data


class NodesGridView(QtWidgets.QListView):

    def __init__(self, parent=None):
        super(NodesGridView, self).__init__(parent)
        self.setSelectionMode(self.ExtendedSelection)
        self.setUniformItemSizes(True)
        self.setResizeMode(self.Adjust)
        self.setViewMode(self.IconMode)
        self.setDragDropMode(self.DragOnly)
        self.setDragEnabled(True)
        self.setMinimumSize(450, 300)
        self.setSpacing(4)

        model = QtGui.QStandardItemModel()
        proxy_model = NodesGridProxyModel()
        proxy_model.setSourceModel(model)
        self.setModel(proxy_model)
        self.setItemDelegate(NodesGridDelagate(self))

    def clear(self):
        self.model().sourceMode().clear()

    def add_item(self, label, tooltip=''):
        item = QtGui.QStandardItem(label)
        item.setSizeHint(QtCore.QSize(130, 40))
        item.setToolTip(tooltip)
        model = self.model().sourceModel()
        model.appendRow(item)


class NodesPaletteWidget(QtWidgets.QWidget):

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

    def __repr__(self):
        return '<{} object at {}>'.format(
            self.__class__.__name__, hex(id(self))
        )

    def _build_ui(self):
        """
        populate the ui
        """
        categories = set()
        node_types = defaultdict(list)
        for name, node_ids in self._factory.names.items():
            for nid in node_ids:
                category = '.'.join(nid.split('.')[:-1])
                categories.add(category)
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

    def update(self):
        """
        Update and refresh the node palette widget.
        """
        self._build_tree()





