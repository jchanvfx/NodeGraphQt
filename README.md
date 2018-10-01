### NodeGraph Widget

This is a **_work in progress_** widget I'm working on in my spare time, as
a learning exercise to write a custom node graph with PySide2.

NodeGraphQt is node graph widget that can be implemented and repurposed into applications that supports PySide2.

![screencap01](https://raw.githubusercontent.com/jchanvfx/NodeGraphQt/master/example/screenshot.png)

#### Navigation

| action        | controls                               |
| ------------- |:--------------------------------------:|
| Zoom in/out   | `RMB + Drag` or `Mouse Scroll Up/Down` |
| Pan           | `RMB + Drag` or `Alt + LMB + Drag`     |

#### Node Search
![screencap03](https://raw.githubusercontent.com/jchanvfx/NodeGraphQt/master/example/screenshot_tab_search.png)

| action           | hotkey |
| ---------------- |:------:|
| Show node search | `Tab`  |

#### Context Menu
![screencap02](https://raw.githubusercontent.com/jchanvfx/NodeGraphQt/master/example/screenshot_menu.png)

#### Example

```python
import sys
from PySide2 import QtWidgets
from NodeGraphQt import NodeGraph, Node

# create node object

class MyNode(Node):
    """example test node."""

    # unique node identifier.
    __identifier__ = 'com.chantasticvfx'

    # initial default node name.
    NODE_NAME = 'Test Node'

    def __init__(self):
        super(MyNode, self).__init__()
        self.add_input('foo')
        self.add_output('bar')
        
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    # create the main node graph controller.
    graph = NodeGraph()
   
    # register node into the node graph.
    graph.register_node(MyNode)
   
    # create nodes.
    node_a = graph.create_node('com.chantasticvfx.MyNode', name='Foo Node')
    node_b = graph.create_node('com.chantasticvfx.MyNode', name='Bar Node', color='#5b162f')
    
    # connect nodes.
    node_a.set_input(0, node_b.output(0))    

    # show the viewer widget.
    graph_widget = graph.viewer()
    graph_widget.show()

    app.exec_()
```
