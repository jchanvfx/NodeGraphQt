#!/usr/bin/python
from Qt import QtWidgets, QtCore

from .prop_widgets_abstract import BaseProperty


class PropSlider(BaseProperty):
    """
    Displays a node property as a "Slider" widget in the PropertiesBin
    widget.
    """

    def __init__(self, parent=None, disable_scroll=True, realtime_update=False):
        super(PropSlider, self).__init__(parent)
        self._block = False
        self._realtime_update = realtime_update
        self._disable_scroll = disable_scroll
        self._slider = QtWidgets.QSlider()
        self._spinbox = QtWidgets.QSpinBox()
        self._init()
        self._init_signal_connections()

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
        # store the original press event.
        self._slider_mouse_press_event = self._slider.mousePressEvent
        self._slider.mousePressEvent = self._on_slider_mouse_press
        self._slider.mouseReleaseEvent = self._on_slider_mouse_release

        if self._disable_scroll:
            self._slider.wheelEvent = lambda _: None
            self._spinbox.wheelEvent = lambda _: None

    def _init_signal_connections(self):
        self._spinbox.valueChanged.connect(self._on_spnbox_changed)
        self._slider.valueChanged.connect(self._on_slider_changed)

    def _on_slider_mouse_press(self, event):
        self._block = True
        self._slider_mouse_press_event(event)

    def _on_slider_mouse_release(self, event):
        if not self._realtime_update:
            self.value_changed.emit(self.get_name(), self.get_value())
        self._block = False

    def _on_slider_changed(self, value):
        self._spinbox.setValue(value)
        if self._realtime_update:
            self.value_changed.emit(self.get_name(), self.get_value())

    def _on_spnbox_changed(self, value):
        if value != self._slider.value():
            self._slider.setValue(value)
            if not self._block:
                self.value_changed.emit(self.get_name(), self.get_value())

    def get_value(self):
        return self._spinbox.value()

    def set_value(self, value):
        if value != self.get_value():
            self._block = True
            self._spinbox.setValue(value)
            self.value_changed.emit(self.get_name(), value)
            self._block = False

    def set_min(self, value=0):
        self._spinbox.setMinimum(value)
        self._slider.setMinimum(value)

    def set_max(self, value=0):
        self._spinbox.setMaximum(value)
        self._slider.setMaximum(value)


class QDoubleSlider(QtWidgets.QSlider):
    double_value_changed = QtCore.Signal(float)

    def __init__(self, decimals=2, *args, **kargs):
        super(QDoubleSlider, self).__init__(*args, **kargs)
        self._multiplier = 10 ** decimals

        self.valueChanged.connect(self._on_value_change)

    def _on_value_change(self):
        value = float(super(QDoubleSlider, self).value()) / self._multiplier
        self.double_value_changed.emit(value)

    def value(self):
        return float(super(QDoubleSlider, self).value()) / self._multiplier

    def setMinimum(self, value):
        return super(QDoubleSlider, self).setMinimum(value * self._multiplier)

    def setMaximum(self, value):
        return super(QDoubleSlider, self).setMaximum(value * self._multiplier)

    def setSingleStep(self, value):
        return super(QDoubleSlider, self).setSingleStep(value * self._multiplier)

    def singleStep(self):
        return float(super(QDoubleSlider, self).singleStep()) / self._multiplier

    def setValue(self, value):
        super(QDoubleSlider, self).setValue(int(value * self._multiplier))


class PropDoubleSlider(PropSlider):
    def __init__(self, parent=None, decimals=2, disable_scroll=True, realtime_update=False):
        # Do not initialize Propslider, just its parents
        super(PropSlider, self).__init__(parent)
        self._block = False
        self._realtime_update = realtime_update
        self._disable_scroll = disable_scroll
        self._slider = QDoubleSlider(decimals=decimals)
        self._spinbox = QtWidgets.QDoubleSpinBox()
        self._init()
        self._init_signal_connections()

    def _init_signal_connections(self):
        self._spinbox.valueChanged.connect(self._on_spnbox_changed)
        # Connect to double_value_changed instead valueChanged
        self._slider.double_value_changed.connect(self._on_slider_changed)
