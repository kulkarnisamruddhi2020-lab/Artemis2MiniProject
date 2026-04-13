# Artemis2MiniProject
# 🚀 Artemis 2 Mission Simulation

A full-stack Python-based mission control simulation for the upcoming Artemis 2 lunar trajectory. This project simulates real-time orbital mission parameters, events, and telemetry by heavily utilizing advanced data structures. It features a fully interactive web dashboard to monitor the mission in real-time.

## ✨ Features

- **Mission Trajectory Mapping:** Implements a **Directed Weighted Graph** to map the nodes of the Artemis 2 flight path (e.g., Earth Orbit, Translunar Injection, Lunar Flyby).
- **Event Scheduling (DES):** Uses a **Priority Queue** for discrete event simulation, executing mission events sequentially based on priority and timing.
- **Emergency Abort System:** Employs **Dijkstra's Algorithm** to calculate the safest and fastest return trajectory back to Earth in the event of an abort scenario.
- **Mission Control Dashboard:** A **Flask-based** web interface that visualizes the trajectory, displays live telemetry feeds, and allows users to trigger simulations or abort sequences.

## 🛠️ Technologies & Data Structures Used

**Backend:** Python
**Web Framework:** Flask
**Frontend:** HTML, CSS, JavaScript (in `/static` and `/templates`)

**Core Data Structures:**
- `Graph` (Mission routing)
- `Priority Queue/Min-Heap` (Event management)
- `Dijkstra's Algorithm` (Abort pathfinding)
