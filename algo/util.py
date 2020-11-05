def build_adj_list(e):
    def add_key_value(v, w):
        if v not in adj:
            adj[v] = [w]
        else:
            adj[v].append(w)

    adj = {}
    for edge in e:
        v1, v2 = edge[0], edge[1]
        add_key_value(v1, v2)
        add_key_value(v2, v1)
    return adj
