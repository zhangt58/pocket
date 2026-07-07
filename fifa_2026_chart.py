import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import numpy as np

# ── Palette (GitHub dark) ──
BG = '#0d1117'
CARD = '#161b22'
BORDER = '#30363d'
TEXT = '#e6edf3'
MUTE = '#8b949e'
BLUE = '#58a6ff'
GREEN = '#3fb950'
RED = '#f85149'
ORANGE = '#f0883e'
PURPLE = '#d2a8ff'
PINK = '#f778ba'
YELLOW = '#ffa657'

fig = plt.figure(figsize=(16, 10), facecolor=BG)
fig.suptitle('FIFA WORLD CUP 2026  |  ROUND OF 16',
             fontsize=24, fontweight='bold', color=TEXT, y=0.96,
             family='sans-serif')

gs = GridSpec(3, 2, figure=fig, hspace=0.42, wspace=0.38,
              left=0.05, right=0.96, top=0.91, bottom=0.05)

def rnd_box(ax, x, y, w, h, color, alpha=0.85, zorder=1):
    box = mpatches.FancyBboxPatch((x, y), w, h,
                                   boxstyle="round,pad=0.12",
                                   facecolor=color, edgecolor='none',
                                   alpha=alpha, zorder=zorder)
    ax.add_patch(box)

def flag_box(ax, x, y, code, w=0.9, h=0.45, zorder=3):
    """Draw a small colored flag placeholder."""
    # Color maps for country flag bands
    colors = {
        'BR': ['#009c3b', '#fdd100', '#002776'],
        'NO': ['#ef2b2d', '#00205b', '#ffffff'],
        'MX': ['#006847', '#ffffff', '#ce1126'],
        'EN': ['#ce1126', '#ffffff', '#00257e'],
        'PT': ['#006600', '#cf142b'],
        'SP': ['#c60b1e', '#ffc400'],
        'US': ['#b22234', '#ffffff', '#3c3b6e'],
        'BE': ['#262626', '#fae042', '#e30613'],
    }
    flag_colors = colors.get(code, ['#888888'])
    band_h = h / len(flag_colors)
    for i, c in enumerate(flag_colors):
        rect = mpatches.Rectangle((x, y + i*band_h), w, band_h,
                                   facecolor=c, edgecolor='white',
                                   linewidth=0.5, zorder=zorder)
        ax.add_patch(rect)
    ax.text(x + w/2, y + h/2, code, fontsize=8, color='#fff',
            ha='center', va='center', fontweight='bold', zorder=zorder+1,
            family='monospace')

# ════════════════════════════════════════
# LEFT PANEL: Knockout Bracket
# ════════════════════════════════════════
ax1 = fig.add_subplot(gs[:, 0])
ax1.set_xlim(0, 10)
ax1.set_ylim(0, 10)
ax1.axis('off')

# Subtle card bg
rnd_box(ax1, 0.3, 0.3, 9.4, 9.4, CARD, alpha=0.4)
ax1.text(5, 9.6, 'KNOCKOUT BRACKET', fontsize=12, fontweight='bold',
         color=BLUE, ha='center', family='sans-serif')

# Separator line
ax1.plot([1, 9], [9.1, 9.1], color=BORDER, lw=1)

matches = [
    ('BR', 'Brazil',   'W',   'Norway', 'NO', 'L', 8.1),
    ('MX', 'Mexico',   'L',   'England', 'EN', 'W', 6.5),
    ('PT', 'Portugal', '0',   'Spain',   'SP', '1', 4.9),
    ('US', 'USA',      'vs', 'Belgium', 'BE', 'vs', 3.3),
]

for code1, t1, s1, t2, code2, s2, y in matches:
    is_live = s1 == 'vs'
    bg_alpha = 0.5 if is_live else 0.25
    rnd_box(ax1, 0.6, y-0.4, 8.8, 0.8, CARD, alpha=bg_alpha)

    # Border glow for live
    if is_live:
        border = mpatches.FancyBboxPatch((0.6, y-0.4), 8.8, 0.8,
                                          boxstyle="round,pad=0.12",
                                          facecolor='none', edgecolor=PINK,
                                          linewidth=2, linestyle='--', zorder=10)
        ax1.add_patch(border)

    # Flag + Team 1
    flag_box(ax1, 1.0, y-0.35, code1)
    ax1.text(2.2, y, t1, fontsize=12, color=TEXT, ha='left',
             fontweight='bold' if ('W' in s1) else 'normal', family='sans-serif')

    # Score
    sc1_color = GREEN if 'W' == s1 else (PINK if is_live else RED)
    ax1.text(4.5, y, s1, fontsize=14, color=sc1_color, ha='center',
             fontweight='bold', family='monospace')

    ax1.text(5.0, y, '|', fontsize=10, color=MUTE, ha='center', family='sans-serif')

    sc2_color = GREEN if 'W' == s2 else (PINK if is_live else RED)
    ax1.text(5.5, y, s2, fontsize=14, color=sc2_color, ha='center',
             fontweight='bold', family='monospace')

    # Team 2 + Flag
    ax1.text(6.3, y, t2, fontsize=12, color=TEXT, ha='left',
             fontweight='bold' if ('W' in s2) else 'normal', family='sans-serif')
    flag_box(ax1, 7.8, y-0.35, code2)

# LIVE badge
circle = mpatches.Circle((0.85, 3.3), 0.1, color=RED, zorder=12)
ax1.add_patch(circle)
ax1.text(0.85, 3.3, '', fontsize=6, color='#fff', ha='center', va='center', zorder=13)
ax1.text(1.25, 3.3, 'LIVE', fontsize=9, color=PINK, ha='left', fontweight='bold',
         family='sans-serif', zorder=13)

# Quarter finalists
ax1.text(5, 1.6, 'QUARTER-FINALISTS', fontsize=10, fontweight='bold',
         color=PURPLE, ha='center', family='sans-serif')
ax1.plot([2, 8], [1.35, 1.35], color=BORDER, lw=0.8)
qf = ['Brazil', 'England', 'Spain', 'USA / BEL']
for i, q in enumerate(qf):
    x = 2.0 + i * 1.5
    ax1.text(x, 0.9, q, fontsize=10, color=TEXT, ha='center',
             fontweight='bold' if i < 3 else 'normal',
             style='italic' if i == 3 else 'normal',
             family='sans-serif')

# ════════════════════════════════════════
# TOP RIGHT: Top Scorers
# ════════════════════════════════════════
ax2 = fig.add_subplot(gs[0, 1])
ax2.set_xlim(0, 10)
ax2.set_ylim(0, 10)
ax2.axis('off')

rnd_box(ax2, 0.3, 0.3, 9.4, 5.0, CARD, alpha=0.3)
ax2.text(5, 4.9, 'TOP SCORERS', fontsize=12, fontweight='bold',
         color=YELLOW, ha='center', family='sans-serif')
ax2.plot([1, 9], [4.6, 4.6], color=BORDER, lw=0.8)

scorers = [
    ('Haaland', 'NO', 7, BLUE),
    ('Mbappe',  'FR', 4, GREEN),
    ('Messi',   'AR', 3, GREEN),
    ('Ronaldo', 'PT', 3, GREEN),
]

for i, (name, code, goals, bar_color) in enumerate(scorers):
    y = 3.7 - i * 1.15
    bar_w = goals / 7 * 4.5

    # Bar background
    rnd_box(ax2, 3.8, y-0.2, 5.5, 0.4, '#21262d', alpha=0.6)
    # Bar fill
    rnd_box(ax2, 3.8, y-0.2, bar_w, 0.4, bar_color, alpha=0.75)

    # Rank
    ax2.text(0.7, y, f'#{i+1}', fontsize=10, color=MUTE, ha='center',
             family='monospace')
    # Name
    ax2.text(2.2, y, name, fontsize=11, color=TEXT, ha='left',
             fontweight='bold' if goals == 7 else 'normal', family='sans-serif')
    # Goals
    ax2.text(3.8 + bar_w + 0.25, y, str(goals), fontsize=12, color=TEXT,
             ha='left', fontweight='bold', family='monospace')

# Annotation
ax2.text(5, 0.6, 'Haaland alone outscored Messi + Mbappe + Ronaldo combined!',
         fontsize=8.5, color=PURPLE, ha='center', style='italic', family='sans-serif')

# ════════════════════════════════════════
# MID RIGHT: Balogun Controversy
# ════════════════════════════════════════
ax3 = fig.add_subplot(gs[1, 1])
ax3.set_xlim(0, 10)
ax3.set_ylim(0, 10)
ax3.axis('off')

rnd_box(ax3, 0.3, 0.3, 9.4, 4.8, CARD, alpha=0.3)
# Red header bar
rnd_box(ax3, 0.3, 4.3, 9.4, 0.7, '#da3633', alpha=0.25)
ax3.text(5, 4.85, 'THE BALOGUN CONTROVERSY', fontsize=12, fontweight='bold',
         color=RED, ha='center', family='sans-serif')

timeline = [
    ('Group Stage', 'Balogun sent off, 1-game ban', RED),
    ('Appeals', 'FIFA suspension handed down', ORANGE),
    ('US President', 'Trump calls FIFA chief Infantino', PURPLE),
    ('RESULT', 'Ban OVERTURNED - Balogun cleared', GREEN),
    ('Belgium', 'Appeal to reinstate ban DENIED', RED),
]

for i, (label, desc, c) in enumerate(timeline):
    y = 3.7 - i * 0.8
    # Dot
    dot = mpatches.Circle((1.1, y), 0.1, color=c, zorder=5)
    ax3.add_patch(dot)
    # Connector
    if i < len(timeline) - 1:
        ax3.plot([1.1, 1.1], [y-0.1, y-0.7], color=BORDER, lw=1.5, zorder=3)
    # Label
    ax3.text(1.6, y, label, fontsize=9, color=c, ha='left', fontweight='bold',
             family='sans-serif')
    ax3.text(5.5, y, desc, fontsize=8, color=MUTE, ha='left', family='sans-serif')

ax3.text(5, 0.5, '"Integrity of the game is at stake"  -  UEFA',
         fontsize=8, color=MUTE, ha='center', style='italic', family='sans-serif')

# ════════════════════════════════════════
# BOTTOM RIGHT: Ronaldo Farewell
# ════════════════════════════════════════
ax4 = fig.add_subplot(gs[2, 1])
ax4.set_xlim(0, 10)
ax4.set_ylim(0, 10)
ax4.axis('off')

rnd_box(ax4, 0.3, 0.3, 9.4, 4.5, CARD, alpha=0.3)
ax4.text(5, 4.4, 'RONALDO\'S FINAL WORLD CUP BOW', fontsize=12, fontweight='bold',
         color=TEXT, ha='center', family='sans-serif')
ax4.plot([1, 9], [4.1, 4.1], color=BORDER, lw=0.8)

# 5 World Cups timeline
years = [2006, 2010, 2014, 2018, 2026]
for i, yr in enumerate(years):
    x = 1.5 + i * 1.6
    c = ORANGE if yr == 2026 else MUTE
    ax4.text(x, 3.4, str(yr), fontsize=10, color=c, ha='center',
             fontweight='bold', family='monospace')
    ax4.plot([x, x], [3.0, 3.2], color=c, lw=2)

ax4.plot([1.5, 1.5+4*1.6], [3.05, 3.05], color=BORDER, lw=1)
ax4.text(5, 2.7, '5 World Cups  (2010 - 2026)', fontsize=8, color=MUTE,
         ha='center', family='sans-serif')

# Score display
rnd_box(ax4, 2.5, 1.2, 5.0, 1.2, '#21262d', alpha=0.6)
flag_box(ax4, 3.0, 1.35, 'PT', w=0.7, h=0.35)
ax4.text(5.0, 1.8, '0  -  1', fontsize=20, ha='center',
         fontweight='bold', color=TEXT, family='monospace')
flag_box(ax4, 6.3, 1.35, 'SP', w=0.7, h=0.35)
ax4.text(5, 0.7, 'Portugal eliminated  |  Round of 16', fontsize=9,
         color=RED, ha='center', family='sans-serif')

# ── Footer ──
fig.text(0.5, 0.01,
         'Sources: BBC | ESPN | FOX Sports | The Guardian | Yahoo Sports    |    Generated July 6, 2026    |    Round of 16 LIVE',
         fontsize=7.5, color='#484f58', ha='center', family='sans-serif')

out = '/home/tong/workspace/pocket/fifa-2026-chart.png'
plt.savefig(out, dpi=150, facecolor=BG, bbox_inches='tight', pad_inches=0.3)
print(f'Done: {out}')
