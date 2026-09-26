"""Stages of the Entrepreneur (2026 refresh) - streamgraph.

Layer shapes follow the original Edward Lowe Foundation graphic: the founder
starts as Creator and Leader, is soon consumed by doing the Work, hires and
grows into a Manager, and eventually moves mostly to Leading the company.
State-change markers sit between milestones, where the founder's role shifts.

Usage:
    python3 streamgraph.py           # static PNG / SVG / PDF
    python3 streamgraph.py --animate # also MP4 + GIF
"""
import sys

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.animation import FFMpegWriter, PillowWriter
from matplotlib.patches import Circle, Polygon, Rectangle
from scipy.interpolate import PchipInterpolator
from scipy.ndimage import gaussian_filter1d

try:
    import imageio_ffmpeg
    matplotlib.rcParams["animation.ffmpeg_path"] = imageio_ffmpeg.get_ffmpeg_exe()
except ImportError:
    pass

BG = "#FAF8F5"
INK = "#1F2430"
MUTED = "#6B6F76"
GUIDE = "#D9D3CA"
FADED = "#B8B2A8"

# Bottom -> top
LAYERS = [
    ("Leader",  "#56ADBF", INK),
    ("Worker",  "#BF8756", INK),
    ("Creator", "#4A5568", "#FFFFFF"),
    ("Manager", "#D4A373", INK),
]

MILESTONES = [
    (0.8, "Create the\nOpportunity"),
    (3.0, "The Capacity\nBottleneck"),
    (5.0, "Systemizing &\nOffloading"),
    (7.0, "Building Team\nAutonomy"),
    (9.2, "The Executive\nShift"),
]
# State changes sit between milestones, where one role hands off to the next
STATE_CHANGES = [(a + b) / 2 for (a, _), (b, _) in zip(MILESTONES, MILESTONES[1:])]

# Illustrative thickness keyframes (x from 0 to 10)
KX = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
KEYS = {
    "Leader":  [1.4, 1.1, 0.8, 0.5, 0.4, 0.6, 1.5, 2.6, 3.4, 3.9, 4.1],
    "Worker":  [0.4, 1.8, 2.8, 2.9, 2.3, 1.2, 0.4, 0.0, 0.0, 0.0, 0.0],
    "Creator": [1.4, 1.1, 0.9, 0.7, 0.6, 0.6, 0.8, 1.1, 1.6, 2.1, 2.4],
    "Manager": [0.0, 0.0, 0.1, 1.0, 2.0, 2.1, 1.6, 1.1, 0.7, 0.5, 0.45],
}
# Where each label sits (x) - inside the layer's fullest stretch
LABEL_X = {"Leader": 8.4, "Worker": 2.5, "Creator": 0.9, "Manager": 4.7}

x = np.linspace(0, 10, 800)
thick = np.array([np.clip(gaussian_filter1d(PchipInterpolator(KX, KEYS[n])(x), 30, mode="nearest"), 0, None)
                  for n, _, _ in LAYERS])

# Flat ground line, like the original: the business builds up from the base
base = np.zeros_like(x)
bottoms = base + np.vstack([np.zeros_like(x), np.cumsum(thick, axis=0)[:-1]])
tops = bottoms + thick

font = "DejaVu Sans"
for f in ("Inter", "Lato", "Source Sans 3", "Helvetica Neue"):
    if any(f == e.name for e in font_manager.fontManager.ttflist):
        font = f
        break
plt.rcParams["font.family"] = font


def draw_cycle(iax, angle=0.0, color=INK):
    """Two chasing arrows in a round badge - the state-change mark."""
    iax.clear()
    iax.set_xlim(-1.1, 1.1)
    iax.set_ylim(-1.1, 1.1)
    iax.set_aspect("equal")
    iax.axis("off")
    iax.add_patch(Circle((0, 0), 1.0, facecolor=BG, edgecolor=color, lw=1.5))
    r, sweep = 0.56, 125
    for start in (35, 215):
        t = np.radians(np.linspace(start, start + sweep, 40) + angle)
        iax.plot(r * np.cos(t), r * np.sin(t), color=color, lw=1.8, solid_capstyle="round")
        # Arrowhead at the end of the arc, pointing along the direction of travel
        e = t[-1]
        tip = np.array([np.cos(e), np.sin(e)]) * r
        tang = np.array([-np.sin(e), np.cos(e)])
        norm = np.array([np.cos(e), np.sin(e)])
        head = [tip + tang * 0.26, tip - norm * 0.2, tip + norm * 0.2]
        iax.add_patch(Polygon(head, closed=True, facecolor=color, edgecolor=color, lw=0.5))


def build():
    fig, ax = plt.subplots(figsize=(16, 9), dpi=100)
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)

    ymin, ymax = -0.35, (tops[-1].max() + 0.4)
    ty = ymax + 0.5
    parts = {"fills": [], "seams": [], "labels": {}, "dots": [], "mtext": [], "icons": []}

    # Milestone guides behind the waves
    for mx, _ in MILESTONES:
        ax.plot([mx, mx], [0, ty], color=GUIDE, lw=1, ls=(0, (2, 4)), zorder=0)

    # Ground line
    ax.plot([-0.1, 10.1], [0, 0], color=INK, lw=1.2, zorder=1, solid_capstyle="round")

    # Waves: fill + 2px background seam between layers
    for i, (name, color, _) in enumerate(LAYERS):
        parts["fills"].append(ax.fill_between(x, bottoms[i], tops[i], color=color, lw=0, zorder=2))
    for i in range(1, len(LAYERS)):
        parts["seams"].append(ax.plot(x, bottoms[i], color=BG, lw=2.2, zorder=3,
                                      solid_capstyle="round")[0])

    # Labels inside the waves
    for i, (name, color, txt) in enumerate(LAYERS):
        lx = LABEL_X[name]
        j = np.argmin(np.abs(x - lx))
        ly = (bottoms[i][j] + tops[i][j]) / 2
        parts["labels"][name] = ax.text(lx, ly, name, ha="center", va="center", fontsize=20,
                                        fontweight="bold", color=txt, zorder=4)

    # Top timeline
    ax.plot([0, 10], [ty, ty], color=INK, lw=1.5, zorder=5, solid_capstyle="round")
    for k, (mx, label) in enumerate(MILESTONES, 1):
        parts["dots"].append(ax.scatter([mx], [ty], s=150, color=BG, edgecolor=INK,
                                        linewidth=2, zorder=6))
        num = ax.text(mx, ty + 0.35, f"{k:02d}", ha="center", va="bottom", fontsize=11,
                      color=MUTED, fontweight="bold", zorder=6)
        lab = ax.text(mx, ty + 0.85, label, ha="center", va="bottom", fontsize=14,
                      color=INK, linespacing=1.25, zorder=6)
        parts["mtext"].append((num, lab))

    # Title block
    fig.text(0.055, 0.93, "Stages of the Entrepreneur", fontsize=28,
             fontweight="bold", color=INK, ha="left", va="center")
    fig.text(0.055, 0.885, "How the founder's role shifts as the business grows",
             fontsize=15, color=MUTED, ha="left", va="center")

    ax.set_xlim(-0.3, 10.3)
    ax.set_ylim(ymin, ty + 2.2)
    ax.axis("off")
    fig.subplots_adjust(left=0.04, right=0.96, top=0.84, bottom=0.04)

    # State-change badges sit on the timeline, sized square in display space
    to_fig = ax.transData + fig.transFigure.inverted()
    size = 0.042  # figure-height fraction
    w, h = size * 9 / 16, size
    for sx in STATE_CHANGES:
        fx, fy = to_fig.transform((sx, ty))
        iax = fig.add_axes([fx - w / 2, fy - h / 2, w, h], zorder=10)
        draw_cycle(iax)
        parts["icons"].append((sx, iax))

    # Key for the badge, top right
    kax = fig.add_axes([0.745 - w / 2, 0.885 - h / 2, w, h])
    draw_cycle(kax)
    fig.text(0.76, 0.885, "State change: the founder's role shifts",
             fontsize=13, color=MUTED, ha="left", va="center")

    parts["ty"], parts["ymin"] = ty, ymin
    return fig, ax, parts


def save_static():
    fig, _, _ = build()
    for ext in ("png", "svg", "pdf"):
        fig.savefig(f"stages_of_the_entrepreneur_2026.{ext}", facecolor=BG,
                    dpi=300 if ext == "png" else None)
    plt.close(fig)


def save_animation(fps=30, sweep_s=7.0, hold_s=3.0):
    """Waves grow left to right; milestones light up and badges spin as reached."""
    fig, ax, parts = build()
    ty, ymin = parts["ty"], parts["ymin"]

    clip = Rectangle((-1, ymin - 1), 0, ty + 10, transform=ax.transData)
    head = ax.plot([0, 0], [0, ty], color=INK, lw=1, alpha=0.35, zorder=4.5)[0]
    head_dot = ax.scatter([0], [ty], s=70, color=INK, zorder=7)

    n_sweep, n_hold = int(fps * sweep_s), int(fps * hold_s)
    x0, x1 = -0.2, 10.2
    spin = 0.45  # half-width (x units) of the window in which a badge spins

    def ease(t):
        return 0.5 - 0.5 * np.cos(np.pi * np.clip(t, 0, 1))

    def frame(f):
        p = x0 + (x1 - x0) * ease(f / n_sweep) if f < n_sweep else x1
        # Rectangle clips are snapshotted when set, so re-apply as the reveal grows
        clip.set_width(p + 1)
        for art in parts["fills"] + parts["seams"]:
            art.set_clip_path(clip)
        done = f >= n_sweep
        head.set_xdata([p, p])
        head.set_alpha(0 if done else 0.35)
        head_dot.set_offsets([[p, ty]])
        head_dot.set_alpha(0 if done else 1)

        for (mx, _), dot, (num, lab) in zip(MILESTONES, parts["dots"], parts["mtext"]):
            on = p >= mx
            dot.set_edgecolor(INK if on else FADED)
            num.set_alpha(1 if on else 0.35)
            lab.set_alpha(1 if on else 0.35)

        for name, txt in parts["labels"].items():
            txt.set_alpha(float(np.clip((p - LABEL_X[name] - 0.2) / 0.5, 0, 1)))

        for sx, iax in parts["icons"]:
            if p < sx - spin:
                draw_cycle(iax, 0, FADED)
            elif p < sx + spin:
                draw_cycle(iax, -360 * (p - (sx - spin)) / (2 * spin), INK)
            else:
                draw_cycle(iax, 0, INK)
        return []

    from matplotlib.animation import FuncAnimation
    total = n_sweep + n_hold
    anim = FuncAnimation(fig, frame, frames=total, blit=False)
    anim.save("stages_of_the_entrepreneur_2026.mp4", dpi=120, savefig_kwargs={"facecolor": BG},
              writer=FFMpegWriter(fps=fps, bitrate=6000, extra_args=["-pix_fmt", "yuv420p"]))

    gif_fps = 15
    anim_gif = FuncAnimation(fig, frame, frames=range(0, total, fps // gif_fps), blit=False)
    anim_gif.save("stages_of_the_entrepreneur_2026.gif", dpi=60,
                  savefig_kwargs={"facecolor": BG}, writer=PillowWriter(fps=gif_fps))
    plt.close(fig)


if __name__ == "__main__":
    save_static()
    if "--animate" in sys.argv:
        save_animation()
    print("saved")
