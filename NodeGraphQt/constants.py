#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
from .pkg_info import __version__
from . import QtWidgets

#: Current version of the NodeGraphQt framework.
VERSION = __version__

# === PIPE ===

PIPE_WIDTH = 1.2
PIPE_STYLE_DEFAULT = 0
PIPE_STYLE_DASHED = 1
PIPE_STYLE_DOTTED = 2
PIPE_DEFAULT_COLOR = (175, 95, 30, 255)
PIPE_DISABLED_COLOR = (190, 20, 20, 255)
PIPE_ACTIVE_COLOR = (70, 255, 220, 255)
PIPE_HIGHLIGHT_COLOR = (232, 184, 13, 255)
PIPE_SLICER_COLOR = (255, 50, 75)
#: Style to draw the connection pipes as straight lines.
PIPE_LAYOUT_STRAIGHT = 0
#: Style to draw the connection pipes as curved lines.
PIPE_LAYOUT_CURVED = 1
#: Style to draw the connection pipes as angled lines.
PIPE_LAYOUT_ANGLE = 2

# === PORT ===

#: Connection type for input ports.
IN_PORT = 'in'
#: Connection type for output ports.
OUT_PORT = 'out'

PORT_DEFAULT_SIZE = 22.0
PORT_DEFAULT_COLOR = (49, 115, 100, 255)
PORT_DEFAULT_BORDER_COLOR = (29, 202, 151, 255)
PORT_ACTIVE_COLOR = (14, 45, 59, 255)
PORT_ACTIVE_BORDER_COLOR = (107, 166, 193, 255)
PORT_HOVER_COLOR = (17, 43, 82, 255)
PORT_HOVER_BORDER_COLOR = (136, 255, 35, 255)
PORT_FALLOFF = 15.0

# === NODE ===

NODE_WIDTH = 170
NODE_HEIGHT = 80
NODE_ICON_SIZE = 24
NODE_SEL_COLOR = (255, 255, 255, 30)
NODE_SEL_BORDER_COLOR = (254, 207, 42, 255)

# === NODE PROPERTY ===

#: Property type will hidden in the properties bin (default).
NODE_PROP = 0
#: Property type represented with a QLabel widget in the properties bin.
NODE_PROP_QLABEL = 2
#: Property type represented with a QLineEdit widget in the properties bin.
NODE_PROP_QLINEEDIT = 3
#: Property type represented with a QTextEdit widget in the properties bin.
NODE_PROP_QTEXTEDIT = 4
#: Property type represented with a QComboBox widget in the properties bin.
NODE_PROP_QCOMBO = 5
#: Property type represented with a QCheckBox widget in the properties bin.
NODE_PROP_QCHECKBOX = 6
#: Property type represented with a QSpinBox widget in the properties bin.
NODE_PROP_QSPINBOX = 7
#: Property type represented with a ColorPicker widget in the properties bin.
NODE_PROP_COLORPICKER = 8
#: Property type represented with a Slider widget in the properties bin.
NODE_PROP_SLIDER = 9
#: Property type represented with a file selector widget in the properties bin.
NODE_PROP_FILE = 10
#: Property type represented with a vector2 widget in the properties bin.
NODE_PROP_VECTOR2 = 11
#: Property type represented with vector3 widget in the properties bin.
NODE_PROP_VECTOR3 = 12
#: Property type represented with vector4 widget in the properties bin.
NODE_PROP_VECTOR4 = 13
#: Property type represented with float widget in the properties bin.
NODE_PROP_FLOAT = 14
#: Property type represented with int widget in the properties bin.
NODE_PROP_INT = 15
#: Property type represented with button widget in the properties bin.
NODE_PROP_BUTTON = 16

# === NODE VIEWER ===

VIEWER_BG_COLOR = (35, 35, 35)
VIEWER_GRID_COLOR = (45, 45, 45)
VIEWER_GRID_OVERLAY = True
VIEWER_GRID_SIZE = 20

DRAG_DROP_ID = 'n0deGraphQT'

# === PATHS ===

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
ICON_PATH = os.path.join(BASE_PATH, 'widgets', 'icons')
ICON_DOWN_ARROW = os.path.join(ICON_PATH, 'down_arrow.png')
ICON_NODE_BASE = os.path.join(ICON_PATH, 'node_base.png')

# === DRAW STACK ORDER ===

Z_VAL_PIPE = -1
Z_VAL_NODE = 1
Z_VAL_PORT = 2
Z_VAL_NODE_WIDGET = 3


# === ITEM CACHE MODE ===

# QGraphicsItem.NoCache
# QGraphicsItem.DeviceCoordinateCache
# QGraphicsItem.ItemCoordinateCache

ITEM_CACHE_MODE = QtWidgets.QGraphicsItem.DeviceCoordinateCache