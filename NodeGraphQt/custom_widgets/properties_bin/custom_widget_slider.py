#!/usr/bin/python
from Qt import QtWidgets, QtCore

from .prop_widgets_abstract import BaseProperty


class PropSlider(BaseProperty):
    """
    Displays a node property as a "Slider" widget in the PropertiesBin
    widget.
    """

    def __init__(self, parent=None):
        super(PropSlider, self).__init__(parent)
        self._block = False
        self._slider = QtWidgets.QSlider()
        self._spinbox = QtWidgets.QSpinBox()
        self._init()

    def _init(self):
        self._slider.setOrientation(QtCore.Qt.Horizontal)
        self._slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self._slider.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Preferred)
        self._spinbox.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._spinbox)
        layout.addWidget(self._slider)
        self._spinbox.valueChanged.connect(self._on_spnbox_changed)
        self._slider.valueChanged.connect(self._on_slider_changed)
        # store the original press event.
        self._slider_mouse_press_event = self._slider.mousePressEvent
        self._slider.mousePressEvent = self._on_slider_mouse_press
        self._slider.mouseReleaseEvent = self._on_slider_mouse_release

    def _on_slider_mouse_press(self, event):
        self._block = True
        self._slider_mouse_press_event(event)

    def _on_slider_mouse_release(self, event):
        self.value_changed.emit(self.toolTip(), self.get_value())
        self._block = False

    def _on_slider_changed(self, value):
        self._spinbox.setValue(value)

    def _on_spnbox_changed(self, value):
        if value != self._slider.value():
            self._slider.setValue(value)
            if not self._block:
                self.value_changed.emit(self.toolTip(), self.get_value())

    def get_value(self):
        return self._spinbox.value()

    def set_value(self, value):
        if value != self.get_value():
            self._block = True
            self._spinbox.setValue(value)
            self.value_changed.emit(self.toolTip(), value)
            self._block = False

    def set_min(self, value=0):
        self._spinbox.setMinimum(value)
        self._slider.setMinimum(value)

    def set_max(self, value=0):
        self._spinbox.setMaximum(value)
        self._slider.setMaximum(value)
