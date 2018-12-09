## NodeGraphQT

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE.md) 
[![PEP8](https://img.shields.io/badge/code%20style-pep8-green.svg)](https://www.python.org/dev/peps/pep-0008/) 
[![stability-wip](https://img.shields.io/badge/stability-work_in_progress-lightgrey.svg)](https://github.com/orangemug/stability-badges/blob/master/README.md)

This is a personal project as a learning exercise into writing a custom node graph frame work. 
It is still very much in a work in progress stage as I'm only working on in my spare time.

---

NodeGraphQt is a node graph framework that can be implemented and repurposed into 
applications that supports [PySide2](https://doc-snapshots.qt.io/qtforpython/).

![screencap01](/docs/_images/screenshot.png)


#### Documentation

http://chantasticvfx.com/nodeGraphQt/html/index.html

#### Navigation

| action        | controls                                     |
| ------------- |:--------------------------------------------:|
| Zoom in/out   | `Alt + MMB + Drag` or `Mouse Scroll Up/Down` |
| Pan           | `Alt + LMB + Drag` or `MMB + Drag`           |

#### Node Search
![screencap03](/docs/_images/node_search.png)

| action           | hotkey |
| ---------------- |:------:|
| Show node search | `Tab`  |

#### Context Menu
![screencap02](/docs/_images/menu_hotkeys.png)

#### Example Code

```python
import sys
from PySide2 import QtWidgets
from NodeGraphQt import NodeGraph, Node, Backdrop

# create a example node object with a input/output port.
class MyNode(Node):
    """example test node."""

    # unique node identifier domain. ("com.chantasticvfx.MyNode")
    __identifier__ = 'com.chantasticvfx'

    # initial default node name.
    NODE_NAME = 'My Node'

    def __init__(self):
        super(MyNode, self).__init__()
        self.add_input('foo')
        self.add_output('bar')


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    # create the node graph controller.
    graph = NodeGraph()
   
    # register backdrop node. (included in the NodeGraphQt module)
    graph.register_node(Backdrop)
   
    # register example node into the node graph.
    graph.register_node(MyNode)
   
    # create nodes.
    backdrop = graph.create_node('nodeGraphQt.nodes.Backdrop', name='Backdrop')
    node_a = graph.create_node('com.chantasticvfx.MyNode', name='Node A')
    node_b = graph.create_node('com.chantasticvfx.MyNode', name='Node B', color='#5b162f')
    
    # connect node a input to node b output.
    node_a.set_input(0, node_b.output(0))    

    # show widget.
    viewer = graph.viewer()
    viewer.show()

    app.exec_()
```

