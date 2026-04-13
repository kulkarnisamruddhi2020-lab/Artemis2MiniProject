from data_structures.graph import Graph
from data_structures.event_queue import EventQueue
from data_structures.avl_tree import AVLTree

class SimulationEngine:
    def __init__(self):
        self.graph = Graph()
        self.event_queue = EventQueue()
        self.telemetry_db = AVLTree()
        self.current_time = 0.0
        
        self.aborted = False
        self.finished = False
        self._build_network()
        
        # Standard Mission Path
        self.mission_plan = [
            "Pad_39B", "LEO", "HEO", "TLI", "Lunar_Flyby", "Earth_Orbit", "Splashdown"
        ]
        self.current_stage_idx = 0
        
        # Schedule the first event
        start_node = self.mission_plan[0]
        self.event_queue.schedule_event(0.0, 'ARRIVE', {'node': start_node})

    def _build_network(self):
        # Normal Mission Edges (target, delta_v, time)
        self.graph.add_edge("Pad_39B", "LEO", 7800, 0.2)
        self.graph.add_edge("LEO", "HEO", 1500, 24)
        self.graph.add_edge("HEO", "TLI", 2500, 72)
        self.graph.add_edge("TLI", "Lunar_Flyby", 300, 96)
        self.graph.add_edge("Lunar_Flyby", "Earth_Orbit", 250, 90)
        
        # Abort Routes (Emergency trajectories)
        self.graph.add_edge("LEO", "Splashdown", 100, 2)
        self.graph.add_edge("HEO", "LEO", 1400, 12)
        self.graph.add_edge("HEO", "Splashdown", 1500, 14)
        self.graph.add_edge("TLI", "Earth_Orbit", 2400, 50)
        self.graph.add_edge("Earth_Orbit", "Splashdown", 200, 5)
        self.graph.add_edge("TLI", "Splashdown", 2500, 55) 
        self.graph.add_edge("Lunar_Flyby", "Splashdown", 40, 90)

    def get_stage_telemetry(self, stage):
        telemetry_map = {
            "Pad_39B": {"alt": 0, "vel": 0},
            "LEO": {"alt": 400, "vel": 7.66},
            "HEO": {"alt": 70000, "vel": 10.0},
            "TLI": {"alt": 380000, "vel": 11.0},
            "Lunar_Flyby": {"alt": 390000, "vel": 2.5},
            "Earth_Orbit": {"alt": 500, "vel": 8.0},
            "Splashdown": {"alt": 0, "vel": 0}
        }
        return telemetry_map.get(stage, {"alt": 0, "vel": 0})

    def step(self):
        """
        Processes the next event in the queue. 
        Returns dict containing state, or None if finished.
        """
        if self.finished or self.event_queue.is_empty():
            return None

        current_event = self.event_queue.next_event()
        self.current_time, event_type, data = current_event
        node = data['node']
        
        telemetry = self.get_stage_telemetry(node)
        telemetry['stage'] = node
        
        # Log to AVL Tree
        self.telemetry_db.insert(self.current_time, telemetry)
        
        if node == "Splashdown":
            self.finished = True
        else:
            # If not aborted, schedule next nominal step
            if not self.aborted:
                self.current_stage_idx += 1
                if self.current_stage_idx < len(self.mission_plan):
                    next_node = self.mission_plan[self.current_stage_idx]
                    edge = next((e for e in self.graph.nodes.get(node, []) if e.target == next_node), None)
                    if edge:
                        next_time = self.current_time + edge.time_cost
                        self.event_queue.schedule_event(next_time, 'ARRIVE', {'node': next_node})

        return {
            "timestamp": self.current_time,
            "node": node,
            "telemetry": telemetry,
            "status": "aborted" if self.aborted else ("finished" if self.finished else "nominal")
        }

    def trigger_abort(self, current_node):
        """
        Calculates Dijkstra shortest path back to Splashdown from current_node.
        Clears nominal events from PQ (not needed since step handles it)
        Enqueues abort events.
        """
        if self.aborted or self.finished:
            return None
            
        self.aborted = True
        self.event_queue.events = [] # Clear pending nominal steps
        
        path, total_time = self.graph.dijkstra_shortest_path(current_node, "Splashdown", weight_type='time')
        
        if not path:
            return None
            
        # Schedule the abort path events
        sim_time = self.current_time
        for i in range(len(path) - 1):
            curr_step = path[i]
            next_step = path[i+1]
            edge = next((e for e in self.graph.nodes.get(curr_step, []) if e.target == next_step), None)
            if edge:
                sim_time += edge.time_cost
                self.event_queue.schedule_event(sim_time, 'ARRIVE', {'node': next_step})
                
        return {
            "path": path,
            "total_time": total_time
        }
