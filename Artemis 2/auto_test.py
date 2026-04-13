from simulation_engine import SimulationEngine
from cli_console import Console

# We can hijack the user input to run an automated test
def mock_input(prompt):
    # Print the prompt to simulate console
    print(f"\n[MOCK INPUT] {prompt}")
    
    # Trigger an abort specifically at High Earth Orbit (HEO)
    if "HEO" in prompt:
        print("-> 'y' (ABORT INITIATED)")
        return "y"
    
    # Anything else, just continue nominal path
    print("-> 'n' (Nominal proceed)")
    return "n"

def run_automated_test():
    Console.input_prompt = mock_input  # Override the interactive prompt
    
    engine = SimulationEngine()
    
    print("\n--- STARTING AUTOMATED SIMULATION TEST ---")
    engine.run()
    print("--- SIMULATION FINISHED ---\n")
    
    # Verify the AVL Tree telemetry data manually
    print("\n--- VERIFYING Telemetry in AVL Tree (Search Demo) ---")
    
    # We know Pad_39B happens at T+0.0h
    ts_pad = 0.0
    val1 = engine.telemetry_db.search(ts_pad)
    print(f"Search for timestamp {ts_pad}h -> Stage: {val1['stage'] if val1 else 'Not found'}, Alt: {val1['alt']}km")

    # LEO happens at T+0.2h
    ts_leo = 0.2
    val2 = engine.telemetry_db.search(ts_leo)
    print(f"Search for timestamp {ts_leo}h -> Stage: {val2['stage'] if val2 else 'Not found'}, Alt: {val2['alt']}km")

    # HEO happens at T+24.2h
    ts_heo = 24.2
    val3 = engine.telemetry_db.search(ts_heo)
    print(f"Search for timestamp {ts_heo}h -> Stage: {val3['stage'] if val3 else 'Not found'}, Alt: {val3['alt']}km")


if __name__ == "__main__":
    run_automated_test()
