## NodeGraphQt

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE.md) 
[![python 3.7+](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://www.python.org/downloads/)
[![PEP8](https://img.shields.io/badge/code%20style-PEP8-green.svg)](https://www.python.org/dev/peps/pep-0008/) 
[![stability-wip](https://img.shields.io/badge/stability-Work_In_Progress-lightgrey.svg)](https://github.com/orangemug/stability-badges/blob/master/README.md)

*(Note: this project is a work in progress and not production ready.)*

---

NodeGraphQt is a node graph framework that can be implemented and re purposed into 
applications that supports PySide2.

<img src="/docs/_images/screenshot.png" width="100%" title="NodeGraphQt">

#### Documentation

<a href="https://jchanvfx.github.io/NodeGraphQt">NodeGraphQt Documentation</a>

#### Navigation

| action        | controls                                   |
| ------------- |:------------------------------------------:|
| Zoom in/out   | `Alt + MMB Drag` or `Mouse Scroll Up/Down` |
| Pan           | `Alt + LMB Drag` or `MMB Drag`             |
| Node search   | `Tab`                                      |

#### Slice Connections

<img src="/docs/_images/slicer.png" width="500" title="Pipe Slicer">

| action            | controls                 |
| ----------------- |:------------------------:|
| Slice Connections | `Shift + Alt + LMB Drag` |

#### Properties Bin
<img src="/docs/_images/prop_bin.png" width="600" title="Properties Bin">

#### Example

```python
import sys

from NodeGraphQt import QtWidgets
from NodeGraphQt import NodeGraph, BaseNode, BackdropNode, setup_context_menu

# create a example node object with a input/output port.
class MyNode(BaseNode):
    """example test node."""

    # unique node identifier domain. ("com.chantasticvfx.MyNode")
    __identifier__ = 'com.chantasticvfx'

    # initial default node name.
    NODE_NAME = 'My Node'

    def __init__(self):
        super(MyNode, self).__init__()
        self.add_input('foo', color=(180, 80, 0))
        self.add_output('bar')


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    # create the node graph controller.
    graph = NodeGraph()
    
    # set up default menu and commands.
    setup_context_menu(graph)
   
    # register backdrop node. (included in the NodeGraphQt module)
    graph.register_node(BackdropNode)
   
    # register example node into the node graph.
    graph.register_node(MyNode)
   
    # create nodes.
    backdrop = graph.create_node('nodeGraphQt.nodes.Backdrop', name='Backdrop')
    node_a = graph.create_node('com.chantasticvfx.MyNode', name='Node A')
    node_b = graph.create_node('com.chantasticvfx.MyNode', name='Node B', color='#5b162f')
    
    # connect node a input to node b output.
    node_a.set_input(0, node_b.output(0))    

    # get the widget and show.
    graph_widget = graph.widget
    graph_widget.show()

    app.exec_()
```

