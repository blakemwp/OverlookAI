# Overlook — Agent-Based Model

**Blake Peterman — DIGIT 430**

An agent-based simulation exploring how human politeness and "personal bubbles" create an **Artificial Capacity Ceiling** at a scenic overlook. Three agent types compete for 30 railing slots, driven by a seeded Stochastic Decision Engine.

## Agents

| Type | Behavior |
|------|----------|
| **Photographer** | Camps any empty slot for 5–15 min. Ignores neighbours. |
| **Viewer** | Needs ≤1 occupied neighbour. Rolls patience each tick when crowded — leaves if it breaks. |
| **Socializer** | Picks the empty slot with the most occupied neighbours. Stays for a normally-distributed duration. |

When more than one slot ties for "most preferred" under an agent's rule, the choice is broken **uniformly at random** so the rail doesn't develop a left-edge bias.

## How It Works

- Agents arrive via a **Poisson distribution** (λ = 2/tick)
- Each agent type is equally likely (33%)
- A seeded **PRNG** (seed = 42) ensures reproducible runs
- When the railing fills up (or when Viewers can't find a sparse-enough slot), incoming agents form **phantom queues** with escalating abandonment probability
- Slots that stay crowded long enough become **Social Dead Zones** that Viewers permanently avoid
- The **Artificial Capacity Ceiling** is *emergent*: no rule hardcodes an upper limit, yet steady-state occupancy stabilizes well below the 30-slot physical capacity because Viewers actively flee crowds

## Running

### Python (matplotlib dashboard)

```bash
pip install -r Documentation/requirements.txt
python overlook_abm.py
```

A live matplotlib window will open. Each tick is 1 real-world second, displayed as "Minutes" in the top-left.

### NetLogo (browser or desktop)

The model is also provided as a NetLogo translation in `NetLogo/Overlook.nls`. Open NetLogo (Web or Desktop), paste the contents into the **Code** tab, click **Check**, then add a `setup` button and a forever `go` button on the Interface tab. Setup → Go and the world view auto-resizes to display the rail and waiting area.

The two implementations are **functionally equivalent** — same parameters, same agent rules, same statistical behavior — but not bit-identical (NetLogo uses Mersenne Twister, NumPy uses PCG64; same seed produces different exact streams).

## Project Structure

```
overlook_abm.py        Python entry point
config.py              All tunables (seed, arrival rate, dwell times, etc.)
Code/
  agents.py            Agent base class + Photographer, Viewer, Socializer
  environment.py       Overlook railing + waiting area + dead zones
  simulation.py        Tick loop, spawning, placement, queue processing
  visualization.py     Live matplotlib dashboard
NetLogo/
  Overlook.nls         NetLogo port (paste into the Code tab)
Documentation/
  requirements.txt     Python dependencies
  *.pdf, *.png         Design docs and assignment artifacts
```

## Configuration

Edit `config.py` to tweak the simulation. Key knobs:

| Parameter | Default | What it does |
|-----------|---------|-------------|
| `SEED` | 42 | PRNG seed |
| `NUM_SLOTS` | 30 | Railing length (physical capacity) |
| `SIM_DURATION` | 120 | Total ticks |
| `ARRIVAL_LAMBDA` | 2.0 | Avg. new agents per tick |
| `VIEWER_PATIENCE_THRESHOLD` | 0.5 | Per-tick leave probability when crowded |
| `QUEUE_ABANDON_BASE` | 0.05 | Base per-tick abandonment in waiting area |
| `QUEUE_ABANDON_GROWTH` | 0.02 | Additional abandonment per tick already waited |
| `DEAD_ZONE_DENSITY_TICKS` | 10 | Consecutive crowded ticks needed to mark a slot dead |
| `DEAD_ZONE_NEIGHBOR_MIN` | 2 | Neighbours required for a slot to count as crowded |
| `TICK_INTERVAL_MS` | 100 | Real-time ms between ticks |

The same values are mirrored at the top of `setup` in `NetLogo/Overlook.nls` — change them in both places to keep the two implementations aligned.
