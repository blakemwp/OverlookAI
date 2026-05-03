import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
from matplotlib.animation import FuncAnimation
from matplotlib.colors import ListedColormap, BoundaryNorm

from Code.agents import Photographer, Viewer, Socializer
from config import NUM_SLOTS, SIM_DURATION, TICK_INTERVAL_MS, AGENT_COLORS, EMPTY_COLOR
from Code.simulation import Simulation

# 0=empty, 1=photographer, 2=viewer, 3=socializer
CMAP = ListedColormap([EMPTY_COLOR, AGENT_COLORS["Photographer"],
                        AGENT_COLORS["Viewer"], AGENT_COLORS["Socializer"]])
BOUNDS = [-0.5, 0.5, 1.5, 2.5, 3.5]
NORM = BoundaryNorm(BOUNDS, CMAP.N)

# palette
_BG = "#0F172A"
_TEXT = "#E2E8F0"
_GRID = "#334155"


def _style_ax(ax):
    ax.set_facecolor(_BG)
    ax.tick_params(colors=_TEXT, labelsize=8)
    for spine in ax.spines.values():
        spine.set_color(_GRID)


def _build_layout(fig):
    """Create all axes, return them as a dict so the update loop can find them."""
    gs = gridspec.GridSpec(3, 2, height_ratios=[1, 4, 2],
                           hspace=0.35, wspace=0.30,
                           left=0.07, right=0.95, top=0.92, bottom=0.08)

    axes = {
        "rail": fig.add_subplot(gs[0, 0]),
        "info": fig.add_subplot(gs[0, 1]),
        "heat": fig.add_subplot(gs[1, :]),
        "occ":  fig.add_subplot(gs[2, 0]),
        "wait": fig.add_subplot(gs[2, 1]),
    }
    for ax in axes.values():
        _style_ax(ax)
    return axes


def _setup_rail(ax):
    ax.set_xlim(-0.5, NUM_SLOTS - 0.5)
    ax.set_ylim(-0.5, 0.5)
    ax.set_yticks([])

    # adapt tick density and per-slot decorations to the slot count
    show_per_slot_labels = NUM_SLOTS <= 30
    tick_step = max(1, NUM_SLOTS // 20)
    ticks = list(range(0, NUM_SLOTS, tick_step))
    ax.set_xticks(ticks)
    ax.set_xticklabels([str(i) for i in ticks], fontsize=8, color=_TEXT)
    ax.set_title("Railing State", fontsize=10, color=_TEXT, pad=6)

    rect_w = 0.9 if NUM_SLOTS <= 30 else 1.0
    edge_lw = 1.2 if NUM_SLOTS <= 30 else 0.0
    dz_w = 0.96 if NUM_SLOTS <= 30 else 1.02

    rects, labels, dz_markers = [], [], []
    for i in range(NUM_SLOTS):
        r = plt.Rectangle((i - rect_w / 2, -0.4), rect_w, 0.8,
                           facecolor=EMPTY_COLOR, edgecolor="#475569",
                           linewidth=edge_lw, zorder=2)
        ax.add_patch(r)
        rects.append(r)

        if show_per_slot_labels:
            t = ax.text(i, 0, "", ha="center", va="center",
                        fontsize=7, color="white", fontweight="bold", zorder=3)
        else:
            t = None
        labels.append(t)

        dz = plt.Rectangle((i - dz_w / 2, -0.48), dz_w, 0.96,
                            facecolor="none", edgecolor="#EF4444",
                            linewidth=2 if NUM_SLOTS <= 30 else 1, linestyle="--",
                            zorder=4, visible=False)
        ax.add_patch(dz)
        dz_markers.append(dz)

    return rects, labels, dz_markers


def _setup_info(ax):
    ax.axis("off")
    patches = [
        mpatches.Patch(color=AGENT_COLORS["Photographer"], label="Photographer"),
        mpatches.Patch(color=AGENT_COLORS["Viewer"],       label="Viewer"),
        mpatches.Patch(color=AGENT_COLORS["Socializer"],   label="Socializer"),
        mpatches.Patch(facecolor=EMPTY_COLOR, label="Empty", edgecolor="#475569"),
    ]
    ax.legend(handles=patches, loc="center left", ncol=2,
              fontsize=9, frameon=False, labelcolor=_TEXT)
    stats = ax.text(0.95, 0.5, "", transform=ax.transAxes,
                    ha="right", va="center", fontsize=9,
                    color=_TEXT, fontfamily="monospace")
    return stats


def _setup_line_chart(ax, title, ylabel):
    ax.set_title(title, fontsize=10, color=_TEXT, pad=6)
    ax.set_xlabel("Time (minutes)", fontsize=9, color=_TEXT)
    ax.set_ylabel(ylabel, fontsize=9, color=_TEXT)
    ax.set_xlim(0, SIM_DURATION)


def run(seed=None):
    from config import SEED as default_seed
    sim = Simulation(seed=seed or default_seed)

    fig = plt.figure(figsize=(14, 8), facecolor=_BG)
    fig.canvas.manager.set_window_title("Overlook — Agent-Based Model")

    axes = _build_layout(fig)

    # timer + title
    timer_text = fig.text(0.07, 0.96, "Minutes: 0", fontsize=14,
                          fontweight="bold", color="#F8FAFC", fontfamily="monospace")
    fig.text(0.50, 0.96, "Overlook Agent-Based Model",
             fontsize=16, fontweight="bold", color="#F8FAFC",
             ha="center", fontfamily="sans-serif")

    # railing panel
    rects, labels, dz_markers = _setup_rail(axes["rail"])

    # info panel (legend + live stats)
    stats_text = _setup_info(axes["info"])

    # heatmap
    ax_heat = axes["heat"]
    ax_heat.set_title("Spatiotemporal Heatmap", fontsize=10, color=_TEXT, pad=6)
    ax_heat.set_xlabel("Slot Index", fontsize=9, color=_TEXT)
    ax_heat.set_ylabel("Time (minutes)", fontsize=9, color=_TEXT)

    # occupancy line chart
    _setup_line_chart(axes["occ"], "Railing Occupancy", "Occupied Slots")
    axes["occ"].set_ylim(0, NUM_SLOTS + 1)
    occ_line, = axes["occ"].plot([], [], color="#3B82F6", linewidth=1.5)
    axes["occ"].axhline(y=NUM_SLOTS, color="#EF4444", linestyle="--", linewidth=0.8, alpha=0.5)
    axes["occ"].text(SIM_DURATION - 1, NUM_SLOTS + 0.3, "Physical Capacity",
                     fontsize=7, color="#EF4444", ha="right", alpha=0.7)

    # waiting area line chart
    _setup_line_chart(axes["wait"], "Waiting Area Population", "Agents Waiting")
    wait_line, = axes["wait"].plot([], [], color="#F97316", linewidth=1.5)

    def update(_frame):
        if sim.finished:
            return

        sim.step()
        timer_text.set_text(f"Minutes: {sim.tick}")

        # railing colours + labels
        for i in range(NUM_SLOTS):
            agent = sim.env.slots[i]
            if agent is None:
                rects[i].set_facecolor(EMPTY_COLOR)
                if labels[i] is not None:
                    labels[i].set_text("")
            else:
                rects[i].set_facecolor(AGENT_COLORS[agent.agent_type])
                if labels[i] is not None:
                    labels[i].set_text(repr(agent))
            dz_markers[i].set_visible(i in sim.env.dead_zones)

        # live stats
        n_ph = sum(1 for s in sim.env.slots if isinstance(s, Photographer))
        n_vw = sum(1 for s in sim.env.slots if isinstance(s, Viewer))
        n_so = sum(1 for s in sim.env.slots if isinstance(s, Socializer))
        stats_text.set_text(
            f"Railing  P:{n_ph}  V:{n_vw}  S:{n_so}\n"
            f"Waiting  {len(sim.env.waiting_area):>3}   "
            f"Dead Zones  {len(sim.env.dead_zones)}"
        )

        # rebuild heatmap each frame (it grows a row per tick)
        if sim.heatmap_data:
            ax_heat.clear()
            _style_ax(ax_heat)
            data = np.array(sim.heatmap_data)
            ax_heat.imshow(data, aspect="auto", cmap=CMAP, norm=NORM,
                           origin="upper", interpolation="nearest",
                           extent=[-0.5, NUM_SLOTS - 0.5, len(data) - 0.5, -0.5])
            ax_heat.set_title("Spatiotemporal Heatmap", fontsize=10, color=_TEXT, pad=6)
            ax_heat.set_xlabel("Slot Index", fontsize=9, color=_TEXT)
            ax_heat.set_ylabel("Time (minutes)", fontsize=9, color=_TEXT)
            ax_heat.set_xticks(range(NUM_SLOTS))

        # line charts
        ticks = list(range(len(sim.occupancy_history)))
        occ_line.set_data(ticks, sim.occupancy_history)
        wait_line.set_data(ticks, sim.waiting_history)
        if sim.waiting_history:
            axes["wait"].set_ylim(0, max(max(sim.waiting_history) + 2, 5))

    _anim = FuncAnimation(fig, update, interval=TICK_INTERVAL_MS,
                          cache_frame_data=False, save_count=0)
    plt.show()
