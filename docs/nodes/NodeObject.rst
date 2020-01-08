NodeObject
##########

.. autoclass:: NodeGraphQt.NodeObject
    :members:
    :exclude-members: NODE_NAME, graph, id, model, type_, view

    .. autoattribute:: NODE_NAME
        :annotation: = (re-implementation required)

        Initial base node name.

        :return: node name
        :rtype: str

    .. autoattribute:: __identifier__
        :annotation: = (re-implementation required)

        Unique node identifier domain. eg. ``"com.chantacticvfx"``

        :return: node identifer domain
        :rtype: str

    .. autoattribute:: graph
    .. autoattribute:: id
    .. autoattribute:: model
    .. autoattribute:: type_
        :annotation: = (__identifier__.__className__)

        Node type identifier followed by the class name. `eg.` ``"com.chantacticvfx.NodeObject"``

        :return: node type
        :rtype: str

    .. autoattribute:: view
