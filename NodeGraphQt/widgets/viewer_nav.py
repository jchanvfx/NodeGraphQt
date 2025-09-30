from Qt import QtCore, QtGui, QtWidgets

from NodeGraphQt.constants import NodeEnum, ViewerNavEnum


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
        bg_color = QtGui.QColor(*ViewerNavEnum.ITEM_COLOR.value)
        itm_color = QtGui.QColor(80, 128, 123)
        if option.state & QtWidgets.QStyle.State_Selected:
            bg_color = bg_color.lighter(120)
            itm_color = QtGui.QColor(*NodeEnum.SELECTED_BORDER_COLOR.value)

        roundness = 2.0
        painter.setBrush(bg_color)
        painter.drawRoundedRect(rect, roundness, roundness)

        if index.row() != 0:
            txt_offset = 8.0
            m = 6.0
            x = rect.left() + 2.0 + m
            y = rect.top() + m + 2
            h = rect.height() - (m * 2) - 2
            painter.setBrush(itm_color)
            for i in range(4):
                itm_rect = QtCore.QRectF(x, y, 1.3, h)
                painter.drawRoundedRect(itm_rect, 1.0, 1.0)
                x += 2.0
                y += 2
                h -= 4
        else:
            txt_offset = 5.0
            x = rect.left() + 4.0
            size = 10.0
            for clr in [QtGui.QColor(0, 0, 0, 80), itm_color]:
                itm_rect = QtCore.QRectF(
                    x, rect.center().y() - (size / 2), size, size)
                painter.setBrush(clr)
                painter.drawRoundedRect(itm_rect, 2.0, 2.0)
                size -= 5.0
                x += 2.5

        # text
        # pen_color = option.palette.text().color()
        pen_color = QtGui.QColor(*tuple(map(
            lambda i, j: i - j, (255, 255, 255), bg_color.getRgb()
        )))
        pen = QtGui.QPen(pen_color, 0.5)
        pen.setCapStyle(QtCore.Qt.RoundCap)
        painter.setPen(pen)

        font = painter.font()
        font_metrics = QtGui.QFontMetrics(font)
        item_text = item.text().replace(' ', '_')
        if hasattr(font_metrics, 'horizontalAdvance'):
            font_width = font_metrics.horizontalAdvance(item_text)
        else:
            font_width = font_metrics.width(item_text)
        font_height = font_metrics.height()
        text_rect = QtCore.QRectF(
            rect.center().x() - (font_width / 2) + txt_offset,
            rect.center().y() - (font_height / 2),
            font_width, font_height
        )
        painter.drawText(text_rect, item.text())
        painter.restore()


class NodeNavigationWidget(QtWidgets.QListView):

    navigation_changed = QtCore.Signal(str, list)

    def __init__(self, parent=None):
        super(NodeNavigationWidget, self).__init__(parent)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.setResizeMode(QtWidgets.QListView.Adjust)
        self.setViewMode(QtWidgets.QListView.ListMode)
        self.setFlow(QtWidgets.QListView.LeftToRight)
        self.setDragEnabled(False)
        self.setMinimumHeight(20)
        self.setMaximumHeight(36)
        self.setSpacing(0)

        # self.viewport().setAutoFillBackground(False)
        self.setStyleSheet(
            'QListView {{border: 0px;background-color: rgb({0},{1},{2});}}'
            .format(*ViewerNavEnum.BACKGROUND_COLOR.value)
        )

        self.setItemDelegate(NodeNavigationDelagate(self))
        self.setModel(QtGui.QStandardItemModel())

    def keyPressEvent(self, event):
        event.ignore()

    def mouseReleaseEvent(self, event):
        super(NodeNavigationWidget, self).mouseReleaseEvent(event)
        if not self.selectedIndexes():
            return
        index = self.selectedIndexes()[0]
        rows = reversed(range(1, self.model().rowCount()))
        if index.row() == 0:
            rows = [r for r in rows if r > 0]
        else:
            rows = [r for r in rows if index.row() < r]
        if not rows:
            return
        rm_node_ids = [self.model().item(r, 0).toolTip() for r in rows]
        node_id = self.model().item(index.row(), 0).toolTip()
        [self.model().removeRow(r) for r in rows]
        self.navigation_changed.emit(node_id, rm_node_ids)

    def clear(self):
        self.model().sourceMode().clear()

    def add_label_item(self, label, node_id):
        item = QtGui.QStandardItem(label)
        item.setToolTip(node_id)
        metrics = QtGui.QFontMetrics(item.font())
        if hasattr(metrics, 'horizontalAdvance'):
            width = metrics.horizontalAdvance(item.text())
        else:
            width = metrics.width(item.text())
        width *= 1.5
        item.setSizeHint(QtCore.QSize(width, 20))
        self.model().appendRow(item)
        self.selectionModel().setCurrentIndex(
            self.model().indexFromItem(item),
            QtCore.QItemSelectionModel.ClearAndSelect)

    def update_label_item(self, label, node_id):
        rows = reversed(range(self.model().rowCount()))
        for r in rows:
            item = self.model().item(r, 0)
            if item.toolTip() == node_id:
                item.setText(label)

    def remove_label_item(self, node_id):
        rows = reversed(range(1, self.model().rowCount()))
        node_ids = [self.model().item(r, 0).toolTip() for r in rows]
        if node_id not in node_ids:
            return
        index = node_ids.index(node_id)
        if index == 0:
            rows = [r for r in rows if r > 0]
        else:
            rows = [r for r in rows if index < r]
        [self.model().removeRow(r) for r in rows]


if __name__ == '__main__':
    import sys

    def on_nav_changed(selected_id, remove_ids):
        print(selected_id, remove_ids)

    app = QtWidgets.QApplication(sys.argv)

    widget = NodeNavigationWidget()
    widget.navigation_changed.connect(on_nav_changed)

    widget.add_label_item('Close Graph', 'root')
    for i in range(1, 5):
        widget.add_label_item(
            'group node {}'.format(i),
            'node_id{}'.format(i)
        )
    widget.resize(600, 30)
    widget.show()

    app.exec_()
