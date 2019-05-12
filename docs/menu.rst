Menus
*****

.. image:: _images/menu_hotkeys.png
    :width: 50%

The ``NodeGraphQt.setup_context_menu`` has a built in function that'll populate the node graphs context menu a few
default menus and commands.

.. code-block:: python
    :linenos:

    from NodeGraphQt import NodeGraph, setup_context_menu

    graph = NodeGraph()
    setup_context_menu(graph)

example adding "Foo" menu to the node graphs context menu.

.. code-block:: python
    :linenos:

    from NodeGraphQt import NodeGraph

    # create node graph.
    graph = NodeGraph()

    # get the main context menu.
    root_menu = graph.context_menu()

    # add a menu called "Foo".
    foo_menu = root_menu.add_menu('Foo')

add "Bar" command to the "Foo" menu.

.. code-block:: python
    :linenos:
    :lineno-start: 11

    # test function.
    def my_test():
        print('Hello World')

    # add "Bar" command to the "Foo" menu.
    foo_menu.add_command('Bar', my_test, 'Shift+t')

----

.. autofunction:: NodeGraphQt.setup_context_menu
    :noindex:




Menu
====

Node graph menu.


----

.. autoclass:: NodeGraphQt.Menu
    :members:


Command
=======

Node graph menu command.

----

.. autoclass:: NodeGraphQt.MenuCommand
    :members:
