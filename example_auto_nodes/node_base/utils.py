from NodeGraphQt import topological_sort_by_down, NodePublishWidget

# node stream update


def _update_nodes(nodes):
    for node in nodes:
        if node.disabled():
            continue
        node.cook()
        if node.has_error:
            break


def update_node_down_stream(nodes):
    if not isinstance(nodes, list):
        nodes = [nodes]
    _update_nodes(topological_sort_by_down(start_nodes=nodes))


def update_nodes(nodes):
    _update_nodes(topological_sort_by_down(all_nodes=nodes))


# node menu

def setup_node_menu(graph, published_node_class):
    from .auto_node import AutoNode
    from .subgraph_node import SubGraphNode

    node_menu = graph.context_nodes_menu()
    node_menu.add_command('Allow Edit', allow_edit, node_class=published_node_class)
    node_menu.add_command('Enter Node', enter_node, node_class=SubGraphNode)
    node_menu.add_command('Publish Node', publish_node, node_class=SubGraphNode)
    node_menu.add_command('Print Children', print_children, node_class=SubGraphNode)
    node_menu.add_command('Cook Node', cook_node, node_class=AutoNode)
    node_menu.add_command('Toggle Auto Cook', toggle_auto_cook, node_class=AutoNode)
    node_menu.add_command('Print Path', print_path, node_class=AutoNode)


def cook_node(graph, node):
    node.update_stream(forceCook=True)


def toggle_auto_cook(graph, node):
    node.auto_cook = not node.auto_cook


def enter_node(graph, node):
    graph.set_node_space(node)


def allow_edit(graph, node):
    node.set_property('published', False)


def print_path(graph, node):
    print(node.path())


def print_children(graph, node):
    children = node.children()
    print(len(children), children)


def publish_node(graph, node):
    wid = NodePublishWidget(node=node)
    wid.show()
