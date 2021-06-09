from Qt import QtWidgets, QtCore, QtGui

from NodeGraphQt.constants import NODE_SEL_BORDER_COLOR


class NodeNavigationDelagate(QtWidgets.QStyledItemDelegate):

    def paint(self, painter, option, index):
        """
        Args:
            painter (QtGui.QPainter):
            option (QtGui.QStyleOptionViewItem):
            index (QtCore.QModelIndex):
        """
        if index.column() != 0:
            super(NodeNavigationDelagate, self).paint(painter, option, index)
            return

        item = index.model().item(index.row(), index.column())

        margin = 1.0, 1.0
        rect = QtCore.QRectF(
            option.rect.x() + margin[0],
            option.rect.y() + margin[1],
            option.rect.width() - (margin[0] * 2),
            option.rect.height() - (margin[1] * 2)
        )

        painter.save()
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtCore.Qt.NoBrush)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)

        # background.
        bg_color = option.palette.window().color()
        itm_color = QtGui.QColor(80, 128, 123)
        if option.state & QtWidgets.QStyle.State_Selected:
            bg_color = bg_color.lighter(120)
            itm_color = QtGui.QColor(*NODE_SEL_BORDER_COLOR)

        roundness = 2.0
        painter.setBrush(bg_color)
        painter.drawRoundedRect(rect, roundness, roundness)

        if index.row() != 0:
            m = 2.0
            h = rect.height()
            x, y = rect.left() + 2.0, rect.top()
            painter.setBrush(itm_color)
            for count in range(2):
                x += 2.8
                y += m
                h -= m * 2
                itm_rect = QtCore.QRectF(x, y, 1.3, h)
                painter.drawRoundedRect(itm_rect, 1.0, 1.0)
        else:
            x = rect.left() + 2.0
            size = 10.0
            for clr in [QtGui.QColor(0, 0, 0, 80), itm_color]:
                itm_rect = QtCore.QRectF(
                    x, rect.center().y() - (size / 2), size, size)
                painter.setBrush(clr)
                painter.drawRoundedRect(itm_rect, 2.0, 2.0)
                size -= 5.0
                x += 2.5

        # text
        pen_color = option.palette.text().color()
        pen = QtGui.QPen(pen_color, 0.5)
        pen.setCapStyle(QtCore.Qt.RoundCap)
        painter.setPen(pen)

        font = painter.font()
        font_metrics = QtGui.QFontMetrics(font)
        font_width = font_metrics.horizontalAdvance(
            item.text().replace(' ', '_')
        )
        font_height = font_metrics.height()
        text_rect = QtCore.QRectF(
            rect.center().x() - (font_width / 2) + 4.0,
            rect.center().y() - (font_height / 2),
            font_width, font_height)
        painter.drawText(text_rect, item.text())
        painter.restore()


class NodeNavigationWidget(QtWidgets.QListView):

    node_item_selected = QtCore.Signal(str, list)

    def __init__(self, parent=None):
        super(NodeNavigationWidget, self).__init__(parent)
        self.setSelectionMode(self.SingleSelection)
        self.setResizeMode(self.Adjust)
        self.setViewMode(self.ListMode)
        self.setFlow(self.LeftToRight)
        self.setDragEnabled(False)
        self.setMinimumHeight(20)
        self.setMaximumHeight(26)
        self.setSpacing(0)

        self.setItemDelegate(NodeNavigationDelagate(self))
        self.setModel(QtGui.QStandardItemModel())

        self.clicked.connect(self._on_item_clicked)

    def keyPressEvent(self, event):
        event.ignore()

    def _on_item_clicked(self, index):
        rows = reversed(range(1, self.model().rowCount()))
        if index.row() == 0:
            rows = [r for r in rows if r > 0]
        else:
            rows = [r for r in rows if index.row() < r]
        rm_node_ids = [self.model().item(r, 0).toolTip() for r in rows]
        node_id = self.model().item(index.row(), 0).toolTip()
        [self.model().removeRow(r) for r in rows]
        self.node_item_selected.emit(node_id, rm_node_ids)

    def clear(self):
        self.model().sourceMode().clear()

    def add_label_item(self, label, node_id):
        item = QtGui.QStandardItem(label)
        item.setToolTip(node_id)
        metrics = QtGui.QFontMetrics(item.font())
        width = metrics.horizontalAdvance(item.text()) + 26
        item.setSizeHint(QtCore.QSize(width, 20))
        self.model().appendRow(item)
        self.selectionModel().setCurrentIndex(
            self.model().indexFromItem(item),
            QtCore.QItemSelectionModel.ClearAndSelect)


if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)

    widget = NodeNavigationWidget()
    widget.add_label_item('Root', 'root')
    for i in range(1, 6):
        widget.add_label_item('group node {}'.format(i),
                              'node_id{}'.format(i))
    widget.show()

    app.exec_()
