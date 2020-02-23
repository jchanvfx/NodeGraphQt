#!/usr/bin/python
from .. import QtWidgets, QtCore, QtGui, QtCompat

from .properties import NodePropWidget


class PropertiesDelegate(QtWidgets.QStyledItemDelegate):

    def paint(self, painter, option, index):
        """
        Args:
            painter (QtGui.QPainter):
            option (QtGui.QStyleOptionViewItem):
            index (QtCore.QModelIndex):
        """
        painter.save()
        painter.setRenderHint(QtGui.QPainter.Antialiasing, False)
        painter.setPen(QtCore.Qt.NoPen)

        painter.setBrush(QtCore.Qt.NoBrush)
        painter.drawRect(option.rect)

        if option.state & QtWidgets.QStyle.State_Selected:
            bdr_clr = option.palette.highlight().color()
            painter.setPen(QtGui.QPen(bdr_clr, 1.5))
        else:
            bdr_clr = QtGui.QColor(100, 100, 100)
            painter.setPen(QtGui.QPen(bdr_clr, 1))

        painter.setBrush(QtCore.Qt.NoBrush)
        painter.drawRect(QtCore.QRect(option.rect.x() + 1,
                                      option.rect.y() + 1,
                                      option.rect.width() - 2,
                                      option.rect.height() - 2))
        painter.restore()


class PropertiesList(QtWidgets.QTableWidget):

    def __init__(self, parent=None):
        super(PropertiesList, self).__init__(parent)
        self.setItemDelegate(PropertiesDelegate())
        self.setColumnCount(1)
        self.setShowGrid(False)
        self.verticalHeader().hide()
        self.horizontalHeader().hide()
        QtCompat.QHeaderView.setSectionResizeMode(
            self.verticalHeader(), QtWidgets.QHeaderView.Stretch)
        QtCompat.QHeaderView.setSectionResizeMode(
            self.horizontalHeader(), 0, QtWidgets.QHeaderView.Stretch)
        self.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)

    def wheelEvent(self, event):
        delta = event.delta() * 0.2
        self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta)


class PropertiesBinWidget(QtWidgets.QWidget):
    """
    Node properties bin for displaying properties.

    Args:
        parent (QtWidgets.QWidget): parent of the new widget.
        node_graph (NodeGraphQt.NodeGraph): node graph.
    """

    #: Signal emitted (node_id, prop_name, prop_value)
    property_changed = QtCore.Signal(str, str, object)

    def __init__(self, parent=None, node_graph=None):
        super(PropertiesBinWidget, self).__init__(parent)
        self.setWindowTitle('Properties Bin')
        self._prop_list = PropertiesList()
        self._limit = QtWidgets.QSpinBox()
        self._limit.setToolTip('Set display nodes limit.')
        self._limit.setMaximum(10)
        self._limit.setMinimum(0)
        self._limit.setValue(2)
        self._limit.valueChanged.connect(self.__on_limit_changed)
        self.resize(450, 400)

        self._block_signal = False

        self._lock = False
        self.btn_lock = QtWidgets.QPushButton('lock')
        self.btn_lock.setToolTip(
            'Lock the properties bin prevent nodes from being loaded.')
        self.btn_lock.clicked.connect(self.lock_bin)

        btn_clr = QtWidgets.QPushButton('clear')
        btn_clr.setToolTip('Clear the properties bin.')
        btn_clr.clicked.connect(self.clear_bin)

        top_layout = QtWidgets.QHBoxLayout()
        top_layout.setSpacing(2)
        top_layout.addWidget(self._limit)
        top_layout.addStretch(1)
        top_layout.addWidget(self.btn_lock)
        top_layout.addWidget(btn_clr)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addLayout(top_layout)
        layout.addWidget(self._prop_list, 1)

        # wire up node graph.
        node_graph.add_properties_bin(self)
        node_graph.node_double_clicked.connect(self.add_node)
        node_graph.nodes_deleted.connect(self.__on_nodes_deleted)
        node_graph.property_changed.connect(self.__on_graph_property_changed)

    def __repr__(self):
        return '<{} object at {}>'.format(self.__class__.__name__, hex(id(self)))

    def __on_prop_close(self, node_id):
        items = self._prop_list.findItems(node_id, QtCore.Qt.MatchExactly)
        [self._prop_list.removeRow(i.row()) for i in items]

    def __on_limit_changed(self, value):
        rows = self._prop_list.rowCount()
        if rows > value:
            self._prop_list.removeRow(rows - 1)

    def __on_nodes_deleted(self, nodes):
        """
        Slot function when a node has been deleted.

        Args:
            nodes (list[str]): list of node ids.
        """
        [self.__on_prop_close(n) for n in nodes]

    def __on_graph_property_changed(self, node, prop_name, prop_value):
        """
        Slot function that updates the property bin from the node graph signal.

        Args:
            node (NodeGraphQt.NodeObject):
            prop_name (str):
            prop_value (object):
        """
        properties_widget = self.prop_widget(node)
        if not properties_widget:
            return

        property_window = properties_widget.get_widget(prop_name)

        if property_window and prop_value != property_window.get_value():
            self._block_signal = True
            property_window.set_value(prop_value)
            self._block_signal = False

    def __on_property_widget_changed(self, node_id, prop_name, prop_value):
        """
        Slot function triggered when a property widget value has changed.

        Args:
            node_id (str):
            prop_name (str):
            prop_value (object):
        """
        if not self._block_signal:
            self.property_changed.emit(node_id, prop_name, prop_value)

    def limit(self):
        """
        Returns the limit for how many nodes can be loaded into the bin.

        Returns:
            int: node limit.
        """
        return int(self._limit.value())

    def set_limit(self, limit):
        """
        Set limit of nodes to display.

        Args:
            limit (int): node limit.
        """
        self._limit.setValue(limit)

    def add_node(self, node):
        """
        Add node to the properties bin.

        Args:
            node (NodeGraphQt.NodeObject): node object.
        """
        if self.limit() == 0 or self._lock:
            return

        itm_find = self._prop_list.findItems(node.id, QtCore.Qt.MatchExactly)

        if itm_find:
            if itm_find[0].row() == 0:
                return
            self._prop_list.removeRow(itm_find[0].row())

        self._prop_list.insertRow(0)
        prop_widget = NodePropWidget(node=node)
        prop_widget.property_changed.connect(self.__on_property_widget_changed)
        prop_widget.property_closed.connect(self.__on_prop_close)
        self._prop_list.setCellWidget(0, 0, prop_widget)

        item = QtWidgets.QTableWidgetItem(node.id)
        self._prop_list.setItem(0, 0, item)
        self._prop_list.selectRow(0)

        rows = self._prop_list.rowCount()
        if rows > self.limit():
            self._prop_list.removeRow(rows - 1)

    def remove_node(self, node):
        """
        Remove node from the properties bin.

        Args:
            node (str or NodeGraphQt.BaseNode): node id or node object.
        """
        node_id = node if isinstance(node, str) else node.id
        self.__on_prop_close(node_id)

    def lock_bin(self):
        """
        Lock/UnLock the properties bin.
        """
        self._lock = not self._lock
        if self._lock:
            self.btn_lock.setText('UnLock')
        else:
            self.btn_lock.setText('Lock')

    def clear_bin(self):
        """
        Clear the properties bin.
        """
        self._prop_list.setRowCount(0)

    def prop_widget(self, node):
        """
        Returns the node property widget.

        Args:
            node (str or NodeGraphQt.NodeObject): node id or node object.

        Returns:
            NodePropWidget: node property widget.
        """
        node_id = node if isinstance(node, str) else node.id
        itm_find = self._prop_list.findItems(node_id, QtCore.Qt.MatchExactly)
        if itm_find:
            item = itm_find[0]
            return self._prop_list.cellWidget(item.row(), 0)


if __name__ == '__main__':
    import sys
    from .. import BaseNode, NodeGraph
    from ..constants import (NODE_PROP_QLABEL,
                            NODE_PROP_QLINEEDIT,
                            NODE_PROP_QCOMBO,
                            NODE_PROP_QSPINBOX,
                            NODE_PROP_COLORPICKER,
                            NODE_PROP_SLIDER)


    class TestNode(BaseNode):
        NODE_NAME = 'test node'

        def __init__(self):
            super(TestNode, self).__init__()
            self.create_property('label_test', 'foo bar',
                                 widget_type=NODE_PROP_QLABEL)
            self.create_property('text_edit', 'hello',
                                 widget_type=NODE_PROP_QLINEEDIT)
            self.create_property('color_picker', (0, 0, 255),
                                 widget_type=NODE_PROP_COLORPICKER)
            self.create_property('integer', 10,
                                 widget_type=NODE_PROP_QSPINBOX)
            self.create_property('list', 'foo',
                                 items=['foo', 'bar'],
                                 widget_type=NODE_PROP_QCOMBO)
            self.create_property('range', 50,
                                 range=(45, 55),
                                 widget_type=NODE_PROP_SLIDER)

    def prop_changed(node_id, prop_name, prop_value):
        print('-'*100)
        print(node_id, prop_name, prop_value)


    app = QtWidgets.QApplication(sys.argv)

    graph = NodeGraph()
    graph.register_node(TestNode)

    prop_bin = PropertiesBinWidget(node_graph=graph)
    prop_bin.property_changed.connect(prop_changed)

    node = graph.create_node('nodeGraphQt.nodes.TestNode')

    prop_bin.add_node(node)
    prop_bin.show()

    app.exec_()
