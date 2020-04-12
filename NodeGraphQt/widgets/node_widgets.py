#!/usr/bin/python
from .. import QtCore, QtWidgets

from ..constants import Z_VAL_NODE_WIDGET
from .stylesheet import *
from .file_dialog import file_dialog
from .properties import _valueEdit


class _NodeGroupBox(QtWidgets.QGroupBox):

    def __init__(self, label, parent=None):
        super(_NodeGroupBox, self).__init__(parent)
        margin = (0, 0, 0, 0)
        padding_top = '14px'
        if label == '':
            margin = (0, 2, 0, 0)
            padding_top = '2px'
        style = STYLE_QGROUPBOX.replace('$PADDING_TOP', padding_top)
        self.setTitle(label)
        self.setStyleSheet(style)

        self._layout = QtWidgets.QVBoxLayout(self)
        self._layout.setContentsMargins(*margin)
        self._layout.setSpacing(1)

    def add_node_widget(self, widget):
        self._layout.addWidget(widget)


class NodeBaseWidget(QtWidgets.QGraphicsProxyWidget):
    """
    NodeBaseWidget is the main base class for all node widgets that is
    embedded in a :class:`NodeGraphQt.BaseNode` object.
    """

    value_changed = QtCore.Signal(str, object)
    """
    Signal triggered when the ``value`` attribute has changed.

    :parameters: str, object
    :emits: property name, propety value
    """

    def __init__(self, parent=None, name='widget', label=''):
        super(NodeBaseWidget, self).__init__(parent)
        self.setZValue(Z_VAL_NODE_WIDGET)
        self._name = name
        self._label = label

    def _value_changed(self):
        self.value_changed.emit(self.name, self.value)

    def setToolTip(self, tooltip):
        tooltip = tooltip.replace('\n', '<br/>')
        tooltip = '<b>{}</b><br/>{}'.format(self.name, tooltip)
        super(NodeBaseWidget, self).setToolTip(tooltip)

    @property
    def widget(self):
        """
        Returns the embedded QWidget used in the node.

        Returns:
            QtWidgets.QWidget: nested QWidget
        """
        raise NotImplementedError

    @property
    def value(self):
        """
        Returns the widgets current value.

        Returns:
            str: current property value.
        """
        raise NotImplementedError

    @value.setter
    def value(self, text):
        """
        Sets the widgets current value.

        Args:
            text (str): new text value.
        """
        raise NotImplementedError

    @property
    def label(self):
        """
        Returns the label text displayed above the embedded node widget.

        Returns:
            str: label text.
        """
        return self._label

    @label.setter
    def label(self, label):
        """
        Sets the label text above the embedded widget.

        Args:
            label (str): new label ext.
        """
        self._label = label

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
        Returns the parent base node qgraphics item.

        Returns:
            NodeItem: parent node.
        """
        self.parentItem()

    @property
    def name(self):
        """
        Returns the parent node property name.

        Returns:
            str: property name.
        """
        return self._name

    def get_icon(self, name):
        """
        Returns the qt default icon.

        Returns:
            str: icon name.
        """
        return self.style().standardIcon(QtWidgets.QStyle.StandardPixmap(name))


class NodeComboBox(NodeBaseWidget):
    """
    NodeComboBox widget is subclassed from :class:`NodeBaseWidget`,
    this widget is displayed as a ``QComboBox`` embedded in a node.

    .. note::
        `To embed a ``QComboBox`` in a node see func:`
        :meth:`NodeGraphQt.BaseNode.add_combo_menu`
    """

    def __init__(self, parent=None, name='', label='', items=None):
        super(NodeComboBox, self).__init__(parent, name, label)
        self.setZValue(Z_VAL_NODE_WIDGET + 1)
        self._combo = QtWidgets.QComboBox()
        self._combo.setStyleSheet(STYLE_QCOMBOBOX)
        self._combo.setMinimumHeight(24)
        self._combo.currentIndexChanged.connect(self._value_changed)
        list_view = QtWidgets.QListView(self._combo)
        list_view.setStyleSheet(STYLE_QLISTVIEW)
        self._combo.setView(list_view)
        self._combo.clearFocus()
        self.add_items(items)
        group = _NodeGroupBox(label)
        group.add_node_widget(self._combo)
        self.setWidget(group)

    @property
    def type_(self):
        return 'ComboNodeWidget'

    @property
    def widget(self):
        return self._combo

    @property
    def value(self):
        """
        Returns the widget current text.

        Returns:
            str: current text.
        """
        return str(self._combo.currentText())

    @value.setter
    def value(self, text=''):
        if type(text) is list:
            self._combo.clear()
            self._combo.addItems(text)
            return
        if text != self.value:
            index = self._combo.findText(text, QtCore.Qt.MatchExactly)
            self._combo.setCurrentIndex(index)

    def add_item(self, item):
        self._combo.addItem(item)

    def add_items(self, items=None):
        if items:
            self._combo.addItems(items)

    def all_items(self):
        return [self._combo.itemText(i) for i in range(self._combo.count())]

    def sort_items(self):
        items = sorted(self.all_items())
        self._combo.clear()
        self._combo.addItems(items)

    def clear(self):
        self._combo.clear()


class NodeLineEdit(NodeBaseWidget):
    """
    NodeLineEdit widget is subclassed from :class:`NodeBaseWidget`,
    this widget is displayed as a ``QLineEdit`` embedded in a node.

    .. note::
        `To embed a ``QLineEdit`` in a node see func:`
        :meth:`NodeGraphQt.BaseNode.add_text_input`
    """

    def __init__(self, parent=None, name='', label='', text=''):
        super(NodeLineEdit, self).__init__(parent, name, label)
        self._ledit = QtWidgets.QLineEdit()
        self._ledit.setStyleSheet(STYLE_QLINEEDIT)
        self._ledit.setAlignment(QtCore.Qt.AlignCenter)
        self._ledit.editingFinished.connect(self._value_changed)
        self._ledit.clearFocus()
        group = _NodeGroupBox(label)
        group.add_node_widget(self._ledit)
        group.setMaximumWidth(120)
        self.setWidget(group)
        self.text = text

    @property
    def type_(self):
        return 'LineEditNodeWidget'

    @property
    def widget(self):
        return self._ledit

    @property
    def value(self):
        """
        Returns the widgets current text.

        Returns:
            str: current text.
        """
        return str(self._ledit.text())

    @value.setter
    def value(self, text=''):
        if text != self.value:
            self._ledit.setText(text)
            self._value_changed()


class NodeFloatEdit(NodeBaseWidget):
    """
    NodeFloatEdit widget is subclassed from :class:`NodeBaseWidget`,
    this widget is displayed as a ``QLineEdit`` embedded in a node.

    .. note::
        `To embed a ``QLineEdit`` in a node see func:`
        :meth:`NodeGraphQt.BaseNode.add_float_input`
    """

    def __init__(self, parent=None, name='', label='', value = 0.0):
        super(NodeFloatEdit, self).__init__(parent, name, label)
        self._ledit = _valueEdit()
        self._ledit.setStyleSheet(STYLE_QLINEEDIT)
        self._ledit.setAlignment(QtCore.Qt.AlignCenter)
        self._ledit.valueChanged.connect(self._value_changed)
        self._ledit.clearFocus()
        self._ledit.setValue(value)
        group = _NodeGroupBox(label)
        group.add_node_widget(self._ledit)
        group.setMaximumWidth(120)
        self.setWidget(group)

    @property
    def type_(self):
        return 'FloatEditNodeWidget'

    @property
    def widget(self):
        return self._ledit

    @property
    def value(self):
        """
        Returns the widgets current value.

        Returns:
            float: current value.
        """
        return self._ledit.value()

    @value.setter
    def value(self, value):
        if value != self.value:
            self._ledit.setValue(value)
            self._value_changed()


class NodeIntEdit(NodeFloatEdit):
    """
    NodeIntEdit widget is subclassed from :class:`NodeFloatEdit`,
    this widget is displayed as a ``QLineEdit`` embedded in a node.

    .. note::
        `To embed a ``QLineEdit`` in a node see func:`
        :meth:`NodeGraphQt.BaseNode.add_int_input`
    """

    def __init__(self, parent=None, name='', label='', value=0):
        super(NodeIntEdit, self).__init__(parent, name, label)
        self._ledit.set_data_type(int)
        self._ledit.setValue(value)


class NodeCheckBox(NodeBaseWidget):
    """
    NodeCheckBox widget is subclassed from :class:`NodeBaseWidget`,
    this widget is displayed as a ``QCheckBox`` embedded in a node.

    .. note::
        `To embed a ``QCheckBox`` in a node see func:`
        :meth:`NodeGraphQt.BaseNode.add_checkbox`
    """

    def __init__(self, parent=None, name='', label='', text='', state=False):
        super(NodeCheckBox, self).__init__(parent, name, label)
        self._cbox = QtWidgets.QCheckBox(text)
        self._cbox.setChecked(state)
        self._cbox.setMinimumWidth(80)

        self._cbox.setStyleSheet(STYLE_QCHECKBOX)

        font = self._cbox.font()
        font.setPointSize(11)
        self._cbox.setFont(font)
        self._cbox.stateChanged.connect(self._value_changed)
        group = _NodeGroupBox(label)
        group.add_node_widget(self._cbox)
        self.setWidget(group)
        self.text = text
        self.state = state

    @property
    def type_(self):
        return 'CheckboxNodeWidget'

    @property
    def widget(self):
        return self._cbox

    @property
    def value(self):
        """
        Returns the widget checked state.

        Returns:
            bool: checked state.
        """
        return self._cbox.isChecked()

    @value.setter
    def value(self, state=False):
        if state != self.value:
            self._cbox.setChecked(state)


class NodeFilePath(NodeLineEdit):
    """
    NodeFilePath widget is subclassed from :class:`NodeLineEdit`,
    this widget is displayed as a ``QLineEdit`` embedded in a node.

    .. note::
        `To embed a ``QLineEdit`` in a node see func:`
        :meth:`NodeGraphQt.BaseNode.add_float_input`
    """

    def __init__(self, parent=None, name='', label='', text='', ext="*"):
        super(NodeLineEdit, self).__init__(parent, name, label)
        self._ledit = QtWidgets.QLineEdit()
        self._ledit.setStyleSheet(STYLE_QLINEEDIT)
        self._ledit.setAlignment(QtCore.Qt.AlignCenter)
        self._ledit.editingFinished.connect(self._value_changed)
        self._ledit.clearFocus()

        _button = QtWidgets.QPushButton()
        _button.setStyleSheet(STYLE_QPUSHBUTTON)
        _button.setIcon(self.get_icon(21))

        widget = QtWidgets.QWidget()
        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(self._ledit)
        hbox.addWidget(_button)
        widget.setLayout(hbox)
        widget.setStyleSheet(STYLE_QWIDGET)

        group = _NodeGroupBox(label)
        group.add_node_widget(widget)
        self.text = text

        _button.clicked.connect(self._on_select_file)
        self.setWidget(group)
        self._ext = ext

    def _on_select_file(self):
        file_path = file_dialog.getOpenFileName(ext_filter=self._ext)
        file = file_path[0] or None
        if file:
            self.value = file
