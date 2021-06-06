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
            for i in range(3):
                x += 2.8
                y += m
                h -= m * 2
                itm_rect = QtCore.QRectF(x, y, 1.3, h)
                painter.drawRoundedRect(itm_rect, 1.0, 1.0)
        else:
            size = 10.0
            for clr in [QtGui.QColor(0, 0, 0, 80), itm_color]:
                itm_rect = QtCore.QRectF(rect.center().x() - (size / 2),
                                         rect.center().y() - (size / 2),
                                         size, size)
                painter.setBrush(clr)
                painter.drawRoundedRect(itm_rect, 2.0, 2.0)
                size -= 5.0

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
            rect.center().x() - (font_width / 2) + 5.0,
            rect.center().y() - (font_height / 2),
            font_width, font_height)
        painter.drawText(text_rect, item.text())
        painter.restore()


class NodeNavigationWidget(QtWidgets.QListView):

    def __init__(self, parent=None):
        super(NodeNavigationWidget, self).__init__(parent)
        self.setSelectionMode(self.SingleSelection)
        self.setDragEnabled(False)
        self.setResizeMode(self.Adjust)
        self.setViewMode(self.ListMode)
        self.setFlow(self.LeftToRight)
        self.setMinimumHeight(20)
        self.setMaximumHeight(26)
        self.setSpacing(0)

        self.setItemDelegate(NodeNavigationDelagate(self))
        self.setModel(QtGui.QStandardItemModel())

    def clear(self):
        self.model().sourceMode().clear()

    def add_item(self, label):
        width = 20
        item = QtGui.QStandardItem(label)
        if label:
            metrics = QtGui.QFontMetrics(item.font())
            width = metrics.horizontalAdvance(item.text()) + 28
        item.setSizeHint(QtCore.QSize(width, 20))
        self.model().appendRow(item)


if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)

    widget = NodeNavigationWidget()
    widget.show()

    app.exec_()
