#!/usr/bin/python
# -*- coding: utf-8 -*-
import os

from Qt import QtWidgets
from enum import Enum

from .pkg_info import __version__ as _v

__doc__ = """
| The :py:mod:`NodeGraphQt.constants` namespace contains variables and enums 
 used throughout the NodeGraphQt library.
"""

# ================================== PRIVATE ===================================

URI_SCHEME = 'nodegraphqt://'
URN_SCHEME = 'nodegraphqt::'

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

# === NODE LAYOUT DIRECTION ===

#: Mode for vertical node layout.
NODE_LAYOUT_VERTICAL = 0
#: Mode for horizontal node layout.
NODE_LAYOUT_HORIZONTAL = 1
#: Variable for setting the node layout direction.
# NODE_LAYOUT_DIRECTION = NODE_LAYOUT_VERTICAL
NODE_LAYOUT_DIRECTION = NODE_LAYOUT_HORIZONTAL

# =================================== GLOBAL ===================================


class VersionEnum(Enum):
    """
    Current framework version.
    :py:mod:`NodeGraphQt.constants.VersionEnum`
    """
    #:
    VERSION = _v
    #:
    MAJOR = int(_v.split('.')[0])
    #:
    MINOR = int(_v.split('.')[1])
    #:
    PATCH = int(_v.split('.')[2])

# =================================== VIEWER ===================================


class ViewerEnum(Enum):
    """
    Node graph viewer styling layout:
    :py:mod:`NodeGraphQt.constants.ViewerEnum`
    """
    #: default background color for the node graph.
    BACKGROUND_COLOR = (35, 35, 35)
    #: style node graph background with no grid or dots.
    GRID_DISPLAY_NONE = 0
    #: style node graph background with dots.
    GRID_DISPLAY_DOTS = 1
    #: style node graph background with grid lines.
    GRID_DISPLAY_LINES = 2
    #: grid size when styled with grid lines.
    GRID_SIZE = 50
    #: grid line color.
    GRID_COLOR = (45, 45, 45)


class ViewerNavEnum(Enum):
    """
    Node graph viewer navigation styling layout:
    :py:mod:`NodeGraphQt.constants.ViewerNavEnum`
    """
    #: default background color.
    BACKGROUND_COLOR = (25, 25, 25)
    #: default item color.
    ITEM_COLOR = (35, 35, 35)

# ==================================== NODE ====================================


class NodeEnum(Enum):
    """
    Node styling layout:
    :py:mod:`NodeGraphQt.constants.NodeEnum`
    """
    #: default node width.
    WIDTH = 160
    #: default node height.
    HEIGHT = 60
    #: default node icon size (WxH).
    ICON_SIZE = 18
    #: default node overlay color when selected.
    SELECTED_COLOR = (255, 255, 255, 30)
    #: default node border color when selected.
    SELECTED_BORDER_COLOR = (254, 207, 42, 255)

# ==================================== PORT ====================================


class PortEnum(Enum):
    """
    Port styling layout:
    :py:mod:`NodeGraphQt.constants.PortEnum`
    """
    #: default port size.
    SIZE = 22.0
    #: default port color. (r, g, b, a)
    COLOR = (49, 115, 100, 255)
    #: default port border color.
    BORDER_COLOR = (29, 202, 151, 255)
    #: port color when selected.
    ACTIVE_COLOR = (14, 45, 59, 255)
    #: port border color when selected.
    ACTIVE_BORDER_COLOR = (107, 166, 193, 255)
    #: port color on mouse over.
    HOVER_COLOR = (17, 43, 82, 255)
    #: port border color on mouse over.
    HOVER_BORDER_COLOR = (136, 255, 35, 255)
    #: threshold for selecting a port.
    CLICK_FALLOFF = 15.0


class PortTypeEnum(Enum):
    """
    Port connection types:
    :py:mod:`NodeGraphQt.constants.PortTypeEnum`
    """
    #: Connection type for input ports.
    IN = 'in'
    #: Connection type for output ports.
    OUT = 'out'

# ==================================== PIPE ====================================


class PipeEnum(Enum):
    """
    Pipe styling layout:
    :py:mod:`NodeGraphQt.constants.PipeEnum`
    """
    #: default width.
    WIDTH = 1.2
    #: default color.
    COLOR = (175, 95, 30, 255)
    #: pipe color to a node when it's disabled.
    DISABLED_COLOR = (190, 20, 20, 255)
    #: pipe color when selected or mouse over.
    ACTIVE_COLOR = (70, 255, 220, 255)
    #: pipe color to a node when it's selected.
    HIGHLIGHT_COLOR = (232, 184, 13, 255)
    #: draw connection as a line.
    DRAW_TYPE_DEFAULT = 0
    #: draw connection as dashed lines.
    DRAW_TYPE_DASHED = 1
    #: draw connection as a dotted line.
    DRAW_TYPE_DOTTED = 2


class PipeSlicerEnum(Enum):
    """
    Slicer Pipe styling layout:
    :py:mod:`NodeGraphQt.constants.PipeSlicerEnum`
    """
    #: default width.
    WIDTH = 1.5
    #: default color.
    COLOR = (255, 50, 75)


class PipeLayoutEnum(Enum):
    """
    Pipe connection drawing layout:
    :py:mod:`NodeGraphQt.constants.PipeLayoutEnum`
    """
    #: draw straight lines for pipe connections.
    STRAIGHT = 0
    #: draw curved lines for pipe connections.
    CURVED = 1
    #: draw angled lines for pipe connections.
    ANGLE = 2


# === PROPERTY BIN WIDGET ===

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
#: Property type represented with a file save widget in the properties bin.
NODE_PROP_FILE_SAVE = 11
#: Property type represented with a vector2 widget in the properties bin.
NODE_PROP_VECTOR2 = 12
#: Property type represented with vector3 widget in the properties bin.
NODE_PROP_VECTOR3 = 13
#: Property type represented with vector4 widget in the properties bin.
NODE_PROP_VECTOR4 = 14
#: Property type represented with float widget in the properties bin.
NODE_PROP_FLOAT = 15
#: Property type represented with int widget in the properties bin.
NODE_PROP_INT = 16
#: Property type represented with button widget in the properties bin.
NODE_PROP_BUTTON = 17
