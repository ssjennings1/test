"""Stages of the Entrepreneur (2026 refresh) - streamgraph.

Layer shapes follow the original Edward Lowe Foundation graphic: the founder
starts as Creator and Leader, is soon consumed by doing the Work, hires and
grows into a Manager, and eventually moves mostly to Leading the company.
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import font_manager
from scipy.interpolate import PchipInterpolator
from scipy.ndimage import gaussian_filter1d

BG = "#FAF8F5"
INK = "#1F2430"
MUTED = "#6B6F76"
GUIDE = "#D9D3CA"

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

# Illustrative thickness keyframes (x from 0 to 10)
KX = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
KEYS = {
    "Leader":  [1.4, 1.1, 0.8, 0.5, 0.4, 0.6, 1.5, 2.6, 3.4, 3.9, 4.1],
    "Worker":  [0.4, 1.8, 2.8, 2.9, 2.3, 1.2, 0.4, 0.0, 0.0, 0.0, 0.0],
    "Creator": [1.4, 1.1, 0.9, 0.7, 0.6, 0.6, 0.8, 1.1, 1.3, 1.4, 1.4],
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

fig, ax = plt.subplots(figsize=(16, 9), dpi=100)
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)

ymin, ymax = -0.35, (tops[-1].max() + 0.4)

# Milestone guides behind the waves
for mx, _ in MILESTONES:
    ax.plot([mx, mx], [0, ymax + 0.5], color=GUIDE, lw=1, ls=(0, (2, 4)), zorder=0)

# Ground line
ax.plot([-0.1, 10.1], [0, 0], color=INK, lw=1.2, zorder=1, solid_capstyle="round")

# Waves: fill + 2px background seam between layers
for i, (name, color, _) in enumerate(LAYERS):
    ax.fill_between(x, bottoms[i], tops[i], color=color, lw=0, zorder=2)
for i in range(1, len(LAYERS)):
    ax.plot(x, bottoms[i], color=BG, lw=2.2, zorder=3, solid_capstyle="round")

# Labels inside the waves
for i, (name, color, txt) in enumerate(LAYERS):
    lx = LABEL_X[name]
    j = np.argmin(np.abs(x - lx))
    ly = (bottoms[i][j] + tops[i][j]) / 2
    ax.text(lx, ly, name, ha="center", va="center", fontsize=20,
            fontweight="bold", color=txt, zorder=4)

# Top timeline
ty = ymax + 0.5
ax.plot([0, 10], [ty, ty], color=INK, lw=1.5, zorder=5, solid_capstyle="round")
for k, (mx, label) in enumerate(MILESTONES, 1):
    ax.scatter([mx], [ty], s=150, color=BG, edgecolor=INK, linewidth=2, zorder=6)
    ax.text(mx, ty + 0.35, f"{k:02d}", ha="center", va="bottom", fontsize=11,
            color=MUTED, fontweight="bold", zorder=6)
    ax.text(mx, ty + 0.85, label, ha="center", va="bottom", fontsize=14,
            color=INK, linespacing=1.25, zorder=6)

# Title block
fig.text(0.055, 0.93, "Stages of the Entrepreneur", fontsize=28,
         fontweight="bold", color=INK, ha="left", va="center")
fig.text(0.055, 0.885, "How the founder's role shifts as the business grows",
         fontsize=15, color=MUTED, ha="left", va="center")

ax.set_xlim(-0.3, 10.3)
ax.set_ylim(ymin, ty + 2.2)
ax.axis("off")
fig.subplots_adjust(left=0.04, right=0.96, top=0.84, bottom=0.04)

for ext in ("png", "svg", "pdf"):
    fig.savefig(f"stages_of_the_entrepreneur_2026.{ext}", facecolor=BG,
                dpi=300 if ext == "png" else None)
print("saved")
