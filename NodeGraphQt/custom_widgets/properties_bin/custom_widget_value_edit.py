#!/usr/bin/python
import re

from Qt import QtWidgets, QtCore, QtGui

_NUMB_REGEX = re.compile(r'^((?:\-)*\d+)*([\.,])*(\d+(?:[eE](?:[\-\+])*\d+)*)*')


class _NumberValueMenu(QtWidgets.QMenu):

    mouseMove = QtCore.Signal(object)
    mouseRelease = QtCore.Signal(object)
    stepChange = QtCore.Signal()

    def __init__(self, parent=None):
        super(_NumberValueMenu, self).__init__(parent)
        self.step = 1
        self.steps = []
        self.last_action = None

    def __repr__(self):
        return '<{}() object at {}>'.format(
            self.__class__.__name__, hex(id(self)))

    # re-implemented.

    def mousePressEvent(self, event):
        """
        Disabling the mouse press event.
        """
        return

    def mouseReleaseEvent(self, event):
        """
        Additional functionality to emit signal.
        """
        self.mouseRelease.emit(event)
        super(_NumberValueMenu, self).mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        """
        Additional functionality to emit step changed signal.
        """
        self.mouseMove.emit(event)
        super(_NumberValueMenu, self).mouseMoveEvent(event)
        action = self.actionAt(event.pos())
        if action:
            if action is not self.last_action:
                self.stepChange.emit()
            self.last_action = action
            self.step = action.step
        elif self.last_action:
            self.setActiveAction(self.last_action)

    def _add_step_action(self, step):
        action = QtWidgets.QAction(str(step), self)
        action.step = step
        self.addAction(action)

    def set_steps(self, steps):
        self.clear()
        self.steps = steps
        for step in steps:
            self._add_step_action(step)

    def set_data_type(self, data_type):
        if data_type is int:
            new_steps = []
            for step in self.steps:
                if '.' not in str(step):
                    new_steps.append(step)
            self.set_steps(new_steps)
        elif data_type is float:
            self.set_steps(self.steps)


class _NumberValueEdit(QtWidgets.QLineEdit):

    value_changed = QtCore.Signal(object)

    def __init__(self, parent=None, data_type=float):
        super(_NumberValueEdit, self).__init__(parent)
        self.setToolTip('"MMB + Drag Left/Right" to change values.')
        self.setText('0')

        self._MMB_STATE = False
        self._previous_x = None
        self._previous_value = None
        self._step = 1
        self._speed = 0.05
        self._data_type = float
        self._min = None
        self._max = None

        self._menu = _NumberValueMenu()
        self._menu.mouseMove.connect(self.mouseMoveEvent)
        self._menu.mouseRelease.connect(self.mouseReleaseEvent)
        self._menu.stepChange.connect(self._reset_previous_x)

        self.editingFinished.connect(self._on_editing_finished)

        self.set_data_type(data_type)

    def __repr__(self):
        return '<{}() object at {}>'.format(
            self.__class__.__name__, hex(id(self)))

    # re-implemented

    def mouseMoveEvent(self, event):
        if self._MMB_STATE:
            if self._previous_x is None:
                self._previous_x = event.x()
                self._previous_value = self.get_value()
            else:
                self._step = self._menu.step
                delta = event.x() - self._previous_x
                value = self._previous_value
                value = value + int(delta * self._speed) * self._step
                self.set_value(value)
                self._on_mmb_mouse_move()
        super(_NumberValueEdit, self).mouseMoveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MiddleButton:
            self._MMB_STATE = True
            self._reset_previous_x()
            self._menu.exec_(QtGui.QCursor.pos())
        super(_NumberValueEdit, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self._menu.close()
        self._MMB_STATE = False
        super(_NumberValueEdit, self).mouseReleaseEvent(event)

    def keyPressEvent(self, event):
        super(_NumberValueEdit, self).keyPressEvent(event)
        if event.key() == QtCore.Qt.Key_Up:
            return
        elif event.key() == QtCore.Qt.Key_Down:
            return

    def set_name(self, name):
        self._name = name

    # private

    def _reset_previous_x(self):
        self._previous_x = None

    def _on_mmb_mouse_move(self):
        self.value_changed.emit(self.get_value())

    def _on_editing_finished(self):
        if self._data_type is float:
            match = _NUMB_REGEX.match(self.text())
            if match:
                val1, point, val2 = match.groups()
                if point:
                    val1 = val1 or '0'
                    val2 = val2 or '0'
                    self.setText(val1 + point + val2)
        self.value_changed.emit(self.get_value())

    def _convert_text(self, text):
        """
        Convert text to int or float.

        Args:
            text (str): input text.

        Returns:
            int or float: converted value.
        """
        match = _NUMB_REGEX.match(text)
        if match:
            val1, _, val2 = match.groups()
            val1 = val1 or '0'
            val2 = val2 or '0'
            value = float(val1 + '.' + val2)
        else:
            value = 0.0
        if self._data_type is int:
            value = int(value)
        return value

    # public

    def set_data_type(self, data_type):
        """
        Sets the line edit to either display value in float or int.

        Args:
            data_type(int or float): int or float data type object.
        """
        self._data_type = data_type
        if data_type is int:
            regexp = QtCore.QRegExp(r'\d+')
            validator = QtGui.QRegExpValidator(regexp, self)
            steps = [1, 10, 100, 1000]
            self._min = None if self._min is None else int(self._min)
            self._max = None if self._max is None else int(self._max)
        elif data_type is float:
            regexp = QtCore.QRegExp(r'\d+[\.,]\d+(?:[eE](?:[\-\+]|)\d+)*')
            validator = QtGui.QRegExpValidator(regexp, self)
            steps = [0.001, 0.01, 0.1, 1]
            self._min = None if self._min is None else float(self._min)
            self._max = None if self._max is None else float(self._max)

        self.setValidator(validator)
        if not self._menu.steps:
            self._menu.set_steps(steps)
        self._menu.set_data_type(data_type)

    def set_steps(self, steps=None):
        """
        Sets the step items in the MMB context menu.

        Args:
            steps (list[int] or list[float]): list of ints or floats.
        """
        step_types = {
            int: [1, 10, 100, 1000],
            float: [0.001, 0.01, 0.1, 1]
        }
        steps = steps or step_types.get(self._data_type)
        self._menu.set_steps(steps)

    def set_min(self, value=None):
        """
        Set the minimum range for the input field.

        Args:
            value (int or float): minimum range value.
        """
        if self._data_type is int:
            self._min = int(value)
        elif self._data_type is float:
            self._min = float(value)
        else:
            self._min = value

    def set_max(self, value=None):
        """
        Set the maximum range for the input field.

        Args:
            value (int or float): maximum range value.
        """
        if self._data_type is int:
            self._max = int(value)
        elif self._data_type is float:
            self._max = float(value)
        else:
            self._max = value

    def get_value(self):
        value = self._convert_text(self.text())
        return value

    def set_value(self, value):
        text = str(value)
        converted = self._convert_text(text)
        current = self.get_value()
        if converted == current:
            return
        point = None
        if isinstance(converted, float):
            point = _NUMB_REGEX.match(str(value)).groups(2)
        if self._min is not None and converted < self._min:
            text = str(self._min)
            if point and point not in text:
                text = str(self._min).replace('.', point)
        if self._max is not None and converted > self._max:
            text = str(self._max)
            if point and point not in text:
                text = text.replace('.', point)
        self.setText(text)


class IntValueEdit(_NumberValueEdit):

    def __init__(self, parent=None):
        super(IntValueEdit, self).__init__(parent, data_type=int)


class FloatValueEdit(_NumberValueEdit):

    def __init__(self, parent=None):
        super(FloatValueEdit, self).__init__(parent, data_type=float)


if __name__ == '__main__':
    app = QtWidgets.QApplication([])

    int_edit = IntValueEdit()
    int_edit.set_steps([1, 10])
    float_edit = FloatValueEdit()

    widget = QtWidgets.QWidget()
    layout = QtWidgets.QVBoxLayout(widget)
    layout.addWidget(int_edit)
    layout.addWidget(float_edit)
    widget.show()

    app.exec_()
