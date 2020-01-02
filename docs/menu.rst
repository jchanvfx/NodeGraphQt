Menus
#####

.. image:: _images/menu_hotkeys.png
    :width: 50%


Here's an example where we add a ``"Foo"`` menu and then a ``"Bar"`` command with
the function ``my_test()`` registered.

.. code-block:: python
    :linenos:

    from NodeGraphQt import NodeGraph

    # test function.
    def my_test(graph):
        selected_nodes = graph.selected_nodes()
        print('Number of nodes selected: {}'.format(len(selected_nodes)))

    # create node graph.
    graph = NodeGraph()

    # get the main context menu.
    context_menu = node_graph.get_context_menu('graph')

    # add a menu called "Foo".
    foo_menu = context_menu.add_menu('Foo')

    # add "Bar" command to the "Foo" menu.
    # we also assign a short cut key "Shift+t" for this example.
    foo_menu.add_command('Bar', my_test, 'Shift+t')

----

The ``NodeGraphQt.setup_context_menu`` is a built in function that'll populate
the node graphs context menu a few default menus and commands.


.. autofunction:: NodeGraphQt.setup_context_menu
    :noindex:


NodeGraph Menu
**************

The context menu triggered from the node graph.

.. autoclass:: NodeGraphQt.NodeGraphMenu
    :members:


Nodes Menu
**********

The context menu triggered from a node.

.. autoclass:: NodeGraphQt.NodesMenu
    :members:


Command
*******

.. autoclass:: NodeGraphQt.NodeGraphCommand
    :members:
