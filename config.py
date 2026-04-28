# tunables live here. touch at your own risk.

SEED = 42
NUM_SLOTS = 10
SIM_DURATION = 120          # ticks (shows as "minutes", runs as seconds)
TICK_INTERVAL_MS = 100

# arrival / dwell
ARRIVAL_LAMBDA = 2.0
PHOTOGRAPHER_DURATION = (5, 15)
PHOTOGRAPHER_DURATION_MEAN = 10
PHOTOGRAPHER_DURATION_STD = 2.5
SOCIALIZER_DURATION_MEAN = 8
SOCIALIZER_DURATION_STD = 2.0
VIEWER_PATIENCE_THRESHOLD = 0.5  # chance of bailing each tick when crowded

# phantom queue thresholds
PATH_CONGESTION_THRESHOLD = 7
QUEUE_ABANDON_BASE = 0.05
QUEUE_ABANDON_GROWTH = 0.02      # stacks per tick spent waiting

# dead zone detection
DEAD_ZONE_DENSITY_TICKS = 10
DEAD_ZONE_NEIGHBOR_MIN = 2

# colors
AGENT_COLORS = {
    "Photographer": "#3B82F6",
    "Viewer":       "#22C55E",
    "Socializer":   "#F97316",
}
EMPTY_COLOR = "#1E293B"
