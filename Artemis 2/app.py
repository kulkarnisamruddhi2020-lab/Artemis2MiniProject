from flask import Flask, jsonify, request, render_template
from simulation_engine import SimulationEngine

app = Flask(__name__, template_folder="templates", static_folder="static")
engine = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/simulation/reset', methods=['POST'])
def reset_simulation():
    global engine
    engine = SimulationEngine()
    return jsonify({"status": "success", "message": "Simulation Reset"})

@app.route('/api/simulation/step', methods=['POST'])
def step_simulation():
    global engine
    if not engine:
        return jsonify({"error": "Simulation not initialized"}), 400
        
    state = engine.step()
    if state is None:
        return jsonify({"status": "finished", "message": "Simulation ended."})
        
    return jsonify({"status": "success", "state": state})

@app.route('/api/simulation/abort', methods=['POST'])
def abort_simulation():
    global engine
    if not engine or engine.finished:
        return jsonify({"error": "Cannot abort"}), 400
        
    data = request.json
    current_node = data.get('current_node')
    
    abort_info = engine.trigger_abort(current_node)
    if not abort_info:
        return jsonify({"error": "No abort trajectory found"}), 404
        
    return jsonify({"status": "success", "abort_info": abort_info})

@app.route('/api/telemetry/search', methods=['GET'])
def search_telemetry():
    global engine
    if not engine:
        return jsonify({"error": "Simulation not initialized"}), 400
        
    timestamp = request.args.get('timestamp', '0')
    
    # Custom parser to handle weird inputs like "24.56.43" or "74.53.90"
    try:
        ts = float(timestamp)
    except ValueError:
        clean = ""
        dot_seen = False
        for char in timestamp:
            if char.isdigit():
                clean += char
            elif char in '.:' and not dot_seen:
                clean += '.'
                dot_seen = True
        
        if not clean or clean == '.':
            ts = 0.0
        else:
            ts = float(clean)

    result = engine.telemetry_db.search(ts)
    if result:
        return jsonify({"status": "success", "data": result})
        
    return jsonify({"status": "not_found"}), 404

@app.route('/api/graph/config', methods=['GET'])
def graph_config():
    # Return nodes config with x, y coords for frontend visualizer
    nodes = {
        "Pad_39B": {"x": 50, "y": 300, "label": "Earth Launch Pad"},
        "LEO": {"x": 200, "y": 250, "label": "Low Earth Orbit"},
        "HEO": {"x": 350, "y": 200, "label": "High Earth Orbit"},
        "Earth_Orbit": {"x": 200, "y": 350, "label": "Earth Orbit Return"},
        "TLI": {"x": 550, "y": 150, "label": "Translunar Injection"},
        "Lunar_Flyby": {"x": 750, "y": 300, "label": "Lunar Flyby"},
        "Splashdown": {"x": 100, "y": 450, "label": "Splashdown Target"}
    }
    
    # We will let the frontend draw lines based on what's active.
    # We can also supply all edges.
    edges = []
    if engine:
        for source, es in engine.graph.nodes.items():
            for e in es:
                edges.append({
                    "source": source,
                    "target": e.target,
                    "delta_v": e.delta_v,
                    "time": e.time_cost
                })
                
    return jsonify({"nodes": nodes, "edges": edges})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
