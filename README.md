# Overlook — Agent-Based Model

**Blake Peterman — DIGIT 430**

An agent-based simulation exploring how human politeness and "personal bubbles" create an **Artificial Capacity Ceiling** at a scenic overlook. Three agent types compete for 10 railing slots, driven by a seeded Stochastic Decision Engine.

## Agents

| Type | Behavior |
|------|----------|
| **Photographer** | Camps any empty slot for 5–15 min. Ignores neighbours. |
| **Viewer** | Needs ≤1 occupied neighbour. Rolls patience each tick when crowded — leaves if it breaks. |
| **Socializer** | Picks the empty slot with the most occupied neighbours. Stays for a normally-distributed duration. |

## How It Works

- Agents arrive via a **Poisson distribution** (λ = 2/tick)
- Each agent type is equally likely (33%)
- A seeded **PRNG** ensures identical runs for reproducibility
- When the railing gets congested, incoming agents form **phantom queues** with escalating abandonment probability
- Slots that stay crowded long enough become **Social Dead Zones** that Viewers permanently avoid

## Running

```bash
pip install -r Documentation/requirements.txt
python overlook_abm.py
```

A live matplotlib window will open. Each tick is 1 real-world second, displayed as "Minutes" in the top-left.

## Project Structure

```
overlook_abm.py        Entry point
config.py              All tunables (seed, arrival rate, thresholds, etc.)
Code/
  agents.py            Agent base class + Photographer, Viewer, Socializer
  environment.py       Overlook railing + waiting area + dead zones
  simulation.py        Tick loop, spawning, placement, queue processing
  visualization.py     Live matplotlib dashboard
Documentation/
  requirements.txt     Python dependencies
```

## Configuration

Edit `config.py` to tweak the simulation. Key knobs:

| Parameter | Default | What it does |
|-----------|---------|-------------|
| `SEED` | 42 | PRNG seed |
| `SIM_DURATION` | 120 | Total ticks |
| `ARRIVAL_LAMBDA` | 2.0 | Avg. new agents per tick |
| `VIEWER_PATIENCE_THRESHOLD` | 0.5 | Per-tick leave probability when crowded |
| `PATH_CONGESTION_THRESHOLD` | 7 | Occupied slots that trigger phantom queues |
| `TICK_INTERVAL_MS` | 100 | Real-time ms between ticks |
