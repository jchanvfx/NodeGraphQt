from Qt import QtWidgets
from NodeGraphQt.widgets.viewer_nav import NodeNavigationWidget


class NodeGraphWidget(QtWidgets.QTabWidget):

    def __init__(self, parent=None):
        super(NodeGraphWidget, self).__init__(parent)
        self.setTabsClosable(True)
        self.setTabBarAutoHide(True)

    def add_viewer(self, viewer, name, node_id):
        self.addTab(viewer, name)
        index = self.indexOf(viewer)
        self.setTabToolTip(index, node_id)
        self.setCurrentIndex(index)

    def remove_viewer(self, viewer):
        index = self.indexOf(viewer)
        self.removeTab(index)


class SubGraphWidget(QtWidgets.QWidget):

    def __init__(self, parent=None, graph=None):
        super(SubGraphWidget, self).__init__(parent)
        self._graph = graph
        self._navigator = NodeNavigationWidget()
        self._layout = QtWidgets.QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(1)
        self._layout.addWidget(self._navigator)

        self._viewer_widgets = {}
        self._viewer_current = None

    @property
    def navigator(self):
        return self._navigator

    def add_viewer(self, viewer, name, node_id):
        if viewer in self._viewer_widgets:
            return

        if self._viewer_current:
            self.hide_viewer(self._viewer_current)

        self._navigator.add_label_item(name, node_id)
        self._layout.addWidget(viewer)
        self._viewer_widgets[viewer] = node_id
        self._viewer_current = viewer
        self._viewer_current.show()

    def remove_viewer(self, viewer=None):
        if viewer is None and self._viewer_current:
            viewer = self._viewer_current
        node_id = self._viewer_widgets.pop(viewer)
        self._navigator.remove_label_item(node_id)
        self._layout.removeWidget(viewer)
        viewer.deleteLater()

    def hide_viewer(self, viewer):
        self._layout.removeWidget(viewer)
        viewer.hide()

    def show_viewer(self, viewer):
        if viewer == self._viewer_current:
            self._viewer_current.show()
            return
        if viewer in self._viewer_widgets:
            if self._viewer_current:
                self.hide_viewer(self._viewer_current)
            self._layout.addWidget(viewer)
            self._viewer_current = viewer
            self._viewer_current.show()
