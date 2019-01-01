Overview
********

NodeGraphQt is a node graph framework that can be implemented and repurposed into applications that supports ``PySide2``.

.. image:: _images/overview.png
    :width: 60%

Navigation
==========

+---------------+----------------------------------------------+
| action        | controls                                     |
+===============+==============================================+
| Zoom in/out   | *Alt + MMB + Drag* or *Mouse Scroll Up/Down* |
+---------------+----------------------------------------------+
| Pan           | *Alt + LMB + Drag* or *MMB + Drag*           |
+---------------+----------------------------------------------+

Tab Search
==========

.. image:: _images/node_search.png
    :width: 269px

Node can be created with the tab node search widget.

+-------------+--------+
| action      | hotkey |
+=============+========+
| Show Search | *Tab*  |
+-------------+--------+

.. note::
    To override the tab search widget hotkey see :ref:`NodeGraphQt.NodeGraph` class ``tab_search_key`` argument.

Context Menu Setup
==================

The ``NodeGraphQt`` module has a built in ``setup_context_menu`` function that'll populate the node graphs
context menu some default menus and commands.


see also: :ref:`Menu & Commands`

.. image:: _images/menu_hotkeys.png
    :width: 50%

----

.. autofunction:: NodeGraphQt.setup_context_menu