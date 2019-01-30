#!/usr/bin/python
from collections import defaultdict

from PySide2 import QtWidgets, QtCore, QtGui

from NodeGraphQt.constants import (NODE_PROP_QLABEL,
                                   NODE_PROP_QLINEEDIT,
                                   NODE_PROP_QCOMBO,
                                   NODE_PROP_QCHECKBOX,
                                   NODE_PROP_QSPINBOX,
                                   NODE_PROP_COLORPICKER,
                                   NODE_PROP_SLIDER)


class BaseProperty(QtWidgets.QWidget):

    value_changed = QtCore.Signal(str, object)

    def set_value(self, value):
        raise NotImplementedError

    def get_value(self):
        raise NotImplementedError


class _ColorSolid(QtWidgets.QWidget):

    def __init__(self, parent=None, color=None):
        super(_ColorSolid, self).__init__(parent)
        self.setMinimumSize(15, 15)
        self.setMaximumSize(15, 15)
        self.color = color or (0, 0, 0)

    def paintEvent(self, event):
        size = self.geometry()
        rect = QtCore.QRect(1, 1, size.width() - 2, size.height() - 2)
        painter = QtGui.QPainter(self)
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtGui.QColor(*self._color))
        painter.drawRoundedRect(rect, 4, 4)

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, color):
        self._color = color
        hex = '#{0:02x}{1:02x}{2:02x}'.format(*self._color)
        self.setToolTip('rgb: {}\nhex: {}'.format(self._color[0:3], hex))
        self.update()


class PropColorPicker(BaseProperty):

    def __init__(self, parent=None):
        super(PropColorPicker, self).__init__(parent)
        self._solid = _ColorSolid(self)
        self._solid.setMaximumHeight(15)
        self._label = QtWidgets.QLabel()
        self._update_label()

        button = QtWidgets.QPushButton('select color')
        button.clicked.connect(self._on_select_color)
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 8, 0)
        layout.setSpacing(4)
        layout.addWidget(self._solid, 0, QtCore.Qt.AlignCenter)
        layout.addWidget(self._label, 0, QtCore.Qt.AlignCenter)
        layout.addWidget(button, 1, QtCore.Qt.AlignLeft)

    def _on_select_color(self):
        color = QtWidgets.QColorDialog.getColor()
        if color.isValid():
            self.set_value(color.getRgb())

    def _update_label(self):
        self._label.setStyleSheet(
            'QLabel {{color: rgba({}, {}, {}, 255);}}'
            .format(*self._solid.color))
        self._label.setText(self.hex_color())
        self._label.setAlignment(QtCore.Qt.AlignCenter)
        self._label.setMinimumWidth(60)

    def hex_color(self):
        return '#{0:02x}{1:02x}{2:02x}'.format(*self._solid.color)

    def get_value(self):
        return self._solid.color

    def set_value(self, value):
        if value != self.get_value():
            self._solid.color = value
            self._update_label()
            self.value_changed.emit(self.toolTip(), value)


class PropSlider(BaseProperty):

    def __init__(self, parent=None):
        super(PropSlider, self).__init__(parent)
        self._block = False
        self._slider = QtWidgets.QSlider()
        self._spnbox = QtWidgets.QSpinBox()
        self._init()

    def _init(self):
        self._slider.setOrientation(QtCore.Qt.Horizontal)
        self._slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self._slider.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Preferred)
        self._spnbox.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(self._spnbox)
        layout.addWidget(self._slider)
        self._spnbox.valueChanged.connect(self._on_spnbox_changed)
        self._slider.valueChanged.connect(self._on_slider_changed)
        # store the original press event.
        self._slider_press_event = self._slider.mousePressEvent
        self._slider.mousePressEvent = self.sliderMousePressEvent
        self._slider.mouseReleaseEvent = self.sliderMouseReleaseEvent

    def sliderMousePressEvent(self, event):
        self._block = True
        self._slider_press_event(event)

    def sliderMouseReleaseEvent(self, event):
        self.value_changed.emit(self.toolTip(), self.get_value())
        self._block = False

    def _on_slider_changed(self, value):
        self._spnbox.setValue(value)

    def _on_spnbox_changed(self, value):
        if value != self._slider.value():
            self._slider.setValue(value)
            if not self._block:
                self.value_changed.emit(self.toolTip(), self.get_value())

    def get_value(self):
        return self._spnbox.value()

    def set_value(self, value):
        if value != self.get_value():
            self._block = True
            self._spnbox.setValue(value)
            self.value_changed.emit(self.toolTip(), value)
            self._block = False

    def set_min(self, value=0):
        self._spnbox.setMinimum(value)
        self._slider.setMinimum(value)

    def set_max(self, value=0):
        self._spnbox.setMaximum(value)
        self._slider.setMaximum(value)


class PropLabel(QtWidgets.QLabel):

    value_changed = QtCore.Signal(str, object)

    def get_value(self):
        return self.text()

    def set_value(self, value):
        if value != self.get_value():
            self.setText(value)
            self.value_changed.emit(self.toolTip(), value)


class PropLineEdit(QtWidgets.QLineEdit):

    value_changed = QtCore.Signal(str, object)

    def __init__(self, parent=None):
        super(PropLineEdit, self).__init__(parent)
        self.returnPressed.connect(self._on_return_pressed)

    def _on_return_pressed(self):
        self.value_changed.emit(self.toolTip(), self.get_value())

    def get_value(self):
        return self.text()

    def set_value(self, value):
        if value != self.get_value():
            self.setText(value)
            self.value_changed.emit(self.toolTip(), value)


class PropComboBox(QtWidgets.QComboBox):

    value_changed = QtCore.Signal(str, object)

    def __init__(self, parent=None):
        super(PropComboBox, self).__init__(parent)
        self.currentIndexChanged.connect(self._on_index_changed)

    def _on_index_changed(self):
        self.value_changed.emit(self.toolTip(), self.get_value())

    def items(self):
        return [self.itemText(i) for i in range(self.count())]

    def set_items(self, items):
        self.clear()
        self.addItems(items)

    def get_value(self):
        return self.currentText()

    def set_value(self, value):
        if value != self.get_value():
            idx = self.findText(value, QtCore.Qt.MatchExactly)
            if idx < 0:
                self.setCurrentIndex(idx)
                self.value_changed.emit(self.toolTip(), value)


class PropCheckBox(QtWidgets.QCheckBox):

    value_changed = QtCore.Signal(str, object)

    def __init__(self, parent=None):
        super(PropCheckBox, self).__init__(parent)
        self.clicked.connect(self._on_clicked)

    def _on_clicked(self):
        self.value_changed.emit(self.toolTip(), self.get_value())

    def get_value(self):
        return self.isChecked()

    def set_value(self, value):
        if value != self.get_value():
            self.setChecked(value)
            self.value_changed.emit(self.toolTip(), value)


class PropSpinBox(QtWidgets.QSpinBox):

    value_changed = QtCore.Signal(str, object)

    def __init__(self, parent=None):
        super(PropSpinBox, self).__init__(parent)
        self.setButtonSymbols(self.NoButtons)
        self.valueChanged.connect(self._on_value_change)

    def _on_value_change(self, value):
        self.value_changed.emit(self.toolTip(), value)

    def get_value(self):
        return self.value()

    def set_value(self, value):
        if value != self.get_value():
            self.setValue(value)


WIDGET_MAP = {
    NODE_PROP_QLABEL:       PropLabel,
    NODE_PROP_QLINEEDIT:    PropLineEdit,
    NODE_PROP_QCOMBO:       PropComboBox,
    NODE_PROP_QCHECKBOX:    PropCheckBox,
    NODE_PROP_QSPINBOX:     PropSpinBox,
    NODE_PROP_COLORPICKER:  PropColorPicker,
    NODE_PROP_SLIDER:       PropSlider,
}


# main property widgets.


class PropWindow(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(PropWindow, self).__init__(parent)
        self.__layout = QtWidgets.QGridLayout()
        self.__layout.setColumnStretch(1, 1)
        self.__layout.setSpacing(6)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setAlignment(QtCore.Qt.AlignTop)
        layout.addLayout(self.__layout)

    def add_widget(self, name, widget, value):
        """
        Args:
            name (str):
            widget (BaseProperty):
            value (object):
        """
        widget.setToolTip(name)
        widget.set_value(value)
        label = QtWidgets.QLabel(name)
        label.setAlignment(QtCore.Qt.AlignCenter)
        row = self.__layout.rowCount()
        if row > 0:
            row += 1
        self.__layout.addWidget(label, row, 0,
                                QtCore.Qt.AlignCenter | QtCore.Qt.AlignRight)
        self.__layout.addWidget(widget, row, 1)

    def get_widget(self, name):
        """
        Args:
            name (str): property name.

        Returns:
            QtWidgets.QWidget: property widget.
        """
        for row in range(self.__layout.rowCount()):
            widget = self.__layout.itemAtPosition(row, 1).widget()
            if name == widget.toolTip():
                return widget


class NodePropWidget(QtWidgets.QFrame):
    """
    Node properties widget for display a Node object.

    Args:
        parent:
        node (NodeGraphQt.Node): node.
    """

    #: signal (node_id, prop_name, prop_value)
    property_changed = QtCore.Signal(str, str, object)
    property_closed = QtCore.Signal(str)

    def __init__(self, parent=None, node=None):
        super(NodePropWidget, self).__init__(parent)
        self.resize(350, 200)
        self.setFrameStyle(self.StyledPanel)
        self.__node_id = node.id
        self.__tab_windows = {}
        self.__tab = QtWidgets.QTabWidget()

        close_btn = QtWidgets.QPushButton('X')
        close_btn.setToolTip('close window')
        close_btn.clicked.connect(self._on_close)

        name_wgt = PropLineEdit()
        name_wgt.set_value(node.name())
        name_wgt.value_changed.connect(self._on_property_changed)

        name_layout = QtWidgets.QHBoxLayout()
        name_layout.setContentsMargins(0, 0, 0, 0)
        name_layout.addWidget(QtWidgets.QLabel('name'))
        name_layout.addWidget(name_wgt)
        name_layout.addWidget(close_btn)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addLayout(name_layout)
        layout.addWidget(self.__tab)
        self._read_node(node)

    def _on_close(self):
        self.property_closed.emit(self.__node_id)

    def _on_property_changed(self, name, value):
        self.property_changed.emit(self.__node_id, name, value)

    def _read_node(self, node):
        """
        populate widget from a node.

        Args:
            node (NodeGraphQt.Node): node class.
        """
        model = node.model
        graph_model = node.graph.model

        common_props = graph_model.get_node_common_properties(node.type)

        # sort tabs and properties.
        tab_mapping = defaultdict(list)
        for prop_name, prop_val in model.custom_properties.items():
            tab_name = model.get_tab_name(prop_name)
            tab_mapping[tab_name].append((prop_name, prop_val))

        # add tabs.
        for tab in sorted(tab_mapping.keys()):
            if tab != 'Node':
                self.add_tab(tab)

        # populate tab properties.
        for tab in sorted(tab_mapping.keys()):
            prop_window = self.__tab_windows[tab]
            for prop_name, value in tab_mapping[tab]:
                wid_type = model.get_widget_type(prop_name)
                WidClass = WIDGET_MAP.get(wid_type)

                widget = WidClass()
                if prop_name in common_props.keys():
                    if 'items' in common_props[prop_name].keys():
                        widget.set_items(common_props[prop_name]['items'])
                    if 'range' in common_props[prop_name].keys():
                        prop_range = common_props[prop_name]['range']
                        widget.set_min(prop_range[0])
                        widget.set_max(prop_range[1])

                prop_window.add_widget(prop_name, widget, value)
                widget.value_changed.connect(self._on_property_changed)

        # add "Node" tab properties.
        self.add_tab('Node')
        default_props = ['type', 'color', 'text_color', 'disabled', 'id']
        prop_window = self.__tab_windows['Node']
        for prop_name in default_props:
            wid_type = model.get_widget_type(prop_name)
            WidClass = WIDGET_MAP.get(wid_type)

            widget = WidClass()
            prop_window.add_widget(prop_name,
                                   widget,
                                   model.get_property(prop_name))
            widget.value_changed.connect(self._on_property_changed)

    def node_id(self):
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
            PropWindow: tab child widget.
        """
        if name in self.__tab_windows.keys():
            raise AssertionError('Tab name {} already taken!'.format(name))
        self.__tab_windows[name] = PropWindow(self)
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
        for tab_name, prop_win in self.__tab_windows.items():
            widget = prop_win.get_widget(name)
            if widget:
                return widget


class PropContainerWidget(QtWidgets.QScrollArea):
    """
    Node property bin widget for displaying nodes.
    """

    #: signal (node_id, prop_name, prop_value)
    property_changed = QtCore.Signal(str, str, object)

    def __init__(self, parent=None):
        super(PropContainerWidget, self).__init__(parent)
        self.setWidgetResizable(True)
        self.setMinimumSize(380, 300)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        container = QtWidgets.QWidget()
        self.setWidget(container)
        self.__layout = QtWidgets.QVBoxLayout(container)
        self.__layout.setSpacing(2)
        self.__layout.setContentsMargins(4, 6, 4, 6)
        self.__node_wgts = {}

    def add_node(self, node):
        """
        Add a node to the properties bin.

        Args:
            node (NodeGraphQt.Node): node object.
        """
        if node.id in self.__node_wgts.keys():
            self.remove_node(node.id)
        node_wgt = NodePropWidget(self, node)
        node_wgt.property_closed.connect(self.remove_node)
        node_wgt.property_changed.connect(self.property_changed.emit)
        self.__node_wgts[node.id] = node_wgt
        self.__layout.insertWidget(0, node_wgt)

    def remove_node(self, node_id):
        widget = self.__node_wgts.pop(node_id)
        widget.deleteLater()

    def node_ids(self):
        return list(self.__node_wgts.keys())

    def property_widget(self, node_id):
        return self.__node_wgts.get(node_id)

    def property_widgets(self):
        return self.__node_wgts

    def clear(self):
        for widget in self.__node_wgts.values():
            widget.deleteLater()
        self.__node_wgts = {}


class PropBinWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(PropBinWidget, self).__init__(parent)

        self.__contaner = PropContainerWidget()

        top_layout = QtWidgets.QHBoxLayout()
        top_layout.addWidget(QtWidgets.QLabel('Properties'))

        layout = QtWidgets.QVBoxLayout(self)
        layout.addLayout(top_layout)
        layout.addWidget(self.__contaner)

    @property
    def container(self):
        return self.__contaner

    def scroll_to_top(self):
        self.__container.verticalScrollBar().setValue(0)

    def add_node(self, node):
        self.__contaner.add_node(node)

    def remove_node(self, node_id):
        self.__contaner.remove_node(node_id)


if __name__ == '__main__':
    import sys
    from NodeGraphQt import Node, NodeGraph


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

    test_node = graph.create_node('nodeGraphQt.nodes.TestNode')
    test_node2 = graph.create_node('nodeGraphQt.nodes.TestNode')

    prop_bin = PropBinWidget()
    prop_bin.container.property_changed.connect(prop_changed)

    prop_bin.container.add_node(test_node)
    prop_bin.container.add_node(test_node2)

    prop_bin.show()

    app.exec_()
