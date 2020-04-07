from PySide2 import QtWidgets, QtGui, QtCore


class text_item(QtWidgets.QGraphicsTextItem):
    editingFinished = QtCore.Signal(str)

    def __init__(self, text, parent=None):
        super(text_item, self).__init__(text, parent)
        self.setFlags(QtWidgets.QGraphicsItem.ItemIsFocusable)
        self.setTextInteractionFlags(QtGui.Qt.NoTextInteraction)
        self.isEditing = False

    def _editingFinished(self):
        if self.isEditing:
            self.setTextInteractionFlags(QtGui.Qt.NoTextInteraction)
            self.isEditing = False
            self.editingFinished.emit(self.toPlainText())

    def mousePressEvent(self, event):
        self.setTextInteractionFlags(QtGui.Qt.TextEditable)
        self.isEditing = True
        super(text_item, self).mousePressEvent(event)

    def focusOutEvent(self, event):
        self._editingFinished()
        super(text_item, self).focusOutEvent(event)

    def keyPressEvent(self, event):
        if event.key() is QtGui.Qt.Key_Return:
            self._editingFinished()
        super(text_item, self).keyPressEvent(event)