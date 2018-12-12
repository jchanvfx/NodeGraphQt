Menus
*****

example.

.. code-block:: python
    :linenos:

    from NodeGraphQt import NodeGraph

    # create node graph.
    graph = NodeGraph()

    # get the main context menu.
    root_menu = graph.context_menu()

    # add "Foo" menu.
    foo_menu = root_menu.add_menu('Foo')

    # add "Bar" command to the "Foo" menu.
    foo_menu.add_command('Bar', test, 'Shift+t')



ContextMenu
===========

Node graph context menu.


----

.. autoclass:: NodeGraphQt.ContextMenu
    :members:


ContextMenuCommand
==================

Node graph context menu command.

----

.. autoclass:: NodeGraphQt.ContextMenuCommand
    :members:
