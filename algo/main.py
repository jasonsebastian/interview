from algo.bfs import BFS
from algo.dfs import DFS

v = ['a', 'b', 'c', 'd', 'e', 'f']
e = [('a', 'c'), ('a', 'd'), ('a', 'e'), ('b', 'e'),
     ('b', 'f'), ('c', 'd'), ('c', 'f'), ('e', 'f')]

b = BFS(v, e)
for vertex in v:
    if not b.is_visited(vertex):
        b.bfs(vertex)
print(b.order_of_visit())

d = DFS(v, e)
for vertex in v:
    if not d.is_visited(vertex):
        d.dfs(vertex)
print(d.order_of_visit())
