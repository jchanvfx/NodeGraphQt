Menus
#####

.. currentmodule:: NodeGraphQt

.. seealso::

    Context menus can also be set from a config file or a dictionary with:
    :meth:`NodeGraph.set_context_menu_from_file`, :meth:`NodeGraph.set_context_menu`

.. autosummary::
    NodeGraphMenu
    NodesMenu
    NodeGraphCommand

|

GraphMenu
*********

| The context menu triggered from the node graph.

.. autoclass:: NodeGraphMenu
    :members:
    :exclude-members: qmenu
    :member-order: bysource

|

NodesMenu
*********

| The context menu triggered from a node.

.. autoclass:: NodesMenu
    :members:
    :member-order: bysource

|

NodeGraphCommand
****************

.. autoclass:: NodeGraphCommand
    :members:
    :exclude-members: qaction
    :member-order: bysource
