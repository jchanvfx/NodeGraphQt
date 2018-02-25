#!/usr/bin/python
import re
from PySide import QtGui, QtCore

from .constants import Z_VAL_KNOB, ICON_DOWN_ARROW_ICON

# we reformat the icon file path on windows os.
regex = re.compile('(\w:)')
match = regex.match(ICON_DOWN_ARROW_ICON)
if match:
    match_str = match.group(1)
    ICON_DOWN_ARROW_ICON = ICON_DOWN_ARROW_ICON[len(match_str):]
    ICON_DOWN_ARROW_ICON = ICON_DOWN_ARROW_ICON.replace('\\', '/')

_STYLE_QGROUPBOX = '''
QGroupBox {
    background-color: rgba(0, 0, 0, 0);
    border: 0px solid rgba(0, 0, 0, 0);
    margin-top: 1px;
    padding: 2px;
    padding-top: 10px;
    font-size: 11px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top center;
    color: rgba(255, 255, 255, 85);
}
'''

_STYLE_QLINEEDIT = '''
QLineEdit {
    border: 1px solid rgba(255, 255, 255, 50);
    border-radius: 0px;
    color: rgba(255, 255, 255, 150);
    background: rgba(0, 0, 0, 80);
    selection-background-color: rgba(255, 198, 10, 155);
}
'''

_STYLE_QCOMBOBOX = '''
QComboBox {
    border: 1px solid rgba(255, 255, 255, 50);
    border-radius: 0px;
    margin-left: 2px;
    margin-right: 2px;
    margin-top: 1px;
    margin-bottom: 1px;
    padding-left: 4px;
    padding-right: 4px;
}
QComboBox:hover {
    border: 1px solid rgba(255, 255, 255, 80);
}
QComboBox:editable {
    color: rgba(255, 255, 255, 150);
    background: rgba(10, 10, 10, 80);
}
QComboBox:!editable,
QComboBox::drop-down:editable {
    color: rgba(255, 255, 255, 150);
    background: rgba(80, 80, 80, 80);
}
/* QComboBox gets the "on" state when the popup is open */
QComboBox:!editable:on,
QComboBox::drop-down:editable:on {
    background: rgba(150, 150, 150, 150);
}
QComboBox::drop-down {
    background: rgba(80, 80, 80, 80);
    border-left: 1px solid rgba(80, 80, 80, 255);
    width: 20px;
}
QComboBox::down-arrow {
    image: url($ICON_DOWN_ARROW);
}
QComboBox::down-arrow:on {
    /* shift the arrow when popup is open */
    top: 1px;
    left: 1px;
}'''.replace('$ICON_DOWN_ARROW', ICON_DOWN_ARROW_ICON)

_STYLE_QLISTVIEW = '''
QListView {
    background: rgba(80, 80, 80, 255);
    border: 0px solid rgba(0, 0, 0, 0);
}
QListView::item {
    color: rgba(255, 255, 255, 120);
    background: rgba(60, 60, 60, 255);
    border-bottom: 1px solid rgba(0, 0, 0, 0);
    border-radius: 0px;
    margin: 0px;
    padding: 2px;
}
QListView::item:selected {
    color: rgba(255, 255, 255, 200);
    background: rgba(255, 255, 255, 15);
    border-bottom: 1px solid rgba(255, 255, 255, 5);
    border-radius: 0px;
    margin:0px;
    padding: 2px;
}
'''


class _NodeGroubBox(QtGui.QGroupBox):

    def __init__(self, label, parent=None):
        super(_NodeGroubBox, self).__init__(parent)
        self.setStyleSheet(_STYLE_QGROUPBOX)
        self.setTitle(label)
        self.setMaximumSize(120, 50)
        self._layout = QtGui.QVBoxLayout(self)
        self._layout.setContentsMargins(0, 4, 0, 0)

    def add_node_widget(self, widget):
        self._layout.addWidget(widget)


class BaseNodeWidget(QtGui.QGraphicsProxyWidget):
    """
    Base Node Widget.
    """

    value_changed = QtCore.Signal(str, str)

    def __init__(self, parent=None, name='widget', label=''):
        super(BaseNodeWidget, self).__init__(parent)
        self.setZValue(Z_VAL_KNOB)
        self._name = name
        self._label = label

    def _value_changed(self):
        self.value_changed.emit(self.name, self.value)

    @property
    def value(self):
        raise NotImplementedError

    @value.setter
    def value(self, text):
        raise NotImplementedError

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, label):
        self._label = label

    @property
    def type(self):
        return str(self.__class__.__name__)

    @property
    def node(self):
        self.parentItem()

    @property
    def name(self):
        return self._name


class ComboNodeWidget(BaseNodeWidget):
    """
    ComboBox Node Widget.
    """

    def __init__(self, parent=None, name='', label='', items=None):
        super(ComboNodeWidget, self).__init__(parent, name, label)
        self.setZValue(Z_VAL_KNOB + 1)
        self._combo = QtGui.QComboBox()
        self._combo.setStyleSheet(_STYLE_QCOMBOBOX)
        self._combo.setMinimumHeight(24)
        self._combo.activated.connect(self._value_changed)
        list_view = QtGui.QListView(self._combo)
        list_view.setStyleSheet(_STYLE_QLISTVIEW)
        self._combo.setView(list_view)
        group = _NodeGroubBox(label)
        group.add_node_widget(self._combo)
        self.setWidget(group)
        self.add_items(items)

    @property
    def type(self):
        return 'ComboNodeWidget'

    @property
    def value(self):
        return str(self._combo.currentText())

    @value.setter
    def value(self, text=''):
        index = self._combo.findText(text, QtCore.Qt.MatchExactly)
        self._combo.setCurrentIndex(index)

    def add_item(self, item):
        self._combo.addItem(item)

    def add_items(self, items=None):
        if items:
            self._combo.addItems(items)

    def all_items(self):
        return [self._combo.itemText(i) for i in range(self._combo.count)]

    def sort_items(self):
        items = sorted(self.all_items())
        self._combo.clear()
        self._combo.addItems(items)

    def clear(self):
        self._combo.clear()


class LineEditNodeWidget(BaseNodeWidget):
    """
    LineEdit Node Widget.
    """

    def __init__(self, parent=None, name='', label='', text=''):
        super(LineEditNodeWidget, self).__init__(parent, name, label)
        self._ledit = QtGui.QLineEdit()
        self._ledit.setStyleSheet(_STYLE_QLINEEDIT)
        self._ledit.setAlignment(QtCore.Qt.AlignCenter)
        self._ledit.textChanged.connect(self._value_changed)
        group = _NodeGroubBox(label)
        group.add_node_widget(self._ledit)
        self.setWidget(group)
        self.text = text

    @property
    def type(self):
        return 'LineEditNodeWidget'

    @property
    def value(self):
        return str(self._ledit.text())

    @value.setter
    def value(self, text=''):
        self._ledit.setText(text)
