#!/usr/bin/python
from Qt import QtWidgets, QtCore, QtGui

from .custom_widget_vectors import PropVector3, PropVector4
from .prop_widgets_abstract import BaseProperty


class PropColorPickerRGB(BaseProperty):
    """
    Color picker widget for a node property.
    """

    def __init__(self, parent=None):
        super(PropColorPickerRGB, self).__init__(parent)
        self._color = (0, 0, 0)
        self._button = QtWidgets.QPushButton()
        self._vector = PropVector3()
        self._vector.set_steps([1, 10, 100])
        self._vector.set_data_type(int)
        self._vector.set_value([0, 0, 0])
        self._vector.set_min(0)
        self._vector.set_max(255)
        self._update_color()

        self._button.clicked.connect(self._on_select_color)
        self._vector.value_changed.connect(self._on_vector_changed)

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._button, 0, QtCore.Qt.AlignLeft)
        layout.addWidget(self._vector, 1, QtCore.Qt.AlignLeft)

    def _on_vector_changed(self, _, value):
        self._color = tuple(value)
        self._update_color()
        self.value_changed.emit(self.get_name(), value)

    def _on_select_color(self):
        current_color = QtGui.QColor(*self.get_value())
        color = QtWidgets.QColorDialog.getColor(current_color, self)
        if color.isValid():
            self.set_value(color.getRgb())

    def _update_vector(self):
        self._vector.set_value(self._color)

    def _update_color(self):
        c = [int(max(min(i, 255), 0)) for i in self._color]
        hex_color = '#{0:02x}{1:02x}{2:02x}'.format(*c)
        self._button.setStyleSheet(
            '''
            QPushButton {{background-color: rgba({0}, {1}, {2}, 255);}}
            QPushButton::hover {{background-color: rgba({0}, {1}, {2}, 200);}}
            '''.format(*c)
        )
        self._button.setToolTip(
            'rgb: {}\nhex: {}'.format(self._color[:3], hex_color)
        )

    def set_data_type(self, data_type):
        """
        Sets the input line edit fields to either display in float or int.

        Args:
            data_type(int or float): int or float data type object.
        """
        self._vector.set_data_type(data_type)

    def get_value(self):
        return self._color[:3]

    def set_value(self, value):
        if value != self.get_value():
            self._color = value
            self._update_color()
            self._update_vector()
            self.value_changed.emit(self.get_name(), value)


class PropColorPickerRGBA(PropColorPickerRGB):
    """
    Color4 (rgba) picker widget for a node property.
    """

    def __init__(self, parent=None):
        BaseProperty.__init__(self, parent)
        self._color = (0, 0, 0, 255)
        self._button = QtWidgets.QPushButton()
        self._vector = PropVector4()
        self._vector.set_steps([1, 10, 100])
        self._vector.set_data_type(int)
        self._vector.set_value([0, 0, 0, 255])
        self._vector.set_min(0)
        self._vector.set_max(255)
        self._update_color()

        self._button.clicked.connect(self._on_select_color)
        self._vector.value_changed.connect(self._on_vector_changed)

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._button, 0, QtCore.Qt.AlignLeft)
        layout.addWidget(self._vector, 1, QtCore.Qt.AlignLeft)

    def _update_color(self):
        c = [int(max(min(i, 255), 0)) for i in self._color]
        hex_color = '#{0:02x}{1:02x}{2:02x}{3:03x}'.format(*c)
        self._button.setStyleSheet(
            '''
            QPushButton {{background-color: rgba({0}, {1}, {2}, {3});}}
            QPushButton::hover {{background-color: rgba({0}, {1}, {2}, {3});}}
            '''.format(*c)
        )
        self._button.setToolTip(
            'rgba: {}\nhex: {}'.format(self._color, hex_color)
        )

    def get_value(self):
        return self._color[:4]
