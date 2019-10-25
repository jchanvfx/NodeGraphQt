# Example of Using NodeGraphQt with QtDesigner

NodeGraphQt’s widgets can be included in Designer’s ui files via the “Promote To...” functionality:

1. In Designer, create a QGraphicsView widget (“Graphics View” under the “Display Widgets” category).
2. Right-click on the QGraphicsView and select “Promote To...”.
3. Under “Promoted class name”, enter "NodeViewer".
4. Under “Header file”, enter “NodeGraphQt.widgets.viewer”.
5. Click “Add”, then click “Promote”.

See the QtDesigner's documentation for more information on promoting widgets. 

Then in your GUI init, you can use it like normal!

```python
class GUI(QtWidgets.QMainWindow, Ui_MainWindow):

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.log = logging.getLogger("proto.gui")
        self.setupUi(self)
        self.connect_actions()
        self.console.setVisible(True)
        self.showMaximized()

        self.graph = NodeGraph(view=self.graphicsView)
        setup_context_menu(self.graph)
        self.graph.register_node(BackdropNode)
        self.graph.register_node(BaseNode)

        # Add two nodes by default
        backdrop = self.graph.create_node('nodeGraphQt.nodes.BackdropNode', name='BackdropNode')
        base = self.graph.create_node('nodeGraphQt.nodes.BaseNode', name='BaseNode')

    def connect_actions(self):
        self.actionAddNode.triggered.connect(self.add_node)

    def add_node(self):
        self.graph.create_node('nodeGraphQt.nodes.BaseNode', name="Node")
```
