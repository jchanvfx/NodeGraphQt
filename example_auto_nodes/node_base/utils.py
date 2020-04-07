from NodeGraphQt import topological_sort_by_down


def _update_nodes(nodes):
    for node in nodes:
        if node.disabled():
            node.when_disabled()
        else:
            node.cook()
        if node.error():
            break


def update_node_down_stream(node):
    _update_nodes(topological_sort_by_down(start_nodes=[node]))


def update_nodes(nodes):
    _update_nodes(topological_sort_by_down(all_nodes=nodes))
