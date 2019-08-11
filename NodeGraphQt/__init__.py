#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2017, Johnny Chan
# https://github.com/jchanvfx/NodeGraphQt

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# * Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.

# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.

# * Neither the name Johnny Chan nor the names of its contributors
#   may be used to endorse or promote products derived from this software
#   without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
# OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT
# OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

try:
    from Qt import QtWidgets, QtGui, QtCore, QtCompat
except ImportError as ie:
    from .vendor.Qt import __version__ as qtpy_ver
    from .vendor.Qt import QtWidgets, QtGui, QtCore, QtCompat
    print('Cannot import "Qt.py" module falling back on '
          '"NodeGraphQt.vendor.Qt ({})"'.format(qtpy_ver))

from .base.graph import NodeGraph
from .base.menu import Menu, MenuCommand
from .base.node import NodeObject, BaseNode, BackdropNode
from .base.port import Port
from .pkg_info import __version__ as VERSION

# functions
from .base.actions import setup_context_menu

# widgets
from .widgets.node_tree import NodeTreeWidget
from .widgets.properties_bin import PropertiesBinWidget

__version__ = VERSION
__all__ = [
    'BackdropNode', 'BaseNode', 'Menu', 'MenuCommand', 'NodeGraph',
    'NodeObject', 'NodeTreeWidget', 'Port', 'PropertiesBinWidget', 'VERSION',
    'constants', 'setup_context_menu'
]
