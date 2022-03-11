#!/usr/bin/python
from .dialogs import FileDialog
from .properties import _ValueEdit
from .stylesheet import *

from Qt import QtCore, QtWidgets
from ..constants import Z_VAL_NODE_WIDGET
from ..errors import NodeWidgetError


class _NodeGroupBox(QtWidgets.QGroupBox):

    def __init__(self, label, parent=None):
        super(_NodeGroupBox, self).__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(1)
        self.setTitle(label)

    def setTitle(self, text):
        margin = (0, 0, 0, 0)
        padding_top = '14px'
        if text == '':
            margin = (0, 2, 0, 0)
            padding_top = '2px'
        style = STYLE_QGROUPBOX.replace('$PADDING_TOP', padding_top)
        self.layout().setContentsMargins(*margin)
        self.setStyleSheet(style)
        super(_NodeGroupBox, self).setTitle(text)

    def add_node_widget(self, widget):
        self.layout().addWidget(widget)

    def get_node_widget(self):
        return self.layout().itemAt(0).widget()


class NodeBaseWidget(QtWidgets.QGraphicsProxyWidget):
    """
    This is the main wrapper class that allows a ``QtWidgets.QWidget`` to be
    added in a :class:`NodeGraphQt.BaseNode` object.

    Args:
        parent (NodeGraphQt.BaseNode.view): parent node view.
        name (str): property name for the parent node.
        label (str): label text above the embedded widget.
    """

    value_changed = QtCore.Signal(str, object)
    """
    Signal triggered when the ``value`` attribute has changed.
    
    (This is connected to the :meth: `BaseNode.set_property` function when the 
    widget is added into the node.)

    :parameters: str, object
    :emits: property name, propety value
    """

    def __init__(self, parent=None, name=None, label=''):
        super(NodeBaseWidget, self).__init__(parent)
        self.setZValue(Z_VAL_NODE_WIDGET)
        self._name = name
        self._label = label
        self._node = None

    def setToolTip(self, tooltip):
        tooltip = tooltip.replace('\n', '<br/>')
        tooltip = '<b>{}</b><br/>{}'.format(self.name, tooltip)
        super(NodeBaseWidget, self).setToolTip(tooltip)

    def on_value_changed(self, *args, **kwargs):
        """
        This is the slot function that
        Emits the widgets current :meth:`NodeBaseWidget.value` with the
        :attr:`NodeBaseWidget.value_changed` signal.

        Args:
            args: not used.
            kwargs: not used.

        Emits:
            str, object: <node_property_name>, <node_property_value>
        """
        self.value_changed.emit(self.get_name(), self.get_value())

    @property
    def type_(self):
        """
        Returns the node widget type.

        Returns:
            str: widget type.
        """
        return str(self.__class__.__name__)

    @property
    def node(self):
        """
        Returns the node object this widget is embedded in.
        (This will return ``None`` if the widget has not been added to
        the node yet.)

        Returns:
            NodeGraphQt.BaseNode: parent node.
        """
        return self._node

    def get_icon(self, name):
        """
        Returns the default icon from the Qt framework.

        Returns:
            str: icon name.
        """
        return self.style().standardIcon(QtWidgets.QStyle.StandardPixmap(name))

    def get_name(self):
        """
        Returns the parent node property name.

        Returns:
            str: property name.
        """
        return self._name

    def set_name(self, name):
        """
        Set the property name for the parent node.

        Important:
            The property name must be set before the widget is added to
            the node.

        Args:
            name (str): property name.
        """
        if not name:
            return
        if self.node:
            raise NodeWidgetError(
                'Can\'t set property name widget already added to a Node'
            )
        self._name = name

    def get_value(self):
        """
        Returns the widgets current value.

        You must re-implement this property to if you're using a custom widget.

        Returns:
            str: current property value.
        """
        raise NotImplementedError

    def set_value(self, text):
        """
        Sets the widgets current value.

        You must re-implement this property to if you're using a custom widget.

        Args:
            text (str): new text value.
        """
        raise NotImplementedError

    def get_custom_widget(self):
        """
        Returns the embedded QWidget used in the node.

        Returns:
            QtWidgets.QWidget: nested QWidget
        """
        widget = self.widget()
        return widget.get_node_widget()

    def set_custom_widget(self, widget):
        """
        Set the custom QWidget used in the node.

        Args:
            widget (QtWidgets.QWidget): custom.
        """
        if self.widget():
            raise NodeWidgetError('Custom node widget already set.')
        group = _NodeGroupBox(self._label)
        group.add_node_widget(widget)
        self.setWidget(group)

    def get_label(self):
        """
        Returns the label text displayed above the embedded node widget.

        Returns:
            str: label text.
        """
        return self._label

    def set_label(self, label=''):
        """
        Sets the label text above the embedded widget.

        Args:
            label (str): new label ext.
        """
        if self.widget():
            self.widget().setTitle(label)
        self._label = label


class NodeComboBox(NodeBaseWidget):
    """
    Displays as a ``QComboBox`` in a node.

    **Inherited from:** :class:`NodeBaseWidget`

    .. note::
        `To embed a` ``QComboBox`` `in a node see func:`
        :meth:`NodeGraphQt.BaseNode.add_combo_menu`
    """

    def __init__(self, parent=None, name='', label='', items=None):
        super(NodeComboBox, self).__init__(parent, name, label)
        self.setZValue(Z_VAL_NODE_WIDGET + 1)
        combo = QtWidgets.QComboBox()
        combo.setStyleSheet(STYLE_QCOMBOBOX)
        combo.setMinimumHeight(24)
        list_view = QtWidgets.QListView(combo)
        list_view.setStyleSheet(STYLE_QLISTVIEW)
        combo.setView(list_view)
        combo.addItems(items or [])
        combo.currentIndexChanged.connect(self.on_value_changed)
        combo.clearFocus()
        self.set_custom_widget(combo)

    @property
    def type_(self):
        return 'ComboNodeWidget'

    def get_value(self):
        """
        Returns the widget current text.

        Returns:
            str: current text.
        """
        combo_widget = self.get_custom_widget()
        return str(combo_widget.currentText())

    def set_value(self, text=''):
        combo_widget = self.get_custom_widget()
        if type(text) is list:
            combo_widget.clear()
            combo_widget.addItems(text)
            return
        if text != self.get_value():
            index = combo_widget.findText(text, QtCore.Qt.MatchExactly)
            combo_widget.setCurrentIndex(index)

    def add_item(self, item):
        combo_widget = self.get_custom_widget()
        combo_widget.addItem(item)

    def add_items(self, items=None):
        if items:
            combo_widget = self.get_custom_widget()
            combo_widget.addItems(items)

    def all_items(self):
        combo_widget = self.get_custom_widget()
        return [combo_widget.itemText(i) for i in range(combo_widget.count())]

    def sort_items(self, reversed=False):
        items = sorted(self.all_items(), reverse=reversed)
        combo_widget = self.get_custom_widget()
        combo_widget.clear()
        combo_widget.addItems(items)

    def clear(self):
        combo_widget = self.get_custom_widget()
        combo_widget.clear()


class NodeLineEdit(NodeBaseWidget):
    """
    Displays as a ``QLineEdit`` in a node.

    **Inherited from:** :class:`NodeBaseWidget`

    .. note::
        `To embed a` ``QLineEdit`` `in a node see func:`
        :meth:`NodeGraphQt.BaseNode.add_text_input`
    """

    def __init__(self, parent=None, name='', label='', text=''):
        super(NodeLineEdit, self).__init__(parent, name, label)
        ledit = QtWidgets.QLineEdit()
        ledit.setText(text)
        ledit.setStyleSheet(STYLE_QLINEEDIT)
        ledit.setAlignment(QtCore.Qt.AlignCenter)
        ledit.editingFinished.connect(self.on_value_changed)
        ledit.clearFocus()
        self.set_custom_widget(ledit)
        self.widget().setMaximumWidth(140)

    @property
    def type_(self):
        return 'LineEditNodeWidget'

    def get_value(self):
        """
        Returns the widgets current text.

        Returns:
            str: current text.
        """
        return str(self.get_custom_widget().text())

    def set_value(self, text=''):
        if text != self.get_value():
            self.get_custom_widget().setText(text)
            self.on_value_changed()


class NodeFloatEdit(NodeBaseWidget):
    """
    Displays as a ``QLineEdit`` in a node.

    **Inherited from:** :class:`NodeBaseWidget`

    .. note::
        `To embed a` ``QLineEdit`` `in a node see func:`
        :meth:`NodeGraphQt.BaseNode.add_float_input`
    """

    def __init__(self, parent=None, name='', label='', value=0.0):
        super(NodeFloatEdit, self).__init__(parent, name, label)
        val_ledit = _ValueEdit()
        val_ledit.setStyleSheet(STYLE_QLINEEDIT)
        val_ledit.setAlignment(QtCore.Qt.AlignCenter)
        val_ledit.valueChanged.connect(self.on_value_changed)
        val_ledit.setValue(value)
        val_ledit.clearFocus()
        self.set_custom_widget(val_ledit)
        self.widget().setMaximumWidth(140)

    @property
    def type_(self):
        return 'FloatEditNodeWidget'

    def get_value(self):
        """
        Returns the widgets current value.

        Returns:
            float: current value.
        """
        return self.get_custom_widget().value()

    def set_value(self, value):
        if value != self.get_value():
            self.get_custom_widget().setValue(value)
            self.on_value_changed()


class NodeIntEdit(NodeFloatEdit):
    """
    Displays as a ``QLineEdit`` in a node.

    **Inherited from:** :class:`NodeBaseWidget`

    .. note::
        `To embed a` ``QLineEdit`` `in a node see func:`
        :meth:`NodeGraphQt.BaseNode.add_int_input`
    """

    def __init__(self, parent=None, name='', label='', value=0):
        super(NodeIntEdit, self).__init__(parent, name, label)
        self.get_custom_widget().set_data_type(int)
        self.get_custom_widget().setValue(value)

    @property
    def type_(self):
        return 'IntEditNodeWidget'


class NodeCheckBox(NodeBaseWidget):
    """
    Displays as a ``QCheckBox`` in a node.

    **Inherited from:** :class:`NodeBaseWidget`

    .. note::
        `To embed a` ``QCheckBox`` `in a node see func:`
        :meth:`NodeGraphQt.BaseNode.add_checkbox`
    """

    def __init__(self, parent=None, name='', label='', text='', state=False):
        super(NodeCheckBox, self).__init__(parent, name, label)
        _cbox = QtWidgets.QCheckBox(text)
        _cbox.setChecked(state)
        _cbox.setMinimumWidth(80)
        _cbox.setStyleSheet(STYLE_QCHECKBOX)

        font = _cbox.font()
        font.setPointSize(11)
        _cbox.setFont(font)
        _cbox.stateChanged.connect(self.on_value_changed)
        self.set_custom_widget(_cbox)
        self.widget().setMaximumWidth(140)

    @property
    def type_(self):
        return 'CheckboxNodeWidget'

    def get_value(self):
        """
        Returns the widget checked state.

        Returns:
            bool: checked state.
        """
        return self.get_custom_widget().isChecked()

    def set_value(self, state=False):
        if state != self.get_value():
            self.get_custom_widget().setChecked(state)


class NodeFilePath(NodeLineEdit):
    """
    Displays as a ``QLineEdit`` in a node.

    **Inherited from:** :class:`NodeBaseWidget`

    .. note::
        To embed a ``QLineEdit`` in a node see:
        :meth:`NodeGraphQt.BaseNode.add_file_input`
    """

    def __init__(self, parent=None, name='', label='', text='', ext='*'):
        super(NodeLineEdit, self).__init__(parent, name, label)
        _ledit = QtWidgets.QLineEdit()
        _ledit.setStyleSheet(STYLE_QLINEEDIT)
        _ledit.setAlignment(QtCore.Qt.AlignCenter)
        _ledit.editingFinished.connect(self.on_value_changed)
        _ledit.clearFocus()

        _button = QtWidgets.QPushButton()
        _button.setStyleSheet(STYLE_QPUSHBUTTON)
        _button.setIcon(self.get_icon(21))
        _button.clicked.connect(self._on_select_file)

        widget = QtWidgets.QWidget()
        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(_ledit)
        hbox.addWidget(_button)
        widget.setLayout(hbox)
        widget.setStyleSheet(STYLE_QWIDGET)

        self._ext = ext
        self.set_custom_widget(widget)
        self.widget().setMaximumWidth(140)

    def _on_select_file(self):
        file_path = FileDialog.getOpenFileName(ext_filter=self._ext)
        file = file_path[0] or None
        if file:
            self.value = file
