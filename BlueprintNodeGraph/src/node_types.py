_REGISTERED_NODES = []
_REGISTERED_NODES_TYPES = {}


def register_node(node):
    global _REGISTERED_NODES
    if node not in _REGISTERED_NODES:
        _REGISTERED_NODES.append(node)


def registered_nodes():
    global _REGISTERED_NODES_TYPES
    if not _REGISTERED_NODES_TYPES:
        _REGISTERED_NODES_TYPES = {n().type(): n for n in _REGISTERED_NODES}
    return _REGISTERED_NODES_TYPES


def get_registered_nodes(node_type=None):
    if not node_type:
        return
    if not _REGISTERED_NODES_TYPES:
        registered_nodes()
    for n_type, n_obj in _REGISTERED_NODES_TYPES.items():
        if n_type == node_type:
            return n_obj
