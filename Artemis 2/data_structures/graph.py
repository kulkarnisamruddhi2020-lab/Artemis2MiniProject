import heapq

class Edge:
    def __init__(self, target, delta_v, time_cost):
        self.target = target
        self.delta_v = delta_v
        self.time_cost = time_cost

class Graph:
    def __init__(self):
        self.nodes = {}

    def add_node(self, node_name):
        if node_name not in self.nodes:
            self.nodes[node_name] = []

    def add_edge(self, source, target, delta_v, time_cost):
        self.add_node(source)
        self.add_node(target)
        self.nodes[source].append(Edge(target, delta_v, time_cost))

    def dijkstra_shortest_path(self, start, end, weight_type='time'):
        """
        Uses Dijkstra's algorithm to find the shortest path from start to end.
        weight_type can be 'time' or 'delta_v'
        """
        if start not in self.nodes or end not in self.nodes:
            return None, float('inf')

        # distances[node] = cost
        distances = {node: float('inf') for node in self.nodes}
        distances[start] = 0
        
        # previous_nodes[node] = prev_node for path reconstruction
        previous_nodes = {node: None for node in self.nodes}
        
        # Priority Queue: (cost, node)
        pq = [(0, start)]
        
        while pq:
            current_distance, current_node = heapq.heappop(pq)
            
            if current_distance > distances[current_node]:
                continue
                
            if current_node == end:
                break
                
            for edge in self.nodes[current_node]:
                cost = edge.time_cost if weight_type == 'time' else edge.delta_v
                distance = current_distance + cost
                
                if distance < distances[edge.target]:
                    distances[edge.target] = distance
                    previous_nodes[edge.target] = current_node
                    heapq.heappush(pq, (distance, edge.target))
                    
        # Reconstruct path
        path = []
        curr = end
        while curr is not None:
            path.append(curr)
            curr = previous_nodes[curr]
            
        path.reverse()
        if path[0] == start:
            return path, distances[end]
        return None, float('inf')
