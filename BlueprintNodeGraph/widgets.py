#!/usr/bin/python

from PySide import QtGui, QtCore

from .constants import Z_VAL_KNOB

_QGROUPBOX_STYLE = '''
QGroupBox {
    background-color: rgba(0, 0, 0, 0);
    border-radius: 2px;
    margin-top: 1ex;
    padding: 5px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top center;
    color: rgba(255, 255, 255, 80);
}
'''


class _NodeGroubBox(QtGui.QGroupBox):

    def __init__(self, title, parent=None):
        super(_NodeGroubBox, self).__init__(parent)
        self.setStyleSheet(_QGROUPBOX_STYLE)
        self.setTitle(title)
        self._layout = QtGui.QVBoxLayout(self)
        self._layout.setContentsMargins(0, 5, 0, 0)

    def add_node_widget(self, widget):
        self._layout.addWidget(widget)


class _BaseNodeWidget(QtGui.QGraphicsProxyWidget):
    """
    Custom base node widget.
    """

    def __init__(self, parent=None, name='widget', label=''):
        super(_BaseNodeWidget, self).__init__(parent)
        self.setZValue(Z_VAL_KNOB)
        self.name = name
        self.label = label

    @property
    def type(self):
        return str(self.__class__.__name__)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name=''):
        self._name = name.strip().replace(' ', '_')

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, label):
        self._label = label


class ComboNodeWidget(_BaseNodeWidget):
    """
    Custom ComboBox node widget.
    """

    def __init__(self, parent=None, name='', label=''):
        super(ComboNodeWidget, self).__init__(parent, name, label)
        self._combo = QtGui.QComboBox()
        group = _NodeGroubBox(self.label)
        group.add_node_widget(self._combo)
        self.setWidget(group)

    @property
    def item(self):
        return str(self.widget().currentItemText())

    @item.setter
    def item(self, item):
        index = self._combo.findText(QtCore.Qt.MatchExactly)
        self._combo.setCurrentIndex(index)

    def add_item(self, item):
        self._combo.addItem(item)

    def add_items(self, items):
        self._combo.addItems(items)

    def all_items(self):
        return [self._combo.itemText(i) for i in range(self._combo.count)]

    def clear(self):
        self._combo.clear()

    def sort(self):
        items = sorted(self.all_items())
        self._combo.clear()
        self._combo.addItems(items)


class LineEditNodeWidget(_BaseNodeWidget):
    """
    Custom LineEdit node widget.
    """

    def __init__(self, parent=None, name='', label=''):
        super(LineEditNodeWidget, self).__init__(parent, name, label)
        self._ledit = QtGui.QLineEdit()
        group = _NodeGroubBox(self.label)
        group.add_node_widget(self._ledit)
        self.setWidget(group)

    @property
    def text(self):
        return str(self._ledit.text())

    @text.setter
    def text(self, text):
        self._ledit.setText(text)

    def set_completer(self, completer):
        self._ledit.setCompleter(completer)
