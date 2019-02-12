#!/usr/bin/python
from PySide2 import QtWidgets, QtCore, QtGui

from NodeGraphQt.widgets.properties import NodePropWidget
from NodeGraphQt.constants import NODE_SEL_BORDER_COLOR


class PropertiesDelegate(QtWidgets.QStyledItemDelegate):

    def paint(self, painter, option, index):
        """
        Args:
            painter (QtGui.QPainter):
            option (QtGui.QStyleOptionViewItem):
            index (QtCore.QModelIndex):
        """
        rect = option.rect
        painter.save()
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(option.palette.midlight())
        painter.drawRect(rect)

        if option.state & QtWidgets.QStyle.State_Selected:
            bdr_clr = QtGui.QColor(*NODE_SEL_BORDER_COLOR)
            bdr_clr.setAlpha(80)
            painter.setPen(QtGui.QPen(bdr_clr, 1.5))
        else:
            bdr_clr = option.palette.dark().color()
            painter.setPen(QtGui.QPen(bdr_clr, 1))

        painter.setBrush(QtCore.Qt.NoBrush)
        rect = QtCore.QRect(rect.x() + 1,
                            rect.y() + 1,
                            rect.width() - 2,
                            rect.height() - 2)
        painter.drawRect(rect)
        painter.restore()


class PropertiesList(QtWidgets.QTableWidget):

    def __init__(self, parent=None):
        super(PropertiesList, self).__init__(parent)
        self.setItemDelegate(PropertiesDelegate())
        self.setColumnCount(1)
        self.setShowGrid(False)
        vh, hh = self.verticalHeader(), self.horizontalHeader()
        vh.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        vh.hide()
        hh.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        hh.hide()


class PropertiesBinWidget(QtWidgets.QWidget):

    #: Signal emitted (node_id, prop_name, prop_value)
    property_changed = QtCore.Signal(str, str, object)

    def __init__(self, parent=None):
        super(PropertiesBinWidget, self).__init__(parent)
        self.setWindowTitle('Properties Bin')
        self._prop_list = PropertiesList()
        self._limit = QtWidgets.QSpinBox()
        self._limit.setMaximum(10)
        self._limit.setMinimum(0)
        self.resize(400, 400)

        btn_clr = QtWidgets.QPushButton('clear bin')
        btn_clr.clicked.connect(self.clear_bin)

        top_layout = QtWidgets.QHBoxLayout()
        top_layout.addWidget(btn_clr)
        top_layout.addStretch(1)
        top_layout.addWidget(QtWidgets.QLabel('limit'))
        top_layout.addWidget(self._limit)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addLayout(top_layout)
        layout.addWidget(self._prop_list, 1)

    def __on_prop_close(self, node_id):
        items = self._prop_list.findItems(node_id, QtCore.Qt.MatchExactly)
        if items:
            item = items[0]
            self._prop_list.removeRow(item.row())

    def add_node(self, node):
        """
        Add node to the properties bin.

        Args:
            node (NodeGraphQt.Node): node object.
        """
        itm_find = self._prop_list.findItems(node.id, QtCore.Qt.MatchExactly)
        if itm_find:
            self._prop_list.removeRow(itm_find[0].row())

        self._prop_list.insertRow(0)
        prop_widget = NodePropWidget(node=node)
        prop_widget.property_changed.connect(self.property_changed.emit)
        prop_widget.property_closed.connect(self.__on_prop_close)
        self._prop_list.setCellWidget(0, 0, prop_widget)

        item = QtWidgets.QTableWidgetItem(node.id)
        # item.setForeground(QtGui.QBrush(QtGui.QColor(0, 0, 0, 0)))
        self._prop_list.setItem(0, 0, item)

    def remove_node(self, node):
        """
        Remove node from the properties bin.

        Args:
            node (NodeGraphQt.Node): node object.
        """
        self.__on_prop_close(node.id)

    def clear_bin(self):
        """
        Clear the properties bin.
        """
        self._prop_list.setRowCount(0)

    def prop_widget(self, node):
        """
        Returns the node property widget.

        Args:
            node (NodeGraphQt.Node): node object.

        Returns:
            NodePropWidget: node property widget.
        """
        itm_find = self._prop_list.findItems(node.id, QtCore.Qt.MatchExactly)
        if itm_find:
            item = itm_find[0]
            return self._prop_list.cellWidget(item.row(), 0)


if __name__ == '__main__':
    import sys
    from NodeGraphQt import Node, NodeGraph
    from NodeGraphQt.constants import (NODE_PROP_QLABEL,
                                       NODE_PROP_QLINEEDIT,
                                       NODE_PROP_QCOMBO,
                                       NODE_PROP_QSPINBOX,
                                       NODE_PROP_COLORPICKER,
                                       NODE_PROP_SLIDER)


    class TestNode(Node):
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

    prop_bin = PropertiesBinWidget()
    prop_bin.property_changed.connect(prop_changed)

    node = graph.create_node('nodeGraphQt.nodes.TestNode')

    prop_bin.add_node(node)
    prop_bin.show()

    app.exec_()