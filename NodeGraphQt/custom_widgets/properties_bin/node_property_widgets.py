#!/usr/bin/python
from collections import defaultdict

from Qt import QtWidgets, QtCore, QtGui, QtCompat

from .node_property_factory import NodePropertyWidgetFactory
from .prop_widgets_base import PropLineEdit
from ...constants import NodeEnum   

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
        bg_clr = option.palette.base().color()
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
            self.verticalHeader(), QtWidgets.QHeaderView.ResizeToContents
        )
        QtCompat.QHeaderView.setSectionResizeMode(
            self.horizontalHeader(), 0, QtWidgets.QHeaderView.Stretch
        )
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

        self.__property_widgets = {}

    def __repr__(self):
        return '<{} object at {}>'.format(
            self.__class__.__name__, hex(id(self))
        )

    def add_widget(self, name, widget, value, label=None, tooltip=None):
        """
        Add a property widget to the window.

        Args:
            name (str): property name to be displayed.
            widget (BaseProperty): property widget.
            value (object): property value.
            label (str): custom label to display.
            tooltip (str): custom tooltip.
        """
        label = label or name
        label_widget = QtWidgets.QLabel(label)
        if tooltip:
            widget.setToolTip('{}\n{}'.format(name, tooltip))
            label_widget.setToolTip('{}\n{}'.format(name, tooltip))
        else:
            widget.setToolTip(name)
            label_widget.setToolTip(name)
        widget.set_value(value)
        row = self.__layout.rowCount()
        if row > 0:
            row += 1

        label_flags = QtCore.Qt.AlignCenter | QtCore.Qt.AlignRight
        if widget.__class__.__name__ == 'PropTextEdit':
            label_flags = label_flags | QtCore.Qt.AlignTop

        self.__layout.addWidget(label_widget, row, 0, label_flags)
        self.__layout.addWidget(widget, row, 1)
        self.__property_widgets[name] = widget

    def get_widget(self, name):
        """
        Returns the property widget from the name.

        Args:
            name (str): property name.

        Returns:
            QtWidgets.QWidget: property widget.
        """
        return self.__property_widgets.get(name)

    def get_all_widgets(self):
        """
        Returns the node property widgets.

        Returns:
            dict: {name: widget}
        """
        return self.__property_widgets


class _PortConnectionsContainer(QtWidgets.QWidget):
    """
    Port connection container widget that displays node ports and connections
    under a tab in the ``NodePropWidget`` widget.
    """

    def __init__(self, parent=None, node=None):
        super(_PortConnectionsContainer, self).__init__(parent)
        self._node = node
        self._ports = {}

        self.input_group, self.input_tree = self._build_tree_group(
            'Input Ports'
        )
        self.input_group.setToolTip('Display input port connections')
        for _, port in node.inputs().items():
            self._build_row(self.input_tree, port)
        for col in range(self.input_tree.columnCount()):
            self.input_tree.resizeColumnToContents(col)

        self.output_group, self.output_tree = self._build_tree_group(
            'Output Ports'
        )
        self.output_group.setToolTip('Display output port connections')
        for _, port in node.outputs().items():
            self._build_row(self.output_tree, port)
        for col in range(self.output_tree.columnCount()):
            self.output_tree.resizeColumnToContents(col)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.input_group)
        layout.addWidget(self.output_group)
        layout.addStretch()

        self.input_group.setChecked(False)
        self.input_tree.setVisible(False)
        self.output_group.setChecked(False)
        self.output_tree.setVisible(False)

    def __repr__(self):
        return '<{} object at {}>'.format(
            self.__class__.__name__, hex(id(self))
        )

    @staticmethod
    def _build_tree_group(title):
        """
        Build the ports group box and ports tree widget.

        Args:
            title (str): group box title.

        Returns:
            tuple(QtWidgets.QGroupBox, QtWidgets.QTreeWidget): widgets.
        """
        group_box = QtWidgets.QGroupBox()
        group_box.setMaximumHeight(200)
        group_box.setCheckable(True)
        group_box.setChecked(True)
        group_box.setTitle(title)
        group_box.setLayout(QtWidgets.QVBoxLayout())

        headers = ['Locked', 'Name', 'Connections', '']
        tree_widget = QtWidgets.QTreeWidget()
        tree_widget.setColumnCount(len(headers))
        tree_widget.setHeaderLabels(headers)
        tree_widget.setHeaderHidden(False)
        tree_widget.header().setStretchLastSection(False)
        QtCompat.QHeaderView.setSectionResizeMode(
            tree_widget.header(), 2, QtWidgets.QHeaderView.Stretch
        )

        group_box.layout().addWidget(tree_widget)

        return group_box, tree_widget

    def _build_row(self, tree, port):
        """
        Builds a new row in the parent ports tree widget.

        Args:
            tree (QtWidgets.QTreeWidget): parent port tree widget.
            port (NodeGraphQt.Port): port object.
        """
        item = QtWidgets.QTreeWidgetItem(tree)
        item.setFlags(item.flags() & ~QtCore.Qt.ItemIsSelectable)
        item.setText(1, port.name())
        item.setToolTip(0, 'Lock Port')
        item.setToolTip(1, 'Port Name')
        item.setToolTip(2, 'Select connected port.')
        item.setToolTip(3, 'Center on connected port node.')

        # TODO: will need to update this checkbox lock logic to work with
        #       the undo/redo functionality.
        lock_chb = QtWidgets.QCheckBox()
        lock_chb.setChecked(port.locked())
        lock_chb.clicked.connect(lambda x: port.set_locked(x))
        tree.setItemWidget(item, 0, lock_chb)

        combo = QtWidgets.QComboBox()
        for cp in port.connected_ports():
            item_name = '{} : "{}"'.format(cp.name(), cp.node().name())
            self._ports[item_name] = cp
            combo.addItem(item_name)
        tree.setItemWidget(item, 2, combo)

        focus_btn = QtWidgets.QPushButton()
        focus_btn.setIcon(QtGui.QIcon(
            tree.style().standardIcon(QtWidgets.QStyle.SP_DialogYesButton)
        ))
        focus_btn.clicked.connect(
            lambda: self._on_focus_to_node(self._ports.get(combo.currentText()))
        )
        tree.setItemWidget(item, 3, focus_btn)

    def _on_focus_to_node(self, port):
        """
        Slot function emits the node is of the connected port.

        Args:
            port (NodeGraphQt.Port): connected port.
        """
        if port:
            node = port.node()
            node.graph.center_on([node])
            node.graph.clear_selection()
            node.set_selected(True)

    def set_lock_controls_disable(self, disable=False):
        """
        Enable/Disable port lock column widgets.

        Args:
            disable (bool): true to disable checkbox.
        """
        for r in range(self.input_tree.topLevelItemCount()):
            item = self.input_tree.topLevelItem(r)
            chb_widget = self.input_tree.itemWidget(item, 0)
            chb_widget.setDisabled(disable)
        for r in range(self.output_tree.topLevelItemCount()):
            item = self.output_tree.topLevelItem(r)
            chb_widget = self.output_tree.itemWidget(item, 0)
            chb_widget.setDisabled(disable)


class NodePropEditorWidget(QtWidgets.QWidget):
    """
    Node properties editor widget for display a Node object.

    Args:
        parent (QtWidgets.QWidget): parent object.
        node (NodeGraphQt.NodeObject): node.
    """

    #: signal (node_id, prop_name, prop_value)
    property_changed = QtCore.Signal(str, str, object)
    property_closed = QtCore.Signal(str)

    def __init__(self, parent=None, node=None):
        super(NodePropEditorWidget, self).__init__(parent)
        self.__node_id = node.id
        self.__tab_windows = {}
        self.__tab = QtWidgets.QTabWidget()

        close_btn = QtWidgets.QPushButton()
        close_btn.setIcon(QtGui.QIcon(
            self.style().standardIcon(
                QtWidgets.QStyle.SP_DialogCloseButton
            )
        ))
        close_btn.setMaximumWidth(40)
        close_btn.setToolTip('close property')
        close_btn.clicked.connect(self._on_close)

        pixmap = QtGui.QPixmap()
        if node.icon():
            pixmap = QtGui.QPixmap(node.icon())

            if pixmap.size().height() > NodeEnum.ICON_SIZE.value:
                pixmap = pixmap.scaledToHeight(
                    NodeEnum.ICON_SIZE.value, QtCore.Qt.SmoothTransformation
                )
            if pixmap.size().width() > NodeEnum.ICON_SIZE.value:
                pixmap = pixmap.scaledToWidth(
                    NodeEnum.ICON_SIZE.value, QtCore.Qt.SmoothTransformation
                )

        self.icon_label = QtWidgets.QLabel(self)
        self.icon_label.setPixmap(pixmap)
        self.icon_label.setStyleSheet("background: transparent;")

        self.name_wgt = PropLineEdit()
        self.name_wgt.set_name('name')
        self.name_wgt.setToolTip('name\nSet the node name.')
        self.name_wgt.set_value(node.name())
        self.name_wgt.value_changed.connect(self._on_property_changed)

        self.type_wgt = QtWidgets.QLabel(node.type_)
        self.type_wgt.setAlignment(QtCore.Qt.AlignRight)
        self.type_wgt.setToolTip(
            'type_\nNode type identifier followed by the class name.'
        )
        font = self.type_wgt.font()
        font.setPointSize(10)
        self.type_wgt.setFont(font)

        name_layout = QtWidgets.QHBoxLayout()
        name_layout.setContentsMargins(0, 0, 0, 0)
        name_layout.addWidget(self.icon_label)
        name_layout.addWidget(QtWidgets.QLabel('name'))
        name_layout.addWidget(self.name_wgt)
        name_layout.addWidget(close_btn)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(4)
        layout.addLayout(name_layout)
        layout.addWidget(self.__tab)
        layout.addWidget(self.type_wgt)

        self._port_connections = self._read_node(node)

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

        Returns:
            _PortConnectionsContainer: ports container widget.
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
        reserved_tabs = ['Node', 'Ports']
        for tab in sorted(tab_mapping.keys()):
            if tab in reserved_tabs:
                print('tab name "{}" is reserved by the "NodePropWidget" '
                      'please use a different tab name.')
                continue
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
                widget.set_name(prop_name)

                tooltip = None
                if prop_name in common_props.keys():
                    if 'items' in common_props[prop_name].keys():
                        widget.set_items(common_props[prop_name]['items'])
                    if 'range' in common_props[prop_name].keys():
                        prop_range = common_props[prop_name]['range']
                        widget.set_min(prop_range[0])
                        widget.set_max(prop_range[1])
                    if 'tooltip' in common_props[prop_name].keys():
                        tooltip = common_props[prop_name]['tooltip']
                prop_window.add_widget(
                    name=prop_name,
                    widget=widget,
                    value=value,
                    label=prop_name.replace('_', ' '),
                    tooltip=tooltip
                )
                widget.value_changed.connect(self._on_property_changed)

        # add "Node" tab properties. (default props)
        self.add_tab('Node')
        default_props = {
            'color': 'Node base color.',
            'text_color': 'Node text color.',
            'border_color': 'Node border color.',
            'disabled': 'Disable/Enable node state.',
            'id': 'Unique identifier string to the node.'
        }
        prop_window = self.__tab_windows['Node']
        for prop_name, tooltip in default_props.items():
            wid_type = model.get_widget_type(prop_name)
            widget = widget_factory.get_widget(wid_type)
            widget.set_name(prop_name)
            prop_window.add_widget(
                name=prop_name,
                widget=widget,
                value=model.get_property(prop_name),
                label=prop_name.replace('_', ' '),
                tooltip=tooltip
            )

            widget.value_changed.connect(self._on_property_changed)

        self.type_wgt.setText(model.get_property('type_') or '')

        # add "ports" tab connections.
        ports_container = None
        if node.inputs() or node.outputs():
            ports_container = _PortConnectionsContainer(self, node=node)
            self.__tab.addTab(ports_container, 'Ports')

        # hide/remove empty tabs with no property widgets.
        tab_index = {
            self.__tab.tabText(x): x for x in range(self.__tab.count())
        }
        current_idx = None
        for tab_name, prop_window in self.__tab_windows.items():
            prop_widgets = prop_window.get_all_widgets()
            if not prop_widgets:
                # I prefer to hide the tab but in older version of pyside this
                # attribute doesn't exist we'll just remove.
                if hasattr(self.__tab, 'setTabVisible'):
                    self.__tab.setTabVisible(tab_index[tab_name], False)
                else:
                    self.__tab.removeTab(tab_index[tab_name])
                continue
            if current_idx is None:
                current_idx = tab_index[tab_name]

        self.__tab.setCurrentIndex(current_idx)

        return ports_container

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

    def get_tab_widget(self):
        """
        Returns the underlying tab widget.

        Returns:
            QtWidgets.QTabWidget: tab widget.
        """
        return self.__tab

    def get_widget(self, name):
        """
        get property widget.

        Args:
            name (str): property name.

        Returns:
            NodeGraphQt.custom_widgets.properties_bin.prop_widgets_abstract.BaseProperty: property widget.
        """
        if name == 'name':
            return self.name_wgt
        for prop_win in self.__tab_windows.values():
            widget = prop_win.get_widget(name)
            if widget:
                return widget

    def get_all_property_widgets(self):
        """
        get all the node property widgets.

        Returns:
            list[BaseProperty]: property widgets.
        """
        widgets = [self.name_wgt]
        for prop_win in self.__tab_windows.values():
            for widget in prop_win.get_all_widgets().values():
                widgets.append(widget)
        return widgets

    def get_port_connection_widget(self):
        """
        Returns the ports connections container widget.

        Returns:
            _PortConnectionsContainer: port container widget.
        """
        return self._port_connections

    def set_port_lock_widgets_disabled(self, disabled=True):
        """
        Enable/Disable port lock column widgets.

        Args:
            disabled (bool): true to disable checkbox.
        """
        self._port_connections.set_lock_controls_disable(disabled)


class PropertiesBinWidget(QtWidgets.QWidget):
    """
    The :class:`NodeGraphQt.PropertiesBinWidget` is a list widget for displaying
    and editing a nodes properties.

    .. inheritance-diagram:: NodeGraphQt.PropertiesBinWidget
        :parts: 1

    .. image:: ../_images/prop_bin.png
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

        # this attribute to block signals if for the "on_property_changed" signal
        # in case devs that don't implement the ".prop_widgets_abstract.BaseProperty"
        # widget properly to prevent an infinite loop.
        self._block_signal = False

        self._lock = False
        self._btn_lock = QtWidgets.QPushButton('Lock')
        self._btn_lock.setToolTip(
            'Lock the properties bin prevent nodes from being loaded.')
        self._btn_lock.clicked.connect(self.lock_bin)

        btn_clr = QtWidgets.QPushButton('Clear')
        btn_clr.setToolTip('Clear the properties bin.')
        btn_clr.clicked.connect(self.clear_bin)

        top_layout = QtWidgets.QHBoxLayout()
        top_layout.setSpacing(2)
        top_layout.addWidget(self._limit)
        top_layout.addStretch(1)
        top_layout.addWidget(self._btn_lock)
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
        return '<{} object at {}>'.format(
            self.__class__.__name__, hex(id(self))
        )

    def __on_port_tree_visible_changed(self, node_id, visible, tree_widget):
        """
        Triggered when the visibility of the port tree widget changes we
        resize the property list table row.

        Args:
            node_id (str): node id.
            visible (bool): visibility state.
            tree_widget (QtWidgets.QTreeWidget): ports tree widget.
        """
        items = self._prop_list.findItems(node_id, QtCore.Qt.MatchExactly)
        if items:
            tree_widget.setVisible(visible)
            widget = self._prop_list.cellWidget(items[0].row(), 0)
            widget.adjustSize()
            QtCompat.QHeaderView.setSectionResizeMode(
                self._prop_list.verticalHeader(),
                QtWidgets.QHeaderView.ResizeToContents
            )

    def __on_prop_close(self, node_id):
        """
        Triggered when a node property widget is requested to be removed from
        the property list widget.

        Args:
            node_id (str): node id.
        """
        items = self._prop_list.findItems(node_id, QtCore.Qt.MatchExactly)
        [self._prop_list.removeRow(i.row()) for i in items]

    def __on_limit_changed(self, value):
        """
        Sets the property list widget limit.

        Args:
            value (int): limit value.
        """
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
        properties_widget = self.get_property_editor_widget(node)
        if not properties_widget:
            return

        property_widget = properties_widget.get_widget(prop_name)

        if property_widget and prop_value != property_widget.get_value():
            self._block_signal = True
            property_widget.set_value(prop_value)
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

    def create_property_editor(self, node):
        """
        Creates a new property editor widget from the provided node.

        (re-implement for displaying custom node property editor widget.)

        Args:
            node (NodeGraphQt.NodeObject): node object.

        Returns:
            NodePropEditorWidget: property editor widget.
        """
        return NodePropEditorWidget(node=node)

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

        # remove pre-existing instance
        itm_find = self._prop_list.findItems(node.id, QtCore.Qt.MatchExactly)
        if itm_find:
            self._prop_list.removeRow(itm_find[0].row())

        self._prop_list.insertRow(0)
        rows = self._prop_list.rowCount() - 1
        
        if rows >= (self.limit()):
            # remove last row
            self._prop_list.removeRow(rows)

        prop_widget = self.create_property_editor(node=node)
        prop_widget.property_closed.connect(self.__on_prop_close)
        prop_widget.property_changed.connect(self.__on_property_widget_changed)
        port_connections = prop_widget.get_port_connection_widget()
        if port_connections:
            port_connections.input_group.clicked.connect(
                lambda v: self.__on_port_tree_visible_changed(
                    prop_widget.node_id(), v, port_connections.input_tree
                )
            )
            port_connections.output_group.clicked.connect(
                lambda v: self.__on_port_tree_visible_changed(
                    prop_widget.node_id(), v, port_connections.output_tree
                )
            )

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
            self._btn_lock.setText('UnLock')
        else:
            self._btn_lock.setText('Lock')

    def clear_bin(self):
        """
        Clear the properties bin.
        """
        self._prop_list.setRowCount(0)

    def get_property_editor_widget(self, node):
        """
        Returns the node property editor widget.

        Args:
            node (str or NodeGraphQt.NodeObject): node id or node object.

        Returns:
            NodePropEditorWidget: node property editor widget.
        """
        node_id = node if isinstance(node, str) else node.id
        itm_find = self._prop_list.findItems(node_id, QtCore.Qt.MatchExactly)
        if itm_find:
            item = itm_find[0]
            return self._prop_list.cellWidget(item.row(), 0)
