from collections import deque
import numpy as np

from Code.agents import Agent, Photographer, Viewer, Socializer
from Code.environment import Overlook
from config import (
    SEED, SIM_DURATION, ARRIVAL_LAMBDA,
    VIEWER_PATIENCE_THRESHOLD,
    QUEUE_ABANDON_BASE, QUEUE_ABANDON_GROWTH,
)

# heatmap encodes: 0=empty, 1=photographer, 2=viewer, 3=socializer
_TYPE_CODE = {
    type(None):   0,
    Photographer: 1,
    Viewer:       2,
    Socializer:   3,
}


class Simulation:
    def __init__(self, seed: int = SEED):
        self.rng = np.random.default_rng(seed)
        self.env = Overlook()
        self.tick = 0
        self.all_agents: list[Agent] = []
        self.active_agents: list[Agent] = []
        self.departed: list[Agent] = []

        # recorded per-tick for the viz
        self.heatmap_data: list[list[int]] = []
        self.occupancy_history: list[int] = []
        self.waiting_history: list[int] = []
        self.finished = False

    def _spawn_agents(self):
        """Poisson arrivals, 33% chance per type."""
        n = self.rng.poisson(ARRIVAL_LAMBDA)
        for _ in range(n):
            roll = self.rng.random()
            if roll < 1 / 3:
                agent = Photographer(self.rng)
            elif roll < 2 / 3:
                agent = Viewer(self.rng)
            else:
                agent = Socializer(self.rng)
            self.all_agents.append(agent)
            self.active_agents.append(agent)
            agent.state = "entering"

    def _try_place(self, agent: Agent) -> bool:
        """Find a slot for this agent per its type rules. Returns True if placed."""
        if isinstance(agent, Photographer):
            slot = self.env.any_empty_slot()
        elif isinstance(agent, Viewer):
            slot = self.env.best_slot_for_viewer()
        elif isinstance(agent, Socializer):
            slot = self.env.best_slot_for_socializer()
        else:
            slot = None

        if slot is not None:
            self.env.place_agent(agent, slot)
            return True
        return False

    def _process_entering(self):
        for agent in [a for a in self.active_agents if a.state == "entering"]:
            if self.env.is_path_congested():
                self.env.add_to_waiting(agent)
            elif not self._try_place(agent):
                self.env.add_to_waiting(agent)

    def _tick_railing(self):
        """Countdown timers, patience rolls — remove anyone who's done."""
        to_remove: list[Agent] = []
        for i, agent in enumerate(self.env.slots):
            if agent is None:
                continue
            if isinstance(agent, Photographer):
                agent.timer -= 1
                if agent.timer <= 0:
                    to_remove.append(agent)
            elif isinstance(agent, Viewer):
                if self.env.neighbor_count(i) > 1:
                    if self.rng.random() < VIEWER_PATIENCE_THRESHOLD:
                        to_remove.append(agent)
            elif isinstance(agent, Socializer):
                agent.timer -= 1
                if agent.timer <= 0:
                    to_remove.append(agent)

        for agent in to_remove:
            self.env.remove_agent(agent)
            self.active_agents.remove(agent)
            self.departed.append(agent)

    def _process_waiting(self):
        """Waiting agents either bail, re-enter, or keep waiting."""
        still_waiting: deque[Agent] = deque()
        for agent in self.env.waiting_area:
            agent.ticks_waiting += 1

            # abandonment chance grows the longer you wait
            if self.rng.random() < QUEUE_ABANDON_BASE + QUEUE_ABANDON_GROWTH * agent.ticks_waiting:
                agent.state = "departing"
                if agent in self.active_agents:
                    self.active_agents.remove(agent)
                self.departed.append(agent)
                continue

            if not self.env.is_path_congested() and self._try_place(agent):
                continue  # placed successfully
            still_waiting.append(agent)

        self.env.waiting_area = still_waiting

    def _record_snapshot(self):
        row = [_TYPE_CODE.get(type(s), 0) for s in self.env.slots]
        self.heatmap_data.append(row)
        self.occupancy_history.append(self.env.occupied_count())
        self.waiting_history.append(len(self.env.waiting_area))

    def step(self):
        if self.tick >= SIM_DURATION:
            self.finished = True
            return

        self._spawn_agents()
        self._process_entering()
        self._tick_railing()
        self._process_waiting()
        self.env.update_dead_zones()
        self._record_snapshot()

        self.tick += 1
