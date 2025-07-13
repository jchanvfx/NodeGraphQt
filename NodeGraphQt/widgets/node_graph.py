from Qt import QtWidgets, QtGui

from NodeGraphQt.constants import NodeEnum, ViewerEnum, ViewerNavEnum

from NodeGraphQt.widgets.viewer_nav import NodeNavigationWidget


class NodeGraphWidget(QtWidgets.QTabWidget):

    def __init__(self, parent=None):
        super(NodeGraphWidget, self).__init__(parent)
        self.setTabsClosable(True)
        self.setTabBarAutoHide(True)
        bg_color = QtGui.QColor(*ViewerEnum.BACKGROUND_COLOR.value).darker(120).getRgb()
        text_color = tuple(map(lambda i, j: i - j, (255, 255, 255), bg_color))
        style_dict = {
            "QWidget": {
                "color": "rgb({0},{1},{2})".format(*text_color),
                "background-color": "rgb({0},{1},{2})".format(
                    *ViewerEnum.BACKGROUND_COLOR.value
                ),
            },
            "QTabWidget::pane": {
                "background": "rgb({0},{1},{2})".format(
                    *ViewerEnum.BACKGROUND_COLOR.value
                ),
                "border": "0px",
                "border-top": "0px solid rgb({0},{1},{2})".format(*bg_color),
            },
            "QTabBar::tab": {
                "background": "rgb({0},{1},{2})".format(*bg_color),
                "border": "0px solid black",
                "color": "rgba({0},{1},{2},30)".format(*text_color),
                "min-width": "10px",
                "padding": "10px 20px",
            },
            "QTabBar::tab:selected": {
                "color": "rgb({0},{1},{2})".format(*text_color),
                "background": "rgb({0},{1},{2})".format(
                    *ViewerNavEnum.BACKGROUND_COLOR.value
                ),
                "border-top": "1px solid rgb({0},{1},{2})".format(
                    *NodeEnum.SELECTED_BORDER_COLOR.value
                ),
            },
            "QTabBar::tab:hover": {
                "color": "rgb({0},{1},{2})".format(*text_color),
                "border-top": "1px solid rgb({0},{1},{2})".format(
                    *NodeEnum.SELECTED_BORDER_COLOR.value
                ),
            },
            "QSpinBox": {
                "color": "rgb({0},{1},{2})".format(*text_color),
                "background-color": "rgb({0},{1},{2})".format(
                    *ViewerNavEnum.BACKGROUND_COLOR.value
                ),
                "min-width": "30px",
                "padding-right": "20px",
            },
            "QSpinBox QLineEdit": {
                "min-width": "20px",
            },
        }
        stylesheet = ""
        for css_class, css in style_dict.items():
            style = "{} {{\n".format(css_class)
            for elm_name, elm_val in css.items():
                style += "  {}:{};\n".format(elm_name, elm_val)
            style += "}\n"
            stylesheet += style

        self.setStyleSheet(stylesheet)

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
