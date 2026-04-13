from simulation_engine import SimulationEngine
from cli_console import Console

def main():
    Console.clear()
    engine = SimulationEngine()
    
    try:
        engine.run()
    except KeyboardInterrupt:
        Console.print_warning("\nSimulation forcefully interrupted.")
        
    # Telemetry Search Interface
    Console.print_header("Telemetry Database Archive (AVL Tree)")
    print("Search historical flight data stored dynamically. Retrieval operations are O(log n).")
    print("Timestamps are based on exact T+ times when milestones occurred.")
    
    while True:
        try:
            query = Console.input_prompt("\nEnter timestamp to search (T+ hours) or 'q' to quit: ")
            if query == 'q':
                print("Closing NASA uplink. Goodbye.")
                break
            
            ts = float(query)
            data = engine.telemetry_db.search(ts)
            
            if data:
                Console.print_log(ts, data['stage'], f"Alt: {data['alt']}km, Vel: {data['vel']}km/s")
            else:
                Console.print_warning(f"No telemetry data found for T+{ts:05.1f}h.")
        except ValueError:
            Console.print_error("Invalid input. Please enter a valid number (e.g., 0.0, 24.2).")

if __name__ == "__main__":
    main()
