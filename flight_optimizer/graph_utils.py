
def inverse_graph(graph):
    inv = {}

    for node, successors in graph.items():
        inv.setdefault(node, [])
        for succ in successors:
            inv.setdefault(succ, []).append(node)

    return inv