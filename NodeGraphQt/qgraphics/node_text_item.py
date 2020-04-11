from .. import QtWidgets, QtCore


class NodeTextItem(QtWidgets.QGraphicsTextItem):
    editingFinished = QtCore.Signal(str)

    def __init__(self, text, parent=None):
        super(NodeTextItem, self).__init__(text, parent)
        self.setFlags(QtWidgets.QGraphicsItem.ItemIsFocusable)
        self.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        self.isEditing = False

    def _editingFinished(self):
        if self.isEditing:
            self.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
            self.isEditing = False
            self.editingFinished.emit(self.toPlainText())

    def mousePressEvent(self, event):
        self.setTextInteractionFlags(QtCore.Qt.TextEditable)
        self.isEditing = True
        super(NodeTextItem, self).mousePressEvent(event)

    def focusOutEvent(self, event):
        self._editingFinished()
        super(NodeTextItem, self).focusOutEvent(event)

    def keyPressEvent(self, event):
        if event.key() is QtCore.Qt.Key_Return:
            self._editingFinished()
        super(NodeTextItem, self).keyPressEvent(event)