#!/usr/bin/python
from Qt import QtWidgets, QtCore


class BaseProperty(QtWidgets.QWidget):
    """
    Base class for a custom node property widget to be displayed in the
    PropertiesBin widget.

    Inherits from: :class:`PySide2.QtWidgets.QWidget`
    """

    value_changed = QtCore.Signal(str, object)

    def __init__(self, parent=None):
        super(BaseProperty, self).__init__(parent)
        self._name = None

    def __repr__(self):
        return '<{}() object at {}>'.format(
            self.__class__.__name__, hex(id(self)))

    def get_name(self):
        """
        Returns:
            str: property name matching the node property.
        """
        return self._name

    def set_name(self, name):
        """
        Args:
            name (str): property name matching the node property.
        """
        self._name = name

    def set_items(self, items):
        """
        See Also:
            :meth:`NodeObject.create_property`

        Args:
            items (list or tuple): list of items.
        """
        return

    def set_min(self, min_value):
        """
        See Also:
            :meth:`NodeObject.create_property`

        Args:
            min_value (int or float): min value.
        """
        return

    def set_max(self, max_value):
        """
        See Also:
            :meth:`NodeObject.create_property`

        Args:
            max_value (int or float): max value.
        """
        return

    def get_value(self):
        """
        Returns:
            object: widgets current value.
        """
        raise NotImplementedError

    def set_value(self, value):
        """
        Args:
            value (object): property value to update the widget.
        """
        raise NotImplementedError
