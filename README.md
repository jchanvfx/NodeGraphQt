### NodeGraph Widget

This is a **_work in progress_** widget I'm working on in my spare time, as
a learning exercise to write a custom node graph in PySide.

NodeGraphQt is node graph widget that can be implemented and repurposed into applications that supports PySide.

![screencap01](https://raw.githubusercontent.com/jchanvfx/NodeGraphQt/master/example/screenshot.png)

#### Navigation:
Zoom in/out : `Right Mouse Click + Drag` or `Mouse Scroll Up`/`Mouse Scroll Down`<br/>
Pan scene : `Middle Mouse Click + Drag` or `Alt + Left Mouse Click + Drag`<br/>
Fit to screen : `F`

#### Shortcuts:
![screencap02](https://raw.githubusercontent.com/jchanvfx/NodeGraphQt/master/example/screenshot_menu.png)

Select all nodes : `Ctrl + A`<br/>
Delete selected node(s) : `Backspace` or `Delete`<br/>
Copy node(s): `Ctrl + C` _(copy to clipboard)_<br/>
Paste node(s): `Ctrl + V` _(paste from clipboard)_<br/>
Duplicate node(s) : `Alt + C`<br/>
Save node layout : `Ctrl + S`<br/>
Open node layout : `Ctrl + O` <br/>
undo action: `Ctrl+z` or `Command+z` _(OSX)_ <br/>
Redo action: `Ctrl+Shift+z` or `Command+Shift+z` _(OSX)_ <br/>
Toggle (enable/disable) node: `d`

#### Node Search
![screencap03](https://raw.githubusercontent.com/jchanvfx/NodeGraphQt/master/example/screenshot_tab_search.png)

Show node search: `Tab` <br/>
Create node from selected: `enter`

#### Example Snippet

[example script](https://github.com/jchanvfx/bpNodeGraph/blob/master/example.py)

```python
from NodeGraphQt import NodeGraphWidget, Node

# create a node object
class MyNode(Node):
    """example test node."""

    NODE_NAME = 'Test Node'

    def __init__(self):
        super(MyNode, self).__init__()
        self.add_input('foo')
        self.add_output('bar')

# create a node
my_node = MyNode()

# create node graph.
graph = NodeGraphWidget()

# register node into the node graph.
graph.register_node(MyNode)

# add node to the node graph.
graph.add_node(my_node)

graph.show()
```
