#!/usr/bin/python
from Qt import QtWidgets, QtCore, QtGui


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

    valueChanged = QtCore.Signal(object)

    def __init__(self, parent=None, data_type=float):
        super(_NumberValueEdit, self).__init__(parent)
        self.setToolTip('"MMB + Drag Left/Right" to change values.')
        self.setText('0')

        self._MMB_STATE = False
        self._previous_x = None
        self._previous_value = None
        self._step = 1
        self._speed = 0.1
        self._data_type = float

        self._menu = _NumberValueMenu()
        self._menu.mouseMove.connect(self.mouseMoveEvent)
        self._menu.mouseRelease.connect(self.mouseReleaseEvent)
        self._menu.stepChange.connect(self._reset_previous_x)
        self._menu.set_steps([0.001, 0.01, 0.1, 1, 10, 100, 1000])

        self.editingFinished.connect(self._on_text_changed)

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
                self._on_text_changed()
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

    # private

    def _reset_previous_x(self):
        self._previous_x = None

    def _on_text_changed(self):
        self.valueChanged.emit(self.get_value())

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

    # public

    def set_data_type(self, data_type):
        self._data_type = data_type
        self._menu.set_data_type(data_type)
        if data_type is int:
            self.setValidator(QtGui.QIntValidator())
        elif data_type is float:
            self.setValidator(QtGui.QDoubleValidator())

    def set_steps(self, steps=None):
        steps = steps or [0.001, 0.01, 0.1, 1, 10, 100, 1000]
        self._menu.set_steps(steps)

    def get_value(self):
        if self.text().startswith('.'):
            text = '0' + self.text()
            self.setText(text)
        return self._convert_text(self.text())

    def set_value(self, value):
        if value != self.get_value():
            self.setText(str(self._convert_text(value)))


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
