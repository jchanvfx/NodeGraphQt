Menu Examples
#############

Examples for customizing context menus in NodeGraphQt.

Default Menu Setup
******************

The NodeGraphQt module has a convenience function for setting up the node graph
with a few essential menu commands.

`See function:` :func:`NodeGraphQt.setup_context_menu`

.. image:: ../_images/menu_hotkeys.png
    :width: 300px

Adding to the Graph Menu
************************

The ``"graph"`` menu is the main context menu from the NodeGraph object, below
is an example where we add a ``"Foo"`` menu and then a ``"Bar"`` command with
the registered ``my_test()`` function.

.. code-block:: python
    :linenos:

    from NodeGraphQt import NodeGraph

    # test function.
    def my_test(graph):
        selected_nodes = graph.selected_nodes()
        print('Number of nodes selected: {}'.format(len(selected_nodes)))

    # create node graph.
    node_graph = NodeGraph()

    # get the main context menu.
    context_menu = node_graph.get_context_menu('graph')

    # add a menu called "Foo".
    foo_menu = context_menu.add_menu('Foo')

    # add "Bar" command to the "Foo" menu.
    # we also assign a short cut key "Shift+t" for this example.
    foo_menu.add_command('Bar', my_test, 'Shift+t')

Adding to the Nodes Menu
************************

Aside from the main context menu, the NodeGraph also has a nodes menu where you
can override context menus on a per node type basis.

Below is an example for overriding a context menu for the node type ``"com.chantasticvfx.FooNode"``

.. code-block:: python
    :linenos:

    from NodeGraphQt import BaseNode, NodeGraph, setup_context_menu

    # define a couple example nodes.
    class FooNode(BaseNode):

        __identifier__ = 'com.chantasticvfx'
        NODE_NAME = 'foo node'

        def __init__(self):
            super(FooNode, self).__init__()
            self.add_input('in')
            self.add_output('out')

    class BarNode(FooNode):

        NODE_NAME = 'bar node'

    # define a test function.
    def test_func(graph, node):
        print('Clicked on node: {}'.format(node.name()))

    # create node graph and register node classes.
    node_graph = NodeGraph()
    node_graph.register_node(FooNode)
    node_graph.register_node(BarNode)

    # set up default menu commands.
    setup_context_menu(node_graph)

    # get the nodes menu.
    nodes_menu = node_graph.get_context_menu('nodes')

    # here we add override the context menu for "com.chantasticvfx.FooNode".
    nodes_menu.add_command('Test',
                           func=test_func,
                           node_type='com.chantasticvfx.FooNode')

    # create some nodes.
    foo_node = graph.create_node('com.chantasticvfx.FooNode')
    bar_node = graph.create_node('com.chantasticvfx.BarNode', pos=[300, 100])

    # show widget.
    node_graph.widget.show()