#!/usr/bin/python
from Qt import QtWidgets, QtCore


class BaseProperty(QtWidgets.QWidget):
    """
    Base class for a custom node property widget to be displayed in the
    PropertiesBin widget.

    Inherits from: :class:`PySide2.QtWidgets.QWidget`
    """

    value_changed = QtCore.Signal(str, object)

    def __repr__(self):
        return '<{}() object at {}>'.format(
            self.__class__.__name__, hex(id(self)))

    def get_value(self):
        """

        Returns:
            object:
        """
        raise NotImplementedError

    def set_value(self, value):
        """

        Args:
            value (object):

        Returns:
            object:
        """
        raise NotImplementedError
