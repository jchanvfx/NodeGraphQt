#!/usr/bin/python
from collections import defaultdict

from Qt import QtWidgets, QtCore, QtGui, QtCompat

from .node_property_factory import NodePropertyWidgetFactory
from .prop_widgets_base import PropLineEdit


class _PropertiesDelegate(QtWidgets.QStyledItemDelegate):

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

        # draw background.
        bg_clr = option.palette.midlight().color()
        painter.setBrush(QtGui.QBrush(bg_clr))
        painter.drawRect(option.rect)

        # draw border.
        border_width = 1
        if option.state & QtWidgets.QStyle.State_Selected:
            bdr_clr = option.palette.highlight().color()
            painter.setPen(QtGui.QPen(bdr_clr, 1.5))
        else:
            bdr_clr = option.palette.alternateBase().color()
            painter.setPen(QtGui.QPen(bdr_clr, 1))

        painter.setBrush(QtCore.Qt.NoBrush)
        painter.drawRect(QtCore.QRect(
            option.rect.x() + border_width,
            option.rect.y() + border_width,
            option.rect.width() - (border_width * 2),
            option.rect.height() - (border_width * 2))
        )
        painter.restore()


class _PropertiesList(QtWidgets.QTableWidget):

    def __init__(self, parent=None):
        super(_PropertiesList, self).__init__(parent)
        self.setItemDelegate(_PropertiesDelegate())
        self.setColumnCount(1)
        self.setShowGrid(False)
        self.verticalHeader().hide()
        self.horizontalHeader().hide()

        QtCompat.QHeaderView.setSectionResizeMode(
            self.verticalHeader(), QtWidgets.QHeaderView.ResizeToContents)
        QtCompat.QHeaderView.setSectionResizeMode(
            self.horizontalHeader(), 0, QtWidgets.QHeaderView.Stretch)
        self.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)

    def wheelEvent(self, event):
        """
        Args:
            event (QtGui.QWheelEvent):
        """
        delta = event.angleDelta().y() * 0.2
        self.verticalScrollBar().setValue(
            self.verticalScrollBar().value() - delta
        )


class _PropertiesContainer(QtWidgets.QWidget):
    """
    Node properties container widget that displays nodes properties under
    a tab in the ``NodePropWidget`` widget.
    """

    def __init__(self, parent=None):
        super(_PropertiesContainer, self).__init__(parent)
        self.__layout = QtWidgets.QGridLayout()
        self.__layout.setColumnStretch(1, 1)
        self.__layout.setSpacing(6)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setAlignment(QtCore.Qt.AlignTop)
        layout.addLayout(self.__layout)

    def __repr__(self):
        return '<{} object at {}>'.format(
            self.__class__.__name__, hex(id(self))
        )

    def add_widget(self, name, widget, value, label=None):
        """
        Add a property widget to the window.

        Args:
            name (str): property name to be displayed.
            widget (BaseProperty): property widget.
            value (object): property value.
            label (str): custom label to display.
        """
        widget.setToolTip(name)
        widget.set_value(value)
        if label is None:
            label = name
        row = self.__layout.rowCount()
        if row > 0:
            row += 1

        label_flags = QtCore.Qt.AlignCenter | QtCore.Qt.AlignRight
        if widget.__class__.__name__ == 'PropTextEdit':
            label_flags = label_flags | QtCore.Qt.AlignTop

        self.__layout.addWidget(QtWidgets.QLabel(label), row, 0, label_flags)
        self.__layout.addWidget(widget, row, 1)

    def get_widget(self, name):
        """
        Returns the property widget from the name.

        Args:
            name (str): property name.

        Returns:
            QtWidgets.QWidget: property widget.
        """
        for row in range(self.__layout.rowCount()):
            item = self.__layout.itemAtPosition(row, 1)
            if item and name == item.widget().toolTip():
                return item.widget()


class NodePropWidget(QtWidgets.QWidget):
    """
    Node properties widget for display a Node object.

    Args:
        parent (QtWidgets.QWidget): parent object.
        node (NodeGraphQt.BaseNode): node.
    """

    #: signal (node_id, prop_name, prop_value)
    property_changed = QtCore.Signal(str, str, object)
    property_closed = QtCore.Signal(str)

    def __init__(self, parent=None, node=None):
        super(NodePropWidget, self).__init__(parent)
        self.__node_id = node.id
        self.__tab_windows = {}
        self.__tab = QtWidgets.QTabWidget()

        close_btn = QtWidgets.QPushButton()
        close_btn.setIcon(QtGui.QIcon(
            self.style().standardPixmap(QtWidgets.QStyle.SP_DialogCancelButton)
        ))
        close_btn.setMaximumWidth(40)
        close_btn.setToolTip('close property')
        close_btn.clicked.connect(self._on_close)

        self.name_wgt = PropLineEdit()
        self.name_wgt.setToolTip('name')
        self.name_wgt.set_value(node.name())
        self.name_wgt.value_changed.connect(self._on_property_changed)

        self.type_wgt = QtWidgets.QLabel(node.type_)
        self.type_wgt.setAlignment(QtCore.Qt.AlignRight)
        self.type_wgt.setToolTip('type_')
        font = self.type_wgt.font()
        font.setPointSize(10)
        self.type_wgt.setFont(font)

        name_layout = QtWidgets.QHBoxLayout()
        name_layout.setContentsMargins(0, 0, 0, 0)
        name_layout.addWidget(QtWidgets.QLabel('name'))
        name_layout.addWidget(self.name_wgt)
        name_layout.addWidget(close_btn)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(4)
        layout.addLayout(name_layout)
        layout.addWidget(self.__tab)
        layout.addWidget(self.type_wgt)
        self._read_node(node)

    def __repr__(self):
        return '<{} object at {}>'.format(
            self.__class__.__name__, hex(id(self))
        )

    def _on_close(self):
        """
        called by the close button.
        """
        self.property_closed.emit(self.__node_id)

    def _on_property_changed(self, name, value):
        """
        slot function called when a property widget has changed.

        Args:
            name (str): property name.
            value (object): new value.
        """
        self.property_changed.emit(self.__node_id, name, value)

    def _read_node(self, node):
        """
        Populate widget from a node.

        Args:
            node (NodeGraphQt.BaseNode): node class.
        """
        model = node.model
        graph_model = node.graph.model

        common_props = graph_model.get_node_common_properties(node.type_)

        # sort tabs and properties.
        tab_mapping = defaultdict(list)
        for prop_name, prop_val in model.custom_properties.items():
            tab_name = model.get_tab_name(prop_name)
            tab_mapping[tab_name].append((prop_name, prop_val))

        # add tabs.
        for tab in sorted(tab_mapping.keys()):
            if tab != 'Node':
                self.add_tab(tab)

        # property widget factory.
        widget_factory = NodePropertyWidgetFactory()

        # populate tab properties.
        for tab in sorted(tab_mapping.keys()):
            prop_window = self.__tab_windows[tab]
            for prop_name, value in tab_mapping[tab]:
                wid_type = model.get_widget_type(prop_name)
                if wid_type == 0:
                    continue

                widget = widget_factory.get_widget(wid_type)
                if prop_name in common_props.keys():
                    if 'items' in common_props[prop_name].keys():
                        widget.set_items(common_props[prop_name]['items'])
                    if 'range' in common_props[prop_name].keys():
                        prop_range = common_props[prop_name]['range']
                        widget.set_min(prop_range[0])
                        widget.set_max(prop_range[1])

                prop_window.add_widget(prop_name, widget, value,
                                       prop_name.replace('_', ' '))
                widget.value_changed.connect(self._on_property_changed)

        # add "Node" tab properties.
        self.add_tab('Node')
        default_props = ['color', 'text_color', 'disabled', 'id']
        prop_window = self.__tab_windows['Node']
        for prop_name in default_props:
            wid_type = model.get_widget_type(prop_name)
            widget = widget_factory.get_widget(wid_type)
            prop_window.add_widget(prop_name,
                                   widget,
                                   model.get_property(prop_name),
                                   prop_name.replace('_', ' '))

            widget.value_changed.connect(self._on_property_changed)

        self.type_wgt.setText(model.get_property('type_'))

    def node_id(self):
        """
        Returns the node id linked to the widget.

        Returns:
            str: node id
        """
        return self.__node_id

    def add_widget(self, name, widget, tab='Properties'):
        """
        add new node property widget.

        Args:
            name (str): property name.
            widget (BaseProperty): property widget.
            tab (str): tab name.
        """
        if tab not in self._widgets.keys():
            tab = 'Properties'
        window = self.__tab_windows[tab]
        window.add_widget(name, widget)
        widget.value_changed.connect(self._on_property_changed)

    def add_tab(self, name):
        """
        add a new tab.

        Args:
            name (str): tab name.

        Returns:
            PropListWidget: tab child widget.
        """
        if name in self.__tab_windows.keys():
            raise AssertionError('Tab name {} already taken!'.format(name))
        self.__tab_windows[name] = _PropertiesContainer(self)
        self.__tab.addTab(self.__tab_windows[name], name)
        return self.__tab_windows[name]

    def get_widget(self, name):
        """
        get property widget.

        Args:
            name (str): property name.

        Returns:
            QtWidgets.QWidget: property widget.
        """
        if name == 'name':
            return self.name_wgt
        for tab_name, prop_win in self.__tab_windows.items():
            widget = prop_win.get_widget(name)
            if widget:
                return widget


class PropertiesBinWidget(QtWidgets.QWidget):
    """
    The :class:`NodeGraphQt.PropertiesBinWidget` is a list widget for displaying
    and editing a nodes properties.

    .. image:: _images/prop_bin.png
        :width: 950px

    .. code-block:: python
        :linenos:

        from NodeGraphQt import NodeGraph, PropertiesBinWidget

        # create node graph.
        graph = NodeGraph()

        # create properties bin widget.
        properties_bin = PropertiesBinWidget(parent=None, node_graph=graph)
        properties_bin.show()

    See Also:
            :meth:`NodeGraphQt.BaseNode.add_custom_widget`,
            :meth:`NodeGraphQt.NodeObject.create_property`,
            :attr:`NodeGraphQt.constants.NodePropWidgetEnum`

    Args:
        parent (QtWidgets.QWidget): parent of the new widget.
        node_graph (NodeGraphQt.NodeGraph): node graph.
    """

    #: Signal emitted (node_id, prop_name, prop_value)
    property_changed = QtCore.Signal(str, str, object)

    def __init__(self, parent=None, node_graph=None):
        super(PropertiesBinWidget, self).__init__(parent)
        self.setWindowTitle('Properties Bin')
        self._prop_list = _PropertiesList()
        self._limit = QtWidgets.QSpinBox()
        self._limit.setToolTip('Set display nodes limit.')
        self._limit.setMaximum(10)
        self._limit.setMinimum(0)
        self._limit.setValue(2)
        self._limit.valueChanged.connect(self.__on_limit_changed)
        self.resize(450, 400)

        self._block_signal = False

        self._lock = False
        self.btn_lock = QtWidgets.QPushButton('Lock')
        self.btn_lock.setToolTip(
            'Lock the properties bin prevent nodes from being loaded.')
        self.btn_lock.clicked.connect(self.lock_bin)

        btn_clr = QtWidgets.QPushButton('Clear')
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
            prop_name (str): node property name.
            prop_value (object): node property value.
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
            node_id (str): node id.
            prop_name (str): node property name.
            prop_value (object): node property value.
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

        rows = self._prop_list.rowCount()
        if rows >= self.limit():
            self._prop_list.removeRow(rows - 1)

        itm_find = self._prop_list.findItems(node.id, QtCore.Qt.MatchExactly)
        if itm_find:
            self._prop_list.removeRow(itm_find[0].row())

        self._prop_list.insertRow(0)
        prop_widget = NodePropWidget(node=node)
        prop_widget.property_changed.connect(self.__on_property_widget_changed)
        prop_widget.property_closed.connect(self.__on_prop_close)
        self._prop_list.setCellWidget(0, 0, prop_widget)

        item = QtWidgets.QTableWidgetItem(node.id)
        self._prop_list.setItem(0, 0, item)
        self._prop_list.selectRow(0)

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
    from NodeGraphQt import BaseNode, NodeGraph
    from NodeGraphQt.constants import NodePropWidgetEnum


    class _TestNode(BaseNode):

        __identifier__ = 'property.test'
        NODE_NAME = 'test node'

        def __init__(self):
            super(_TestNode, self).__init__()
            self.create_property(
                'label_test',
                value='foo bar',
                widget_type=NodePropWidgetEnum.QLABEL.value
            )
            self.create_property(
                'text_edit',
                value='text edit test',
                widget_type=NodePropWidgetEnum.QLABEL.value
            )
            self.create_property(
                "file",
                value="",
                widget_type=NodePropWidgetEnum.FILE_OPEN.value
            )
            self.create_property(
                'color_picker',
                value=(0, 0, 255),
                widget_type=NodePropWidgetEnum.COLOR_PICKER.value
            )
            self.create_property(
                'integer',
                value=10,
                widget_type=NodePropWidgetEnum.QSPIN_BOX.value
            )
            self.create_property(
                'list',
                value='itm2',
                items=['itm1', 'itm2', 'itm3'],
                widget_type=NodePropWidgetEnum.QCOMBO_BOX.value
            )
            self.create_property(
                'range',
                value=50,
                range=(45, 55),
                widget_type=NodePropWidgetEnum.SLIDER.value
            )
            self.create_property(
                'float_range',
                value=150.5,
                range=(50.5, 200),
                widget_type=NodePropWidgetEnum.DOUBLE_SLIDER.value
            )
            self.create_property(
                'color4_picker',
                value=(255, 0, 0, 122),
                widget_type=NodePropWidgetEnum.COLOR4_PICKER.value
            )

    def _prop_changed(node_id, prop_name, prop_value):
        print('-'*100)
        print(node_id, prop_name, prop_value)


    app = QtWidgets.QApplication(sys.argv)

    graph = NodeGraph()
    graph.register_node(_TestNode)

    prop_bin = PropertiesBinWidget(node_graph=graph)
    prop_bin.resize(800, 600)
    prop_bin.property_changed.connect(_prop_changed)

    node = graph.create_node('property.test._TestNode')

    prop_bin.add_node(node)
    prop_bin.show()

    app.exec_()
