from collections import deque

from algo.util import build_adj_list


class BFS:
    def __init__(self, v, e):
        self.v = v
        self.v_to_index = {v[i]: i for i in range(len(v))}
        self.visited = [0 for _ in range(len(v))]
        self.adj = build_adj_list(e)
        self.count = 0

    def bfs(self, v):
        self.count += 1
        self.mark(v, self.count)
        q = deque(v)
        while q:
            front = q.popleft()
            for w in self.adj[front]:
                if not self.is_visited(w):
                    self.count += 1
                    self.mark(w, self.count)
                    q.append(w)

    def mark(self, v, count):
        self.visited[self.v_to_index[v]] = count

    def is_visited(self, v):
        return self.visited[self.v_to_index[v]] != 0

    def order_of_visit(self):
        return sorted(self.v, key=lambda i: self.visited[self.v_to_index[i]])
