#!/usr/bin/python
from Qt import QtWidgets, QtCore


class PropLabel(QtWidgets.QLabel):
    """
    Displays a node property as a "QLabel" widget in the PropertiesBin widget.
    """

    value_changed = QtCore.Signal(str, object)

    def __init__(self, parent=None):
        super(PropLabel, self).__init__(parent)
        self._name = None

    def __repr__(self):
        return '<{}() object at {}>'.format(
            self.__class__.__name__, hex(id(self)))

    def get_name(self):
        return self._name

    def set_name(self, name):
        self._name = name

    def get_value(self):
        return self.text()

    def set_value(self, value):
        if value != self.get_value():
            self.setText(str(value))
            self.value_changed.emit(self.get_name(), value)


class PropLineEdit(QtWidgets.QLineEdit):
    """
    Displays a node property as a "QLineEdit" widget in the PropertiesBin
    widget.
    """

    value_changed = QtCore.Signal(str, object)

    def __init__(self, parent=None):
        super(PropLineEdit, self).__init__(parent)
        self._name = None
        self.editingFinished.connect(self._on_editing_finished)

    def __repr__(self):
        return '<{}() object at {}>'.format(
            self.__class__.__name__, hex(id(self)))

    def _on_editing_finished(self):
        self.value_changed.emit(self.get_name(), self.text())

    def get_name(self):
        return self._name

    def set_name(self, name):
        self._name = name

    def get_value(self):
        return self.text()

    def set_value(self, value):
        _value = str(value)
        if _value != self.get_value():
            self.setText(_value)
            self.value_changed.emit(self.get_name(), _value)


class PropTextEdit(QtWidgets.QTextEdit):
    """
    Displays a node property as a "QTextEdit" widget in the PropertiesBin
    widget.
    """

    value_changed = QtCore.Signal(str, object)

    def __init__(self, parent=None):
        super(PropTextEdit, self).__init__(parent)
        self._name = None
        self._prev_text = ''

    def __repr__(self):
        return '<{}() object at {}>'.format(
            self.__class__.__name__, hex(id(self)))

    def focusInEvent(self, event):
        super(PropTextEdit, self).focusInEvent(event)
        self._prev_text = self.toPlainText()

    def focusOutEvent(self, event):
        super(PropTextEdit, self).focusOutEvent(event)
        if self._prev_text != self.toPlainText():
            self.value_changed.emit(self.get_name(), self.toPlainText())
        self._prev_text = ''

    def get_name(self):
        return self._name

    def set_name(self, name):
        self._name = name

    def get_value(self):
        return self.toPlainText()

    def set_value(self, value):
        _value = str(value)
        if _value != self.get_value():
            self.setPlainText(_value)
            self.value_changed.emit(self.get_name(), _value)


class PropComboBox(QtWidgets.QComboBox):
    """
    Displays a node property as a "QComboBox" widget in the PropertiesBin
    widget.
    """

    value_changed = QtCore.Signal(str, object)

    def __init__(self, parent=None):
        super(PropComboBox, self).__init__(parent)
        self._name = None
        self.currentIndexChanged.connect(self._on_index_changed)

    def __repr__(self):
        return '<{}() object at {}>'.format(
            self.__class__.__name__, hex(id(self)))

    def _on_index_changed(self):
        self.value_changed.emit(self.get_name(), self.get_value())

    def items(self):
        """
        Returns items from the combobox.

        Returns:
            list[str]: list of strings.
        """
        return [self.itemText(i) for i in range(self.count())]

    def set_items(self, items):
        """
        Set items on the combobox.

        Args:
            items (list[str]): list of strings.
        """
        self.clear()
        self.addItems(items)

    def get_name(self):
        return self._name

    def set_name(self, name):
        self._name = name

    def get_value(self):
        return self.currentText()

    def set_value(self, value):
        if value != self.get_value():
            idx = self.findText(value, QtCore.Qt.MatchExactly)
            self.setCurrentIndex(idx)
            if idx >= 0:
                self.value_changed.emit(self.get_name(), value)


class PropCheckBox(QtWidgets.QCheckBox):
    """
    Displays a node property as a "QCheckBox" widget in the PropertiesBin
    widget.
    """

    value_changed = QtCore.Signal(str, object)

    def __init__(self, parent=None):
        super(PropCheckBox, self).__init__(parent)
        self._name = None
        self.clicked.connect(self._on_clicked)

    def __repr__(self):
        return '<{}() object at {}>'.format(
            self.__class__.__name__, hex(id(self)))

    def _on_clicked(self):
        self.value_changed.emit(self.get_name(), self.get_value())

    def get_name(self):
        return self._name

    def set_name(self, name):
        self._name = name

    def get_value(self):
        return self.isChecked()

    def set_value(self, value):
        _value = bool(value)
        if _value != self.get_value():
            self.setChecked(_value)
            self.value_changed.emit(self.get_name(), _value)


class PropSpinBox(QtWidgets.QSpinBox):
    """
    Displays a node property as a "QSpinBox" widget in the PropertiesBin widget.
    """

    value_changed = QtCore.Signal(str, object)

    def __init__(self, parent=None):
        super(PropSpinBox, self).__init__(parent)
        self._name = None
        self.setButtonSymbols(self.NoButtons)
        self.valueChanged.connect(self._on_value_change)

    def __repr__(self):
        return '<{}() object at {}>'.format(
            self.__class__.__name__, hex(id(self)))

    def _on_value_change(self, value):
        self.value_changed.emit(self.get_name(), value)

    def get_name(self):
        return self._name

    def set_name(self, name):
        self._name = name

    def get_value(self):
        return self.value()

    def set_value(self, value):
        if value != self.get_value():
            self.setValue(value)


class PropDoubleSpinBox(QtWidgets.QDoubleSpinBox):
    """
    Displays a node property as a "QDoubleSpinBox" widget in the PropertiesBin
    widget.
    """

    value_changed = QtCore.Signal(str, object)

    def __init__(self, parent=None):
        super(PropDoubleSpinBox, self).__init__(parent)
        self._name = None
        self.setButtonSymbols(self.NoButtons)
        self.valueChanged.connect(self._on_value_change)

    def __repr__(self):
        return '<{}() object at {}>'.format(
            self.__class__.__name__, hex(id(self)))

    def _on_value_change(self, value):
        self.value_changed.emit(self.get_name(), value)

    def get_name(self):
        return self._name

    def set_name(self, name):
        self._name = name

    def get_value(self):
        return self.value()

    def set_value(self, value):
        if value != self.get_value():
            self.setValue(value)


# class PropPushButton(QtWidgets.QPushButton):
#     """
#     Displays a node property as a "QPushButton" widget in the PropertiesBin
#     widget.
#     """
#
#     value_changed = QtCore.Signal(str, object)
#     button_clicked = QtCore.Signal(str, object)
#
#     def __init__(self, parent=None):
#         super(PropPushButton, self).__init__(parent)
#         self._name = None
#         self.clicked.connect(self.button_clicked.emit)
#
#     def set_on_click_func(self, func, node):
#         """
#         Sets slot function for the PropPushButton widget.
#
#         Args:
#             func (function): property slot function.
#             node (NodeGraphQt.NodeObject): node object.
#         """
#         if not callable(func):
#             raise TypeError('var func is not a function.')
#         self.clicked.connect(lambda: func(node))
#
#     def get_value(self):
#         return
#
#     def set_value(self, value):
#         return
