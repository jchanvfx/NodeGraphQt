Menu & Commands
***************

example to adding a menu and command.

.. code-block:: python
    :linenos:

    from NodeGraphQt import NodeGraph

    # test function.
    def my_test_func():
        print('Hello World')

    # create node graph.
    graph = NodeGraph()

    # get the main context menu.
    root_menu = graph.context_menu()

    # add "Foo" menu.
    foo_menu = root_menu.add_menu('Foo')

    # add "Bar" command to the "Foo" menu.
    foo_menu.add_command('Bar', my_test_func, 'Shift+t')



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
