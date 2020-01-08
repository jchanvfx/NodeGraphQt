NodeObject
##########

.. autoclass:: NodeGraphQt.NodeObject
    :members:
    :exclude-members: NODE_NAME, graph, id, model, type_, view

    .. autoattribute:: NODE_NAME
        :annotation:

        Initial base node name.

        .. note:: re-implement this attribute to provide a base node name.

        :return: node name
        :rtype: str

    .. autoattribute:: __identifier__
        :annotation:

        Unique node identifier domain. eg. ``"com.chantacticvfx"``

        .. note:: re-implement this attribute to provide a unique node type.

        :return: node identifer domain
        :rtype: str

    .. autoattribute:: graph
    .. autoattribute:: id
    .. autoattribute:: model
    .. autoattribute:: type_
        :annotation:

        Node type identifier followed by the class name. `eg.` ``"com.chantacticvfx.NodeObject"``

        :return: node type (``__identifier__.__className__``)
        :rtype: str

    .. autoattribute:: view
