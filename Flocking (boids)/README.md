# Genetic Algorithm

*Project #15 – An experiment in evolutionary machine learning*

## Overview

This project uses a genetic algorithm to evolve autonomous agents that learn to survive inside a circular arena while avoiding a moving projectile ("lazer").

Each agent is controlled by two evolved weights:

* **w_lazer** – How strongly the agent avoids the lazer
* **w_border** – How strongly the agent avoids the arena boundary

Instead of manually programming a survival strategy, the population evolves over multiple generations. Agents that survive longer achieve higher fitness scores and are more likely to pass their genes to future generations through selection, crossover, and mutation.

---

## How It Works

### Agent Controller

Each frame, an agent calculates steering forces based on environmental inputs:

#### Lazer Avoidance

Agents steer away from the current lazer position. The closer the lazer gets, the stronger the avoidance force becomes.

#### Border Avoidance

Agents steer back toward the arena when approaching the boundary.

The final steering direction is determined by combining these forces using the agent's evolved weights.

---

## Fitness Function

Fitness is based entirely on survival time:

```python
fitness = survival_time * 0.5
```

Agents that survive longer are considered more successful and have a higher chance of contributing genes to future generations.

---

## Evolution Process

At the end of each generation:

1. Agents are ranked by fitness.
2. High-performing genes are preserved.
3. Parent genes are selected from the archive.
4. New offspring are created using crossover.
5. Random mutations introduce genetic diversity.
6. The next generation is spawned and evaluated.

Over time, the population evolves increasingly effective survival strategies.


## Update Log

### v1.0 – Initial Genetic Algorithm

* Added population-based evolution system
* Implemented fitness based on survival time
* Added archive system for preserving successful genes
* Implemented crossover and mutation

### v1.1 – Simplified Objective & Improved gene diversity

* Removed collision penalties
* Removed neighbor avoidance behavior
* Refocused training objective on projectile survival only
* Improved gene archive handling
* Added uniqueness checks during offspring generation (Prevents stagnation...mostly)
* Increased genetic diversity to reduce premature convergence

### Future Plans

* Variable movement speed
* Emergency dash mechanic with cooldown
* Additional environmental sensors
* More complex controllers (hidden-layer neural networks)
* Multiple projectiles and dynamic difficulty

---

## Technologies

* Python
* Pygame
* NumPy
* Pandas

---

## Running

Install dependencies:

```bash
pip install pygame numpy pandas
```

Run the simulation:

```bash
python main.py
```
