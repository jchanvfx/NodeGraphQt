#!/usr/bin/python
from collections import defaultdict

from .. import QtWidgets, QtCore, QtGui
from ..constants import (NODE_PROP_QLABEL,
                         NODE_PROP_QLINEEDIT,
                         NODE_PROP_QTEXTEDIT,
                         NODE_PROP_QCOMBO,
                         NODE_PROP_QCHECKBOX,
                         NODE_PROP_QSPINBOX,
                         NODE_PROP_COLORPICKER,
                         NODE_PROP_SLIDER,
                         NODE_PROP_FILE,
                         NODE_PROP_VECTOR2,
                         NODE_PROP_VECTOR3,
                         NODE_PROP_VECTOR4,
                         NODE_PROP_FLOAT,
                         NODE_PROP_INT,
                         NODE_PROP_BUTTON)
from .file_dialog import file_dialog


class BaseProperty(QtWidgets.QWidget):
    value_changed = QtCore.Signal(str, object)

    def set_value(self, value):
        raise NotImplementedError

    def get_value(self):
        raise NotImplementedError


class PropColorPicker(BaseProperty):
    def __init__(self, parent=None):
        super(PropColorPicker, self).__init__(parent)
        self._color = (0, 0, 0)
        self._button = QtWidgets.QPushButton()
        self._vector = PropVector3()
        self._vector.set_value([0, 0, 0])
        self._update_color()

        self._button.clicked.connect(self._on_select_color)
        self._vector.value_changed.connect(self._on_vector_changed)
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        layout.addWidget(self._button, 0, QtCore.Qt.AlignLeft)
        layout.addWidget(self._vector, 1, QtCore.Qt.AlignLeft)

    def _on_vector_changed(self, o, value):
        self._color = tuple(value)
        self._update_color()
        self.value_changed.emit(self.toolTip(), value)

    def _update_vector(self):
        self._vector.set_value(list(self._color))

    def _on_select_color(self):
        color = QtWidgets.QColorDialog.getColor(QtGui.QColor.fromRgbF(*self.get_value()))
        if color.isValid():
            self.set_value(color.getRgb())

    def _update_color(self):
        c = [int(max(min(i, 255), 0)) for i in self._color]
        hex_color = '#{0:02x}{1:02x}{2:02x}'.format(*c)
        self._button.setStyleSheet(
            '''QPushButton {{background-color: rgba({0}, {1}, {2}, 255);}}
               QPushButton::hover {{background-color: rgba({0}, {1}, {2}, 200);}}'''.format(*c))
        self._button.setToolTip('rgb: {}\nhex: {}'.format(self._color[:3], hex_color))

    def get_value(self):
        return self._color[:3]

    def set_value(self, value):
        if value != self.get_value():
            self._color = value
            self._update_color()
            self._update_vector()
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
            self.setText(str(value))
            self.value_changed.emit(self.toolTip(), value)


class PropLineEdit(QtWidgets.QLineEdit):
    value_changed = QtCore.Signal(str, object)

    def __init__(self, parent=None):
        super(PropLineEdit, self).__init__(parent)
        self.editingFinished.connect(self._on_editing_finished)

    def _on_editing_finished(self):
        self.value_changed.emit(self.toolTip(), self.text())

    def get_value(self):
        return self.text()

    def set_value(self, value):
        _value = str(value)
        if _value != self.get_value():
            self.setText(_value)
            self.value_changed.emit(self.toolTip(), _value)


class PropTextEdit(QtWidgets.QTextEdit):
    value_changed = QtCore.Signal(str, object)

    def __init__(self, parent=None):
        super(PropTextEdit, self).__init__(parent)
        self.__prev_text = ''

    def focusInEvent(self, event):
        super(PropTextEdit, self).focusInEvent(event)
        self.__prev_text = self.toPlainText()

    def focusOutEvent(self, event):
        super(PropTextEdit, self).focusOutEvent(event)
        if self.__prev_text != self.toPlainText():
            self.value_changed.emit(self.toolTip(), self.toPlainText())
        self.__prev_text = ''

    def get_value(self):
        return self.toPlainText()

    def set_value(self, value):
        _value = str(value)
        if _value != self.get_value():
            self.setPlainText(_value)
            self.value_changed.emit(self.toolTip(), _value)


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
        if type(value) is list:
            self.set_items(value)
            return
        if value != self.get_value():
            idx = self.findText(value, QtCore.Qt.MatchExactly)
            self.setCurrentIndex(idx)
            if idx >= 0:
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


class PropFilePath(BaseProperty):
    def __init__(self, parent=None):
        super(PropFilePath, self).__init__(parent)
        self._ledit = QtWidgets.QLineEdit()
        self._ledit.setAlignment(QtCore.Qt.AlignLeft)
        self._ledit.editingFinished.connect(self._on_value_change)
        self._ledit.clearFocus()

        icon = self.style().standardIcon(QtWidgets.QStyle.StandardPixmap(21))
        _button = QtWidgets.QPushButton()
        _button.setIcon(icon)

        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(self._ledit)
        hbox.addWidget(_button)
        self.setLayout(hbox)
        _button.clicked.connect(self._on_select_file)

        self._ledit.setStyleSheet("QLineEdit{border:1px solid}")
        _button.setStyleSheet("QPushButton{border:1px solid}")
        self._ext = "*"

    def set_ext(self, ext):
        self._ext = ext

    def _on_select_file(self):
        file_path = file_dialog.getOpenFileName(self, ext_filter=self._ext)
        file = file_path[0] or None
        if file:
            self.set_value(file)

    def _on_value_change(self, value=None):
        if value is None:
            value = self._ledit.text()
        self.value_changed.emit(self.toolTip(), value)

    def get_value(self):
        return self._ledit.text()

    def set_value(self, value):
        _value = str(value)
        if _value != self.get_value():
            self._ledit.setText(_value)
            self._on_value_change(_value)


class _valueMenu(QtWidgets.QMenu):
    mouseMove = QtCore.Signal(object)
    mouseRelease = QtCore.Signal(object)
    stepChange = QtCore.Signal()

    def __init__(self, parent=None):
        super(_valueMenu, self).__init__(parent)
        self.step = 1
        self.last_action = None
        self.steps = []

    def set_steps(self, steps):
        self.clear()
        self.steps = steps
        for step in steps:
            self._add_action(step)

    def _add_action(self, step):
        action = QtWidgets.QAction(str(step), self)
        action.step = step
        self.addAction(action)

    def mouseMoveEvent(self, event):
        self.mouseMove.emit(event)
        super(_valueMenu, self).mouseMoveEvent(event)

        action = self.actionAt(event.pos())
        if action:
            if action is not self.last_action:
                self.stepChange.emit()
            self.last_action = action
            self.step = action.step
        elif self.last_action:
            self.setActiveAction(self.last_action)

    def mousePressEvent(self, event):
        return

    def mouseReleaseEvent(self, event):
        self.mouseRelease.emit(event)
        super(_valueMenu, self).mouseReleaseEvent(event)

    def set_data_type(self, dt):
        if dt is int:
            new_steps = []
            for step in self.steps:
                if "." not in str(step):
                    new_steps.append(step)
            self.set_steps(new_steps)
        elif dt is float:
            self.set_steps(self.steps)


class _valueEdit(QtWidgets.QLineEdit):
    valueChanged = QtCore.Signal(object)

    def __init__(self, parent=None):
        super(_valueEdit, self).__init__(parent)
        self.mid_state = False
        self._data_type = float
        self.setText("0")

        self.pre_x = None
        self.pre_val = None
        self._step = 1
        self._speed = 0.1

        self.editingFinished.connect(self._on_text_changed)

        self.menu = _valueMenu()
        self.menu.mouseMove.connect(self.mouseMoveEvent)
        self.menu.mouseRelease.connect(self.mouseReleaseEvent)
        self.menu.stepChange.connect(self._reset)
        steps = [0.001, 0.01, 0.1, 1, 10, 100, 1000]
        self.menu.set_steps(steps)

        self.set_data_type(float)

    def _on_text_changed(self):
        self.valueChanged.emit(self.value())

    def _reset(self):
        self.pre_x = None

    def mouseMoveEvent(self, event):
        if self.mid_state:
            if self.pre_x is None:
                self.pre_x = event.x()
                self.pre_val = self.value()
            else:
                self.set_step(self.menu.step)
                delta = event.x() - self.pre_x
                value = self.pre_val + int(delta * self._speed) * self._step
                self.setValue(value)
                self._on_text_changed()

        super(_valueEdit, self).mouseMoveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MiddleButton:
            self.mid_state = True
            self._reset()
            self.menu.exec_(QtGui.QCursor.pos())
        super(_valueEdit, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.menu.close()
        self.mid_state = False
        super(_valueEdit, self).mouseReleaseEvent(event)

    def set_step(self, step):
        self._step = step

    def set_data_type(self, dt):
        if dt is int:
            self.setValidator(QtGui.QIntValidator())
        elif dt is float:
            self.setValidator(QtGui.QDoubleValidator())
        self._data_type = dt
        self.menu.set_data_type(dt)

    def _convert_text(self, text):
        # int("1.0") will return error
        # so we use int(float("1.0"))
        try:
            value = float(text)
        except:
            value = 0.0
        if self._data_type is int:
            value = int(value)
        return value

    def value(self):
        if self.text().startswith("."):
            text = "0" + self.text()
            self.setText(text)
        return self._convert_text(self.text())

    def setValue(self, value):
        if value != self.value():
            self.setText(str(self._convert_text(value)))


class _slider(QtWidgets.QSlider):
    def __init__(self, parent=None):
        super(_slider, self).__init__(parent)
        self.setOrientation(QtCore.Qt.Horizontal)
        self.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                           QtWidgets.QSizePolicy.Preferred)

    def _update_value(self, x):
        value = (self.maximum() - self.minimum()) * x / self.width() + self.minimum()
        self.setValue(value)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self._update_value(event.pos().x())
        super(_slider, self).mousePressEvent(event)


class _valueSliderEdit(QtWidgets.QWidget):
    valueChanged = QtCore.Signal(object)

    def __init__(self, parent=None):
        super(_valueSliderEdit, self).__init__(parent)
        self._edit = _valueEdit()
        self._edit.valueChanged.connect(self._on_edit_changed)
        self._edit.setMaximumWidth(70)
        self._slider = _slider()
        self._slider.valueChanged.connect(self._on_slider_changed)

        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(self._edit)
        hbox.addWidget(self._slider)
        self.setLayout(hbox)

        self._mul = 1000.0
        self.set_min(0)
        self.set_max(10)
        self.set_data_type(float)
        self._lock = False

    def _on_edit_changed(self, value):
        self._set_slider_value(value)
        self.valueChanged.emit(self._edit.value())

    def _on_slider_changed(self, value):
        if self._lock:
            self._lock = False
            return
        value = value / float(self._mul)
        self._edit.setValue(value)
        self._on_edit_changed(value)

    def _set_slider_value(self, value):
        value = int(value * self._mul)

        if value == self._slider.value():
            return
        self._lock = True
        _min = self._slider.minimum()
        _max = self._slider.maximum()
        if _min <= value <= _max:
            self._slider.setValue(value)
        elif value < _min and self._slider.value() != _min:
            self._slider.setValue(_min)
        elif value > _max and self._slider.value() != _max:
            self._slider.setValue(_max)

    def set_min(self, value=0):
        self._slider.setMinimum(int(value * self._mul))

    def set_max(self, value=10):
        self._slider.setMaximum(int(value * self._mul))

    def set_data_type(self, dt):
        _min = int(self._slider.minimum() / self._mul)
        _max = int(self._slider.maximum() / self._mul)
        if dt is int:
            self._mul = 1.0
        elif dt is float:
            self._mul = 1000.0

        self.set_min(_min)
        self.set_max(_max)
        self._edit.set_data_type(dt)

    def value(self):
        return self._edit.value()

    def setValue(self, value):
        self._edit.setValue(value)
        self._on_edit_changed(value)


class _doubleSpinBox(QtWidgets.QDoubleSpinBox):
    def __init__(self, parent=None):
        super(_doubleSpinBox, self).__init__(parent)
        self.setButtonSymbols(self.NoButtons)
        self.setRange(-9999999999999999.0, 9999999999999999.0)
        self.setDecimals(16)
        self.setValue(0)
        self.setStyleSheet("QDoubleSpinBox{border:1px solid}")

    def textFromValue(self, value):
        return str(value)


class PropVector(BaseProperty):
    def __init__(self, parent=None, dim=3):
        super(PropVector, self).__init__(parent)
        hbox = QtWidgets.QHBoxLayout()
        self._value = []
        self._items = []

        for i in range(dim):
            self._add_item(i, hbox)

        self._can_emit = True
        self.setLayout(hbox)

    def _add_item(self, index, hbox):
        _ledit = _valueEdit()
        _ledit.index = index
        _ledit.valueChanged.connect(lambda: self._on_value_change(_ledit.value(), _ledit.index))

        hbox.addWidget(_ledit)
        self._value.append(0.0)
        self._items.append(_ledit)

    def _on_value_change(self, value=None, index=None):
        if self._can_emit:
            if index is not None:
                self._value[index] = value
            self.value_changed.emit(self.toolTip(), self._value)
        self.value_changed.emit(self.toolTip(), self._value)

    def _update_items(self):
        for index, value in enumerate(self._value):
            if index < len(self._items) and self._items[index].value() != value:
                self._items[index].setValue(value)

    def get_value(self):
        return self._value

    def set_value(self, value):
        if value != self.get_value():
            self._value = value.copy()
            self._can_emit = False
            self._update_items()
            self._can_emit = True
            self._on_value_change()


class PropVector2(PropVector):
    def __init__(self, parent=None):
        super(PropVector2, self).__init__(parent, 2)


class PropVector3(PropVector):
    def __init__(self, parent=None):
        super(PropVector3, self).__init__(parent, 3)


class PropVector4(PropVector):
    def __init__(self, parent=None):
        super(PropVector4, self).__init__(parent, 4)


class PropFloat(_valueSliderEdit):
    value_changed = QtCore.Signal(str, object)

    def __init__(self, parent=None):
        super(PropFloat, self).__init__(parent)
        self.valueChanged.connect(self._on_value_changed)

    def _on_value_changed(self, value):
        self.value_changed.emit(self.toolTip(), value)

    def get_value(self):
        return self.value()

    def set_value(self, value):
        if value != self.get_value():
            self.setValue(value)
            self.value_changed.emit(self.toolTip(), value)


class PropInt(PropFloat):
    def __init__(self, parent=None):
        super(PropInt, self).__init__(parent)
        self.set_data_type(int)


class PropButton(QtWidgets.QPushButton):
    value_changed = QtCore.Signal(str, object)

    def __init__(self, parent=None):
        super(PropButton, self).__init__(parent)

    def set_value(self, value, node=None):
        # value: list of functions
        if type(value) is not list:
            return
        for func in value:
            self.clicked.connect(lambda: func(node))

    def get_value(self):
        return None


WIDGET_MAP = {
    NODE_PROP_QLABEL: PropLabel,
    NODE_PROP_QLINEEDIT: PropLineEdit,
    NODE_PROP_QTEXTEDIT: PropTextEdit,
    NODE_PROP_QCOMBO: PropComboBox,
    NODE_PROP_QCHECKBOX: PropCheckBox,
    NODE_PROP_QSPINBOX: PropSpinBox,
    NODE_PROP_COLORPICKER: PropColorPicker,
    NODE_PROP_SLIDER: PropSlider,
    NODE_PROP_FILE: PropFilePath,
    NODE_PROP_VECTOR2: PropVector2,
    NODE_PROP_VECTOR3: PropVector3,
    NODE_PROP_VECTOR4: PropVector4,
    NODE_PROP_FLOAT: PropFloat,
    NODE_PROP_INT: PropInt,
    NODE_PROP_BUTTON: PropButton
}


def registerPropType(name, prop_class, override=False):
    global WIDGET_MAP
    if name in WIDGET_MAP.keys() and not override:
        raise Exception("Prop type {} has already exists, u can use override=True to override)".format(name))
    WIDGET_MAP[name] = prop_class

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

    def __repr__(self):
        return '<PropWindow object at {}>'.format(hex(id(self)))

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

        label = QtWidgets.QLabel(label)
        label_flags = QtCore.Qt.AlignCenter | QtCore.Qt.AlignRight
        if widget.__class__.__name__ == 'PropTextEdit':
            label_flags = label_flags | QtCore.Qt.AlignTop
        elif widget.__class__.__name__ == 'PropButton':
            label.setVisible(False)
            widget.setText(name)
        self.__layout.addWidget(label, row, 0, label_flags)
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

        close_btn = QtWidgets.QPushButton('X')
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
        return '<NodePropWidget object at {}>'.format(hex(id(self)))

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

        min_widget_height = 25
        # populate tab properties.
        for tab in sorted(tab_mapping.keys()):
            prop_window = self.__tab_windows[tab]
            for prop_name, value in tab_mapping[tab]:
                wid_type = model.get_widget_type(prop_name)
                if wid_type == 0:
                    continue

                WidClass = WIDGET_MAP.get(wid_type)
                widget = WidClass()
                widget.setMinimumHeight(min_widget_height)
                if prop_name in common_props.keys():
                    if 'items' in common_props[prop_name].keys():
                        _prop_name = '_' + prop_name + "_"
                        if node.has_property(_prop_name):
                            widget.set_items(node.get_property(_prop_name))
                        else:
                            widget.set_items(common_props[prop_name]['items'])
                    if 'range' in common_props[prop_name].keys():
                        prop_range = common_props[prop_name]['range']
                        widget.set_min(prop_range[0])
                        widget.set_max(prop_range[1])
                    if 'ext' in common_props[prop_name].keys():
                        widget.set_ext(common_props[prop_name]['ext'])
                    if 'funcs' in common_props[prop_name].keys():
                        widget.set_value(common_props[prop_name]['funcs'], node)

                prop_window.add_widget(prop_name, widget, value,
                                       prop_name.replace('_', ' '))
                widget.value_changed.connect(self._on_property_changed)

        # add "Node" tab properties.
        self.add_tab('Node')
        default_props = ['color', 'text_color', 'disabled', 'id']
        prop_window = self.__tab_windows['Node']
        for prop_name in default_props:
            wid_type = model.get_widget_type(prop_name)
            WidClass = WIDGET_MAP.get(wid_type)

            widget = WidClass()
            widget.setMinimumHeight(min_widget_height)
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
        if name == 'name':
            return self.name_wgt
        for tab_name, prop_win in self.__tab_windows.items():
            widget = prop_win.get_widget(name)
            if widget:
                return widget


if __name__ == '__main__':
    import sys
    from .. import BaseNode, NodeGraph


    class TestNode(BaseNode):
        NODE_NAME = 'test node'

        def __init__(self):
            super(TestNode, self).__init__()
            self.create_property('label_test', 'foo bar',
                                 widget_type=NODE_PROP_QLABEL)
            self.create_property('line_edit', 'hello',
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
            self.create_property('text_edit', 'test text',
                                 widget_type=NODE_PROP_QTEXTEDIT,
                                 tab='text')


    def prop_changed(node_id, prop_name, prop_value):
        print('-' * 100)
        print(node_id, prop_name, prop_value)


    def prop_close(node_id):
        print('=' * 100)
        print(node_id)


    app = QtWidgets.QApplication(sys.argv)

    graph = NodeGraph()
    graph.register_node(TestNode)

    test_node = graph.create_node('nodeGraphQt.nodes.TestNode')

    node_prop = NodePropWidget(node=test_node)
    node_prop.property_changed.connect(prop_changed)
    node_prop.property_closed.connect(prop_close)
    node_prop.show()

    app.exec_()
