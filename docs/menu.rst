Menu & Commands
***************

Default Setup
=============

The ``NodeGraphQt`` module has a built in ``setup_context_menu`` function that'll populate the node graphs
context menu some default menus and commands.

.. image:: _images/menu_hotkeys.png
    :width: 50%

----

.. autofunction:: NodeGraphQt.setup_context_menu
    :noindex:

Example
=======

Here's a example where we a menu with the name "Foo" to the node graphs context menu.

.. code-block:: python
    :linenos:

    from NodeGraphQt import NodeGraph

    # create node graph.
    graph = NodeGraph()

    # get the main context menu.
    root_menu = graph.context_menu()

    # add a menu called "Foo".
    foo_menu = root_menu.add_menu('Foo')

and here we add a menu command with the name "Bar" to the "Foo" menu that will execute the ``my_test()`` method.

.. code-block:: python
    :linenos:
    :lineno-start: 11

    # test function.
    def my_test():
        print('Hello World')

    # add "Bar" command to the "Foo" menu.
    foo_menu.add_command('Bar', my_test, 'Shift+t')


Menu
====

Node graph context menu.


----

.. autoclass:: NodeGraphQt.Menu
    :members:


Command
=======

Node graph context menu command.

----

.. autoclass:: NodeGraphQt.MenuCommand
    :members:
