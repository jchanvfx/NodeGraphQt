## NodeGraphQT

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE.md) 
[![PEP8](https://img.shields.io/badge/code%20style-pep8-green.svg)](https://www.python.org/dev/peps/pep-0008/) 
[![stability-wip](https://img.shields.io/badge/stability-work_in_progress-lightgrey.svg)](https://github.com/orangemug/stability-badges/blob/master/README.md)

This is a personal project I'm working on in my spare time, as a learning exercise for writing a custom node graph.

---

NodeGraphQt is a node graph framework that can be implemented and repurposed into 
applications that supports [PySide2](https://doc-snapshots.qt.io/qtforpython/).

![screencap01](/example/screenshot.png)

#### Requirements

- Python3, PySide2

#### Navigation Controls

| action        | controls                                     |
| ------------- |:--------------------------------------------:|
| Zoom in/out   | `Alt + MMB + Drag` or `Mouse Scroll Up/Down` |
| Pan           | `Alt + LMB + Drag` or `MMB + Drag`           |

#### Node Search
![screencap03](/example/screenshot_tab_search.png)

| action           | hotkey |
| ---------------- |:------:|
| Show node search | `Tab`  |

#### Context Menu
![screencap02](/example/screenshot_menu.png)

#### API Documentation

_currently unavaliable_

#### Example Code

```python
import sys
from PySide2 import QtWidgets
from NodeGraphQt import NodeGraph, Node, Backdrop

# create a example node object with a input/output port.
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
   
    # register backdrop node. (included in the NodeGraphQt module)
    graph.register_node(Backdrop)
   
    # register example node into the node graph.
    graph.register_node(MyNode)
   
    # create nodes.
    backdrop = graph.create_node('nodeGraphQt.nodes.Backdrop', name='Backdrop')
    node_a = graph.create_node('com.chantasticvfx.MyNode', name='Foo Node')
    node_b = graph.create_node('com.chantasticvfx.MyNode', name='Bar Node', color='#5b162f')
    
    # connect nodes.
    node_a.set_input(0, node_b.output(0))    

    # show widget.
    viewer = graph.viewer()
    viewer.show()

    app.exec_()
```

