Menus
#####

.. currentmodule:: NodeGraphQt

.. seealso::

    Context menus can also be set from a config file or a dictionary with:
    :meth:`NodeGraph.set_context_menu_from_file`, :meth:`NodeGraph.set_context_menu`


Graph Menu
**********

| The context menu triggered from the node graph.

.. autoclass:: NodeGraphMenu
    :members:
    :exclude-members: qmenu


Nodes Menu
**********

| The context menu triggered from a node.

.. autoclass:: NodesMenu
    :members:


Command
*******

.. autoclass:: NodeGraphCommand
    :members:
    :exclude-members: qaction
