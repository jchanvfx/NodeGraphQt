#!/usr/bin/python
from Qt import QtWidgets

from .custom_widget_value_edit import _NumberValueEdit
from .prop_widgets_abstract import BaseProperty


class _PropVector(BaseProperty):
    """
    Base widget for the PropVector widgets.
    """

    def __init__(self, parent=None, fields=0):
        super(_PropVector, self).__init__(parent)
        self._value = []
        self._items = []
        self._can_emit = True

        layout = QtWidgets.QHBoxLayout(self)
        layout.setSpacing(2)
        layout.setContentsMargins(0, 0, 0, 0)
        for i in range(fields):
            self._add_item(i)

    def _add_item(self, index):
        _ledit = _NumberValueEdit()
        _ledit.index = index
        _ledit.value_changed.connect(
            lambda: self._on_value_change(_ledit.get_value(), _ledit.index)
        )

        self.layout().addWidget(_ledit)
        self._value.append(0.0)
        self._items.append(_ledit)

    def _on_value_change(self, value=None, index=None):
        if self._can_emit:
            if index is not None:
                self._value = list(self._value)
                self._value[index] = value
            self.value_changed.emit(self.get_name(), self._value)

    def _update_items(self):
        if not isinstance(self._value, (list, tuple)):
            raise TypeError('Value "{}" must be either list or tuple.'
                            .format(self._value))
        for index, value in enumerate(self._value):
            if (index + 1) > len(self._items):
                continue
            if self._items[index].get_value() != value:
                self._items[index].set_value(value)

    def set_data_type(self, data_type):
        """
        Sets the input line edit fields to either display in float or int.

        Args:
            data_type(int or float): int or float data type object.
        """
        for item in self._items:
            item.set_data_type(data_type)

    def set_steps(self, steps):
        """
        Sets the step items in the MMB context menu.

        Args:
            steps (list[int] or list[float]): list of ints or floats.
        """
        for item in self._items:
            item.set_steps(steps)

    def set_min(self, value):
        """
        Set the minimum range for the input fields.

        Args:
            value (int or float): minimum range value.
        """
        for item in self._items:
            item.set_min(value)

    def set_max(self, value):
        """
        Set the maximum range for the input fields.

        Args:
            value (int or float): maximum range value.
        """
        for item in self._items:
            item.set_max(value)

    def get_value(self):
        return self._value

    def set_value(self, value=None):
        if value != self.get_value():
            self._value = value
            self._can_emit = False
            self._update_items()
            self._can_emit = True
            self._on_value_change()


class PropVector2(_PropVector):
    """
    Displays a node property as a "Vector2" widget in the PropertiesBin
    widget.

    Useful for display X,Y data.
    """

    def __init__(self, parent=None):
        super(PropVector2, self).__init__(parent, 2)


class PropVector3(_PropVector):
    """
    Displays a node property as a "Vector3" widget in the PropertiesBin
    widget.

    Useful for displaying x,y,z data.
    """

    def __init__(self, parent=None):
        super(PropVector3, self).__init__(parent, 3)


class PropVector4(_PropVector):
    """
    Displays a node property as a "Vector4"  widget in the PropertiesBin
    widget.

    Useful for display r,g,b,a data.
    """

    def __init__(self, parent=None):
        super(PropVector4, self).__init__(parent, 4)
