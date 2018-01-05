### PySide Node Graph

This is a *work in progress* widget I'm working on in my spare time, as
a learning exercise on how to write a node graph in [PySide](http://pyside.github.io/docs/pyside/).

widget can be implemented and repurposed into applications that supports PySide.

![screencap01](https://raw.githubusercontent.com/jchanvfx/bpNodeGraph/master/screenshot.png)

[view example code](https://github.com/jchanvfx/bpNodeGraph/blob/master/example.py)

#### Navigation:
zoom in/out : `Right Mouse Click + Drag` or `Mouse Scroll Up`/`Mouse Scroll Down`<br/>
pan scene : `Middle Mouse Click + Drag` or `Alt + Left Mouse Click + Drag`<br/>
fit to screen : `F`

#### Shortcuts:
select all nodes : `Ctrl + A`<br/>
delete selected node(s) : `Backspace` or `Delete`<br/>
copy node(s): `Ctrl + C` _(copy to clipboard)_<br/>
paste node(s): `Ctrl + V` _(paste from clipboard)_<br/>
duplicate node(s) : `Alt + C`<br/>
save node layout : `Ctrl + S` <br/>
open node layout : `Ctrl + O` <br/>
layout saved in JSON format. (`.bpg` file ext) <br/>
undo action: `Ctrl+z` or `Command+z` _(OSX)_ <br/>
redo action: `Ctrl+Shift+z` or `Command+Shift+z` _(OSX)_