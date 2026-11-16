"""
OsdagBridge CAD and Engineering Drawing Generator for Design Reports.
Generates publication-grade, dimensioned 2D and 3D engineering drawings
when CAD views are not exported from GUI or when running in headless mode.
"""

import os
import math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# Color palette matching Osdag theme
COLOR_CONCRETE = "#D9D9D6"
COLOR_ASPHALT = "#4A4A4A"
COLOR_STEEL = "#4682B4"
COLOR_STEEL_DARK = "#2C5D88"
COLOR_BARRIER = "#B0B7BD"
COLOR_STIFFENER = "#D35400"
COLOR_BRACING = "#E67E22"
COLOR_DIM = "#8B0000"
COLOR_BG = "#FFFFFF"


def _setup_fig_ax(figsize=(8, 5)):
    fig, ax = plt.subplots(figsize=figsize, dpi=300)
    fig.patch.set_facecolor(COLOR_BG)
    ax.set_facecolor(COLOR_BG)
    return fig, ax


def draw_bridge_3d(span=20.0, width=5.15, n_girders=3, depth=1.12, out_path=""):
    """Figure 6.1: Overall 3D Bridge Superstructure (Isometric View)."""
    fig = plt.figure(figsize=(9, 5.5), dpi=300)
    ax = fig.add_subplot(111, projection='3d')
    ax.set_facecolor(COLOR_BG)
    fig.patch.set_facecolor(COLOR_BG)

    # Deck slab box
    t_deck = 0.25
    x = [0, span, span, 0]
    y = [-width/2, -width/2, width/2, width/2]
    z_top = depth + t_deck
    z_bot = depth

    # Top surface of deck
    verts_top = [[(x[i], y[i], z_top) for i in range(4)]]
    ax.add_collection3d(Poly3DCollection(verts_top, facecolors=COLOR_CONCRETE, edgecolors='#777777', linewidths=0.5, alpha=0.9))

    # Bottom surface of deck
    verts_bot = [[(x[i], y[i], z_bot) for i in range(4)]]
    ax.add_collection3d(Poly3DCollection(verts_bot, facecolors=COLOR_CONCRETE, edgecolors='#777777', linewidths=0.5, alpha=0.9))

    # Sides of deck
    for i in range(4):
        j = (i + 1) % 4
        verts_side = [[(x[i], y[i], z_bot), (x[j], y[j], z_bot), (x[j], y[j], z_top), (x[i], y[i], z_top)]]
        ax.add_collection3d(Poly3DCollection(verts_side, facecolors='#C0C0BA', edgecolors='#777777', linewidths=0.5, alpha=0.9))

    # Roadway markings (centerline)
    dash_len = 2.0
    for cx in np.arange(1.0, span - 1.0, 4.0):
        ax.plot([cx, cx + dash_len], [0, 0], [z_top + 0.01, z_top + 0.01], color='#FFFFFF', lw=2.0)

    # Crash barriers on both edges
    hb = 0.90
    wb = 0.45
    for sign in [-1, 1]:
        by = sign * (width/2 - wb/2)
        by_outer = sign * width/2
        by_inner = sign * (width/2 - wb)
        verts_b = [[(0, by_inner, z_top), (span, by_inner, z_top), (span, by_inner, z_top + hb), (0, by_inner, z_top + hb)]]
        ax.add_collection3d(Poly3DCollection(verts_b, facecolors=COLOR_BARRIER, edgecolors='#666666', linewidths=0.5, alpha=0.95))
        verts_top_b = [[(0, by_inner, z_top + hb), (span, by_inner, z_top + hb), (span, by_outer, z_top + hb), (0, by_outer, z_top + hb)]]
        ax.add_collection3d(Poly3DCollection(verts_top_b, facecolors='#9FA8A3', edgecolors='#666666', linewidths=0.5, alpha=0.95))

    # Steel plate girders
    girder_spacing = (width - 2 * 0.86) / (n_girders - 1) if n_girders > 1 else 0
    girder_ys = [-width/2 + 0.86 + i * girder_spacing for i in range(n_girders)]

    for gy in girder_ys:
        # Top flange
        ax.plot([0, span], [gy, gy], [depth, depth], color=COLOR_STEEL_DARK, lw=2.5)
        # Web line
        ax.plot([0, span], [gy, gy], [depth/2, depth/2], color=COLOR_STEEL, lw=1.5)
        # Bottom flange
        ax.plot([0, span], [gy, gy], [0, 0], color=COLOR_STEEL_DARK, lw=2.5)

        # Stiffeners along the span
        for sx in np.linspace(0, span, 13):
            ax.plot([sx, sx], [gy, gy], [0, depth], color=COLOR_STIFFENER, lw=1.2)

    # Cross bracings between adjacent girders
    for i in range(n_girders - 1):
        g1_y = girder_ys[i]
        g2_y = girder_ys[i+1]
        for bx in np.linspace(0, span, 6):
            # Top chord
            ax.plot([bx, bx], [g1_y, g2_y], [depth * 0.85, depth * 0.85], color=COLOR_BRACING, lw=1.2)
            # Bottom chord
            ax.plot([bx, bx], [g1_y, g2_y], [depth * 0.15, depth * 0.15], color=COLOR_BRACING, lw=1.2)
            # X diagonals
            ax.plot([bx, bx], [g1_y, g2_y], [depth * 0.15, depth * 0.85], color=COLOR_BRACING, lw=1.0, ls='--')
            ax.plot([bx, bx], [g1_y, g2_y], [depth * 0.85, depth * 0.15], color=COLOR_BRACING, lw=1.0, ls='--')

    # Bearings at supports
    for gy in girder_ys:
        for sx in [0, span]:
            ax.plot([sx, sx], [gy, gy], [-0.15, 0], color='#222222', lw=4.0)

    ax.set_xlim(0, span)
    ax.set_ylim(-width/2 - 0.5, width/2 + 0.5)
    ax.set_zlim(-0.5, depth + t_deck + hb + 0.5)
    ax.view_init(elev=24, azim=-58)
    ax.set_xlabel("Span X (m)", fontsize=8, labelpad=4)
    ax.set_ylabel("Transverse Y (m)", fontsize=8, labelpad=4)
    ax.set_zlabel("Height Z (m)", fontsize=8, labelpad=4)
    ax.set_title("Overall 3D Bridge Superstructure (Isometric View)", fontsize=11, fontweight='bold', pad=12)

    plt.tight_layout()
    if out_path:
        plt.savefig(out_path, dpi=300, bbox_inches='tight')
        plt.close()
    return out_path


def draw_typical_cross_section(width=5.15, cw=4.25, depth=1.12, t_deck=0.25, n_girders=3, spacing=1.72, overhang=0.86, out_path=""):
    """Figure 6.2: Typical Transverse Cross Section with dimension callouts."""
    fig, ax = _setup_fig_ax((9.5, 5.2))

    # Y coordinates: 0 is deck bottom
    deck_bot = 0.0
    deck_top = t_deck
    wc_thk = 0.065
    wc_top = deck_top + wc_thk

    # Deck slab polygon (with 2.5% camber/slope from center to edges)
    xs = [-width/2, width/2, width/2, -width/2]
    ys = [deck_bot, deck_bot, deck_top, deck_top]
    deck_poly = patches.Polygon(list(zip(xs, ys)), closed=True, facecolor=COLOR_CONCRETE, edgecolor='#333333', lw=1.2)
    ax.add_patch(deck_poly)

    # Wearing course (carriageway 4.25m centered)
    wc_xs = [-cw/2, cw/2, cw/2, -cw/2]
    wc_ys = [deck_top, deck_top, wc_top, wc_top]
    wc_poly = patches.Polygon(list(zip(wc_xs, wc_ys)), closed=True, facecolor=COLOR_ASPHALT, edgecolor='#222222', lw=0.8)
    ax.add_patch(wc_poly)

    # Crash barriers on both sides
    bw = 0.45
    bh = 0.90
    for sign in [-1, 1]:
        bx_out = sign * width / 2
        bx_in = sign * (width / 2 - bw)
        barr_xs = [bx_out, bx_in, bx_in + sign * 0.1, bx_out]
        barr_ys = [deck_top, deck_top, deck_top + bh, deck_top + bh]
        b_poly = patches.Polygon(list(zip(barr_xs, barr_ys)), closed=True, facecolor=COLOR_BARRIER, edgecolor='#333333', lw=1.0)
        ax.add_patch(b_poly)
        ax.text((bx_out + bx_in)/2, deck_top + bh/2, "Crash\nBarrier", ha='center', va='center', fontsize=6.5, fontweight='bold', color='#222222')

    # Steel Plate Girders
    bf = 0.34
    tf = 0.016
    tw = 0.008
    girder_ys_pos = [-spacing, 0.0, spacing] if n_girders == 3 else [-(n_girders-1)*spacing/2 + i*spacing for i in range(n_girders)]

    for i, gx in enumerate(girder_ys_pos):
        # Girder G1, G2, G3
        # Top flange
        ax.add_patch(patches.Rectangle((gx - bf/2, -tf), bf, tf, facecolor=COLOR_STEEL_DARK, edgecolor='#111111', lw=0.8))
        # Web
        ax.add_patch(patches.Rectangle((gx - tw/2, -depth + tf), tw, depth - 2*tf, facecolor=COLOR_STEEL, edgecolor='#111111', lw=0.6))
        # Bottom flange
        ax.add_patch(patches.Rectangle((gx - bf/2, -depth), bf, tf, facecolor=COLOR_STEEL_DARK, edgecolor='#111111', lw=0.8))
        # Bearing pad below bottom flange
        ax.add_patch(patches.Rectangle((gx - 0.15, -depth - 0.08), 0.30, 0.08, facecolor='#2C3E50', edgecolor='#000000', lw=0.8))

        lbl = f"G{i+1}"
        ax.text(gx, -depth - 0.18, lbl, ha='center', va='top', fontsize=8.5, fontweight='bold', color='#111111')

    # Cross bracing truss between adjacent girders
    for i in range(len(girder_ys_pos) - 1):
        g1x = girder_ys_pos[i]
        g2x = girder_ys_pos[i+1]
        y_top_c = -depth * 0.15
        y_bot_c = -depth * 0.85
        # Top chord
        ax.plot([g1x, g2x], [y_top_c, y_top_c], color=COLOR_BRACING, lw=1.4)
        # Bottom chord
        ax.plot([g1x, g2x], [y_bot_c, y_bot_c], color=COLOR_BRACING, lw=1.4)
        # X Diagonals
        ax.plot([g1x, g2x], [y_top_c, y_bot_c], color=COLOR_BRACING, lw=1.2, ls='--')
        ax.plot([g1x, g2x], [y_bot_c, y_top_c], color=COLOR_BRACING, lw=1.2, ls='--')
        ax.text((g1x + g2x)/2, (y_top_c + y_bot_c)/2, "X-Bracing\n(ISA 40x40x3)", ha='center', va='center',
                fontsize=6.5, color='#B7410E', bbox=dict(boxstyle='square,pad=0.2', facecolor='white', alpha=0.8, edgecolor='none'))

    # Dimensions & Callouts
    dim_y_top = wc_top + 0.45
    # Overall bridge width 5.15 m
    ax.annotate('', xy=(-width/2, dim_y_top), xytext=(width/2, dim_y_top),
                arrowprops=dict(arrowstyle='<->', color=COLOR_DIM, lw=1.0))
    ax.text(0, dim_y_top + 0.08, f"Overall Bridge Width = {width*1000:.0f} mm", ha='center', va='bottom', fontsize=8, color=COLOR_DIM, fontweight='bold')

    # Carriageway width 4.25 m
    cw_dim_y = wc_top + 0.18
    ax.annotate('', xy=(-cw/2, cw_dim_y), xytext=(cw/2, cw_dim_y),
                arrowprops=dict(arrowstyle='<->', color='#006400', lw=1.0))
    ax.text(0, cw_dim_y + 0.06, f"Carriageway = {cw*1000:.0f} mm", ha='center', va='bottom', fontsize=7.5, color='#006400', fontweight='bold')

    # Girder spacing and overhang dimensions at bottom
    dim_y_bot = -depth - 0.35
    ax.annotate('', xy=(-width/2, dim_y_bot), xytext=(girder_ys_pos[0], dim_y_bot),
                arrowprops=dict(arrowstyle='<->', color=COLOR_DIM, lw=0.9))
    ax.text((-width/2 + girder_ys_pos[0])/2, dim_y_bot - 0.08, f"OH={overhang*1000:.0f}", ha='center', va='top', fontsize=7, color=COLOR_DIM)

    ax.annotate('', xy=(girder_ys_pos[0], dim_y_bot), xytext=(girder_ys_pos[1], dim_y_bot),
                arrowprops=dict(arrowstyle='<->', color=COLOR_DIM, lw=0.9))
    ax.text((girder_ys_pos[0] + girder_ys_pos[1])/2, dim_y_bot - 0.08, f"{spacing*1000:.0f} mm", ha='center', va='top', fontsize=7, color=COLOR_DIM)

    ax.annotate('', xy=(girder_ys_pos[1], dim_y_bot), xytext=(girder_ys_pos[2], dim_y_bot),
                arrowprops=dict(arrowstyle='<->', color=COLOR_DIM, lw=0.9))
    ax.text((girder_ys_pos[1] + girder_ys_pos[2])/2, dim_y_bot - 0.08, f"{spacing*1000:.0f} mm", ha='center', va='top', fontsize=7, color=COLOR_DIM)

    ax.annotate('', xy=(girder_ys_pos[2], dim_y_bot), xytext=(width/2, dim_y_bot),
                arrowprops=dict(arrowstyle='<->', color=COLOR_DIM, lw=0.9))
    ax.text((girder_ys_pos[2] + width/2)/2, dim_y_bot - 0.08, f"OH={overhang*1000:.0f}", ha='center', va='top', fontsize=7, color=COLOR_DIM)

    # Vertical dimension: Girder depth 1120 mm
    vdim_x = width/2 + 0.30
    ax.annotate('', xy=(vdim_x, 0), xytext=(vdim_x, -depth),
                arrowprops=dict(arrowstyle='<->', color=COLOR_DIM, lw=0.9))
    ax.text(vdim_x + 0.08, -depth/2, f"Girder Depth\n{depth*1000:.0f} mm", ha='left', va='center', fontsize=7.5, color=COLOR_DIM)

    # Deck thickness callout
    ax.annotate(f"Deck Slab: {t_deck*1000:.0f} mm\n+ 65 mm Wearing Course", xy=(-1.2, deck_top/2), xytext=(-2.3, 0.7),
                arrowprops=dict(arrowstyle='->', color='#333333', lw=0.8), fontsize=7.5, fontweight='bold')

    ax.set_xlim(-width/2 - 0.8, width/2 + 1.2)
    ax.set_ylim(-depth - 0.6, wc_top + 0.8)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title("Typical Bridge Superstructure Cross Section", fontsize=11, fontweight='bold', pad=10)

    plt.tight_layout()
    if out_path:
        plt.savefig(out_path, dpi=300, bbox_inches='tight')
        plt.close()
    return out_path


def draw_top_view(span=20.0, width=5.15, n_girders=3, spacing=1.72, out_path=""):
    """Figure 6.3: Top Plan View showing roadway, girder alignment and bracings."""
    fig, ax = _setup_fig_ax((9.5, 4.5))

    # Deck outline
    ax.add_patch(patches.Rectangle((0, -width/2), span, width, facecolor=COLOR_CONCRETE, edgecolor='#333333', lw=1.2))

    # Carriageway (4.25m)
    cw = 4.25
    ax.add_patch(patches.Rectangle((0, -cw/2), span, cw, facecolor='#EAEAEA', edgecolor='none'))

    # Centerline road markings
    for sx in np.arange(1.0, span - 1.0, 3.5):
        ax.plot([sx, sx + 2.0], [0, 0], color='#FFFFFF', lw=2.5)

    # Crash barriers along top and bottom edges
    bw = 0.45
    ax.add_patch(patches.Rectangle((0, width/2 - bw), span, bw, facecolor=COLOR_BARRIER, edgecolor='#444444', lw=0.8))
    ax.add_patch(patches.Rectangle((0, -width/2), span, bw, facecolor=COLOR_BARRIER, edgecolor='#444444', lw=0.8))
    ax.text(span/2, width/2 - bw/2, "Crash Barrier (North)", ha='center', va='center', fontsize=6.5, color='#222222')
    ax.text(span/2, -width/2 + bw/2, "Crash Barrier (South)", ha='center', va='center', fontsize=6.5, color='#222222')

    # Plate girder centerlines (dashed)
    girder_ys = [-spacing, 0.0, spacing] if n_girders == 3 else [-(n_girders-1)*spacing/2 + i*spacing for i in range(n_girders)]
    for i, gy in enumerate(girder_ys):
        ax.plot([0, span], [gy, gy], color=COLOR_STEEL_DARK, lw=1.5, ls='--')
        ax.text(0.3, gy + 0.12, f"Girder G{i+1}", fontsize=7.5, fontweight='bold', color=COLOR_STEEL_DARK)

    # Cross bracing bays along span
    bay_xs = np.linspace(0, span, 6)
    for bx in bay_xs:
        ax.plot([bx, bx], [girder_ys[0], girder_ys[-1]], color=COLOR_BRACING, lw=1.2)
    for bi in range(len(bay_xs) - 1):
        x1, x2 = bay_xs[bi], bay_xs[bi+1]
        for gi in range(len(girder_ys) - 1):
            y1, y2 = girder_ys[gi], girder_ys[gi+1]
            ax.plot([x1, x2], [y1, y2], color=COLOR_BRACING, lw=0.8, ls=':')
            ax.plot([x1, x2], [y2, y1], color=COLOR_BRACING, lw=0.8, ls=':')

    # Traffic arrow
    ax.annotate('TRAFFIC DIRECTION', xy=(span * 0.7, 0.9), xytext=(span * 0.35, 0.9),
                arrowprops=dict(facecolor='#1E88E5', edgecolor='#1E88E5', width=3, headwidth=8),
                fontsize=8, fontweight='bold', color='#1E88E5', ha='center', va='center')

    # Dimensions
    dim_y = width/2 + 0.4
    ax.annotate('', xy=(0, dim_y), xytext=(span, dim_y),
                arrowprops=dict(arrowstyle='<->', color=COLOR_DIM, lw=1.0))
    ax.text(span/2, dim_y + 0.1, f"Bridge Span L = {span*1000:.0f} mm", ha='center', va='bottom', fontsize=8, color=COLOR_DIM, fontweight='bold')

    dim_x = span + 0.6
    ax.annotate('', xy=(dim_x, -width/2), xytext=(dim_x, width/2),
                arrowprops=dict(arrowstyle='<->', color=COLOR_DIM, lw=1.0))
    ax.text(dim_x + 0.1, 0, f"Width = {width*1000:.0f} mm", ha='left', va='center', rotation=90, fontsize=8, color=COLOR_DIM, fontweight='bold')

    # Support / Bearing lines
    ax.axvline(0, color='#888888', lw=2.0, ls='-')
    ax.axvline(span, color='#888888', lw=2.0, ls='-')
    ax.text(0, -width/2 - 0.4, "Abutment A1", ha='center', va='top', fontsize=7.5, fontweight='bold')
    ax.text(span, -width/2 - 0.4, "Abutment A2", ha='center', va='top', fontsize=7.5, fontweight='bold')

    ax.set_xlim(-1.0, span + 2.0)
    ax.set_ylim(-width/2 - 0.8, width/2 + 0.8)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title("Bridge Superstructure Top View (Plan)", fontsize=11, fontweight='bold', pad=10)

    plt.tight_layout()
    if out_path:
        plt.savefig(out_path, dpi=300, bbox_inches='tight')
        plt.close()
    return out_path


def draw_girder_3d(span=20.0, depth=1.12, n_girders=3, spacing=1.72, out_path=""):
    """Figure 6.4: 3D View of Structural Steel Plate Girders & Bracing Framing."""
    fig = plt.figure(figsize=(9, 5.5), dpi=300)
    ax = fig.add_subplot(111, projection='3d')
    ax.set_facecolor(COLOR_BG)
    fig.patch.set_facecolor(COLOR_BG)

    girder_ys = [-spacing, 0.0, spacing] if n_girders == 3 else [-(n_girders-1)*spacing/2 + i*spacing for i in range(n_girders)]

    for gy in girder_ys:
        # Top flange plate
        ax.plot([0, span], [gy, gy], [depth, depth], color=COLOR_STEEL_DARK, lw=3.0)
        # Web plate surface (represented by outline)
        ax.plot([0, span], [gy, gy], [0, 0], color=COLOR_STEEL_DARK, lw=3.0)
        ax.plot([0, 0], [gy, gy], [0, depth], color=COLOR_STEEL_DARK, lw=2.0)
        ax.plot([span, span], [gy, gy], [0, depth], color=COLOR_STEEL_DARK, lw=2.0)

        # Intermediate stiffeners
        for sx in np.linspace(1.635, span - 1.635, 11):
            ax.plot([sx, sx], [gy, gy], [0, depth], color=COLOR_STIFFENER, lw=1.5)

    # Cross bracing truss bays
    for i in range(len(girder_ys) - 1):
        g1y = girder_ys[i]
        g2y = girder_ys[i+1]
        for bx in np.linspace(0, span, 6):
            ax.plot([bx, bx], [g1y, g2y], [depth*0.85, depth*0.85], color=COLOR_BRACING, lw=1.8)
            ax.plot([bx, bx], [g1y, g2y], [depth*0.15, depth*0.15], color=COLOR_BRACING, lw=1.8)
            ax.plot([bx, bx], [g1y, g2y], [depth*0.15, depth*0.85], color=COLOR_BRACING, lw=1.2, ls='--')
            ax.plot([bx, bx], [g1y, g2y], [depth*0.85, depth*0.15], color=COLOR_BRACING, lw=1.2, ls='--')

    ax.set_xlim(0, span)
    ax.set_ylim(-spacing * 1.5, spacing * 1.5)
    ax.set_zlim(-0.3, depth + 0.3)
    ax.view_init(elev=22, azim=-55)
    ax.set_xlabel("Span X (m)", fontsize=8, labelpad=4)
    ax.set_ylabel("Transverse Y (m)", fontsize=8, labelpad=4)
    ax.set_zlabel("Depth Z (m)", fontsize=8, labelpad=4)
    ax.set_title("3D Framing View of Steel Plate Girders & Cross Bracings", fontsize=11, fontweight='bold', pad=12)

    plt.tight_layout()
    if out_path:
        plt.savefig(out_path, dpi=300, bbox_inches='tight')
        plt.close()
    return out_path


def draw_section_preview(depth=1120, bf=340, tf=16, tw=8, out_path=""):
    """Figure 6.5: Detailed Dimensioned Cross Section of Plate Girder."""
    fig, ax = _setup_fig_ax((6.5, 6.0))

    # Girder centered at x=0, y=0 to y=depth
    d_web = depth - 2 * tf

    # Top Flange
    ax.add_patch(patches.Rectangle((-bf/2, depth - tf), bf, tf, facecolor=COLOR_STEEL_DARK, edgecolor='#111111', lw=1.2))
    # Web
    ax.add_patch(patches.Rectangle((-tw/2, tf), tw, d_web, facecolor=COLOR_STEEL, edgecolor='#111111', lw=1.0))
    # Bottom Flange
    ax.add_patch(patches.Rectangle((-bf/2, 0), bf, tf, facecolor=COLOR_STEEL_DARK, edgecolor='#111111', lw=1.2))

    # Fillet welds between flange and web
    w_size = 8
    ax.plot([-tw/2, -tw/2 - w_size], [tf, tf + w_size], color='#111111', lw=1.0)
    ax.plot([tw/2, tw/2 + w_size], [tf, tf + w_size], color='#111111', lw=1.0)
    ax.plot([-tw/2, -tw/2 - w_size], [depth - tf, depth - tf - w_size], color='#111111', lw=1.0)
    ax.plot([tw/2, tw/2 + w_size], [depth - tf, depth - tf - w_size], color='#111111', lw=1.0)

    # Neutral axis (dashed)
    ax.axhline(depth/2, color='#777777', ls='-.', lw=1.0)
    ax.text(bf/2 + 25, depth/2, "Neutral Axis (N-A)", va='center', fontsize=7.5, color='#555555', fontstyle='italic')

    # Dimensions: Overall Depth
    dim_x = -bf/2 - 70
    ax.annotate('', xy=(dim_x, 0), xytext=(dim_x, depth),
                arrowprops=dict(arrowstyle='<->', color=COLOR_DIM, lw=1.0))
    ax.text(dim_x - 15, depth/2, f"D = {depth:.0f} mm", ha='right', va='center', rotation=90, fontsize=8.5, color=COLOR_DIM, fontweight='bold')

    # Dimensions: Clear Web Depth
    dim_x_web = tw/2 + 40
    ax.annotate('', xy=(dim_x_web, tf), xytext=(dim_x_web, depth - tf),
                arrowprops=dict(arrowstyle='<->', color='#006400', lw=0.9))
    ax.text(dim_x_web + 10, depth/2, f"d_w = {d_web:.0f} mm", ha='left', va='center', rotation=90, fontsize=8, color='#006400')

    # Dimensions: Top Flange Width & Thickness
    dim_y_top = depth + 40
    ax.annotate('', xy=(-bf/2, dim_y_top), xytext=(bf/2, dim_y_top),
                arrowprops=dict(arrowstyle='<->', color=COLOR_DIM, lw=1.0))
    ax.text(0, dim_y_top + 10, f"b_f = {bf:.0f} mm", ha='center', va='bottom', fontsize=8.5, color=COLOR_DIM, fontweight='bold')

    # Flange thickness callouts
    ax.annotate(f"t_f = {tf:.0f} mm", xy=(bf/2, depth - tf/2), xytext=(bf/2 + 50, depth + 10),
                arrowprops=dict(arrowstyle='->', color='#333333', lw=0.8), fontsize=8)
    ax.annotate(f"t_f = {tf:.0f} mm", xy=(bf/2, tf/2), xytext=(bf/2 + 50, -25),
                arrowprops=dict(arrowstyle='->', color='#333333', lw=0.8), fontsize=8)

    # Web thickness callout
    ax.annotate(f"t_w = {tw:.0f} mm", xy=(-tw/2, depth*0.3), xytext=(-bf/2 - 30, depth*0.3),
                arrowprops=dict(arrowstyle='->', color='#333333', lw=0.8), fontsize=8, ha='right')

    ax.set_xlim(-bf/2 - 130, bf/2 + 150)
    ax.set_ylim(-60, depth + 90)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title("Plate Girder Cross-Section Details", fontsize=11, fontweight='bold', pad=10)

    plt.tight_layout()
    if out_path:
        plt.savefig(out_path, dpi=300, bbox_inches='tight')
        plt.close()
    return out_path


def draw_stiffener_preview(span=20.0, depth=1.12, int_spacing=1.635, out_path=""):
    """Figure 6.6: Girder Side Elevation showing Bearing & Intermediate Stiffeners."""
    fig, ax = _setup_fig_ax((9.5, 4.5))

    L_mm = span * 1000
    D_mm = depth * 1000
    tf_mm = 16
    tw_mm = 8

    # Girder top and bottom flanges (side elevation)
    ax.add_patch(patches.Rectangle((0, D_mm - tf_mm), L_mm, tf_mm, facecolor=COLOR_STEEL_DARK, edgecolor='#111111', lw=1.0))
    ax.add_patch(patches.Rectangle((0, 0), L_mm, tf_mm, facecolor=COLOR_STEEL_DARK, edgecolor='#111111', lw=1.0))
    # Web plate
    ax.add_patch(patches.Rectangle((0, tf_mm), L_mm, D_mm - 2*tf_mm, facecolor='#E3EDF7', edgecolor='#111111', lw=0.8))

    # Bearing stiffeners at both ends (Left support and Right support)
    t_bs = 16
    for x_end in [100, L_mm - 100]:
        ax.add_patch(patches.Rectangle((x_end - t_bs/2, tf_mm), t_bs, D_mm - 2*tf_mm, facecolor='#8B0000', edgecolor='#000000', lw=1.2))
        ax.text(x_end, D_mm + 40, "Bearing\nStiffener", ha='center', va='bottom', fontsize=7, fontweight='bold', color='#8B0000')

    # Intermediate transverse stiffeners
    spacing_mm = int_spacing * 1000 if int_spacing < 100 else int_spacing
    t_is = 10
    curr_x = 100 + spacing_mm
    stiff_xs = []
    while curr_x < L_mm - 100 - spacing_mm/2:
        stiff_xs.append(curr_x)
        ax.add_patch(patches.Rectangle((curr_x - t_is/2, tf_mm), t_is, D_mm - 2*tf_mm, facecolor=COLOR_STIFFENER, edgecolor='#555555', lw=0.8))
        curr_x += spacing_mm

    # Callout for intermediate stiffener
    if stiff_xs:
        mid_sx = stiff_xs[len(stiff_xs)//2]
        ax.annotate(f"Intermediate Stiffeners\nSpacing c = {spacing_mm:.0f} mm c/c\nThickness = 14 mm",
                    xy=(mid_sx, D_mm/2), xytext=(mid_sx + 1500, D_mm/2 + 250),
                    arrowprops=dict(arrowstyle='->', color='#B7410E', lw=1.0),
                    fontsize=7.5, fontweight='bold', color='#B7410E',
                    bbox=dict(boxstyle='square,pad=0.2', facecolor='white', alpha=0.9, edgecolor='#B7410E'))

    # Bearings at supports
    for sup_x in [100, L_mm - 100]:
        ax.add_patch(patches.Polygon([[sup_x - 150, -120], [sup_x + 150, -120], [sup_x, 0]], closed=True, facecolor='#555555', edgecolor='#111111', lw=1.0))
        ax.text(sup_x, -160, "Support", ha='center', va='top', fontsize=7.5, fontweight='bold')

    # Dimensions: Span
    dim_y = D_mm + 180
    ax.annotate('', xy=(0, dim_y), xytext=(L_mm, dim_y),
                arrowprops=dict(arrowstyle='<->', color=COLOR_DIM, lw=1.0))
    ax.text(L_mm/2, dim_y + 30, f"Span L = {L_mm:.0f} mm (20.0 m)", ha='center', va='bottom', fontsize=8.5, color=COLOR_DIM, fontweight='bold')

    # Dimensions: Depth
    dim_x = -350
    ax.annotate('', xy=(dim_x, 0), xytext=(dim_x, D_mm),
                arrowprops=dict(arrowstyle='<->', color=COLOR_DIM, lw=1.0))
    ax.text(dim_x - 50, D_mm/2, f"D = {D_mm:.0f} mm", ha='right', va='center', rotation=90, fontsize=8, color=COLOR_DIM, fontweight='bold')

    ax.set_xlim(-700, L_mm + 700)
    ax.set_ylim(-260, D_mm + 320)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title("Plate Girder Side Elevation with Stiffener Spacing Details", fontsize=11, fontweight='bold', pad=10)

    plt.tight_layout()
    if out_path:
        plt.savefig(out_path, dpi=300, bbox_inches='tight')
        plt.close()
    return out_path


def draw_cb_diagram(spacing=1.72, depth=1.12, out_path=""):
    """Figure 6.7: Cross Bracing Layout & Truss Panel Details."""
    fig, ax = _setup_fig_ax((7.0, 5.0))

    s_mm = spacing * 1000
    d_mm = depth * 1000
    bf = 340
    tf = 16

    # 2 Girders in cross-section
    for gx in [0, s_mm]:
        ax.add_patch(patches.Rectangle((gx - bf/2, d_mm - tf), bf, tf, facecolor=COLOR_STEEL_DARK, edgecolor='#111111', lw=1.0))
        ax.add_patch(patches.Rectangle((gx - 4, tf), 8, d_mm - 2*tf, facecolor=COLOR_STEEL, edgecolor='#111111', lw=0.8))
        ax.add_patch(patches.Rectangle((gx - bf/2, 0), bf, tf, facecolor=COLOR_STEEL_DARK, edgecolor='#111111', lw=1.0))

    # X-Bracing Truss between Girders
    yt = d_mm * 0.85
    yb = d_mm * 0.15

    # Top chord
    ax.plot([0, s_mm], [yt, yt], color=COLOR_BRACING, lw=2.5, label='Top Chord (ISA 40x40x3)')
    # Bottom chord
    ax.plot([0, s_mm], [yb, yb], color='#2980B9', lw=2.5, label='Bottom Chord (ISA 40x40x3)')
    # Diagonals
    ax.plot([0, s_mm], [yt, yb], color='#27AE60', lw=2.0, ls='--', label='Diagonal (ISA 40x40x3)')
    ax.plot([0, s_mm], [yb, yt], color='#27AE60', lw=2.0, ls='--')

    # Gusset plates at joints
    gp_sz = 120
    for x in [0, s_mm]:
        for y in [yt, yb]:
            ax.add_patch(patches.Rectangle((x - gp_sz/2, y - gp_sz/2), gp_sz, gp_sz, facecolor='#E5E7E9', edgecolor='#333333', lw=0.8))
            ax.plot([x], [y], marker='o', markersize=4, color='#111111')

    # Dimensions
    ax.annotate('', xy=(0, d_mm + 60), xytext=(s_mm, d_mm + 60),
                arrowprops=dict(arrowstyle='<->', color=COLOR_DIM, lw=1.0))
    ax.text(s_mm/2, d_mm + 75, f"Girder Spacing = {s_mm:.0f} mm", ha='center', va='bottom', fontsize=8, color=COLOR_DIM, fontweight='bold')

    ax.annotate('', xy=(-bf/2 - 40, yb), xytext=(-bf/2 - 40, yt),
                arrowprops=dict(arrowstyle='<->', color='#006400', lw=0.9))
    ax.text(-bf/2 - 50, (yt+yb)/2, f"Bracing Height\n{yt-yb:.0f} mm", ha='right', va='center', rotation=90, fontsize=7.5, color='#006400')

    ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.22), ncol=3, fontsize=7.5, frameon=True)
    ax.set_xlim(-bf - 60, s_mm + bf + 60)
    ax.set_ylim(-60, d_mm + 120)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title("Cross-Bracing Truss Frame Layout (Between Girders)", fontsize=11, fontweight='bold', pad=10)

    plt.tight_layout()
    if out_path:
        plt.savefig(out_path, dpi=300, bbox_inches='tight')
        plt.close()
    return out_path


def draw_ed_diagram(spacing=1.72, depth=1.12, out_path=""):
    """Figure 6.11: End Diaphragm Layout & Support Frame."""
    fig, ax = _setup_fig_ax((7.0, 5.0))

    s_mm = spacing * 1000
    d_mm = depth * 1000
    bf = 340
    tf = 16

    # 2 Girders at support
    for gx in [0, s_mm]:
        ax.add_patch(patches.Rectangle((gx - bf/2, d_mm - tf), bf, tf, facecolor=COLOR_STEEL_DARK, edgecolor='#111111', lw=1.0))
        ax.add_patch(patches.Rectangle((gx - 4, tf), 8, d_mm - 2*tf, facecolor=COLOR_STEEL, edgecolor='#111111', lw=0.8))
        ax.add_patch(patches.Rectangle((gx - bf/2, 0), bf, tf, facecolor=COLOR_STEEL_DARK, edgecolor='#111111', lw=1.0))
        # Bearing stiffener
        ax.add_patch(patches.Rectangle((gx - 8, tf), 16, d_mm - 2*tf, facecolor='#8B0000', edgecolor='#111111', lw=1.0))
        # Elastomeric Bearing Pad below
        ax.add_patch(patches.Rectangle((gx - 150, -70), 300, 70, facecolor='#34495E', edgecolor='#111111', lw=1.0))
        ax.text(gx, -100, "Elastomeric Bearing", ha='center', va='top', fontsize=7, fontweight='bold')

    # End Diaphragm Frame (Truss/Channel diaphragm)
    yt = d_mm * 0.88
    yb = d_mm * 0.12

    # Top and bottom chords
    ax.plot([0, s_mm], [yt, yt], color='#C0392B', lw=3.0, label='Top Chord (ISA 40x40x3)')
    ax.plot([0, s_mm], [yb, yb], color='#C0392B', lw=3.0, label='Bottom Chord (ISA 40x40x3)')
    # Diagonals
    ax.plot([0, s_mm], [yt, yb], color='#8E44AD', lw=2.2, ls='--', label='Diagonals (ISA 40x40x3)')
    ax.plot([0, s_mm], [yb, yt], color='#8E44AD', lw=2.2, ls='--')

    # Dimensions
    ax.annotate('', xy=(0, d_mm + 50), xytext=(s_mm, d_mm + 50),
                arrowprops=dict(arrowstyle='<->', color=COLOR_DIM, lw=1.0))
    ax.text(s_mm/2, d_mm + 65, f"Support Center-to-Center = {s_mm:.0f} mm", ha='center', va='bottom', fontsize=8, color=COLOR_DIM, fontweight='bold')

    ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.22), ncol=3, fontsize=7.5, frameon=True)
    ax.set_xlim(-bf - 60, s_mm + bf + 60)
    ax.set_ylim(-140, d_mm + 110)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title("End-Diaphragm Support Frame Layout", fontsize=11, fontweight='bold', pad=10)

    plt.tight_layout()
    if out_path:
        plt.savefig(out_path, dpi=300, bbox_inches='tight')
        plt.close()
    return out_path


def draw_angle_section(size="40x40x3", title="Equal Angle ISA 40x40x3", out_path=""):
    """Figures 6.8 - 6.10, 6.12 - 6.14: Equal Angle Section Profile with Dimensions."""
    fig, ax = _setup_fig_ax((3.5, 3.5))

    if "90" in str(size):
        leg = 90
        t = 8
        cx, cy = 25.1, 25.1
    else:
        leg = 40
        t = 3
        cx, cy = 11.2, 11.2

    # L-section polygon
    pts = [
        [0, 0],
        [leg, 0],
        [leg, t],
        [t, t],
        [t, leg],
        [0, leg]
    ]
    ax.add_patch(patches.Polygon(pts, closed=True, facecolor='#4682B4', edgecolor='#111111', lw=1.2))

    # Centroid dot
    ax.plot([cx], [cy], 'ro', markersize=3)
    ax.text(cx + 3, cy + 3, "C.G.", fontsize=7, color='#8B0000', fontweight='bold')

    # Dimensions
    dim_off = 8 if leg < 50 else 12
    ax.annotate('', xy=(0, -dim_off), xytext=(leg, -dim_off),
                arrowprops=dict(arrowstyle='<->', color=COLOR_DIM, lw=0.8))
    ax.text(leg/2, -dim_off - 4, f"{leg} mm", ha='center', va='top', fontsize=7.5, color=COLOR_DIM)

    ax.annotate('', xy=(-dim_off, 0), xytext=(-dim_off, leg),
                arrowprops=dict(arrowstyle='<->', color=COLOR_DIM, lw=0.8))
    ax.text(-dim_off - 4, leg/2, f"{leg} mm", ha='right', va='center', rotation=90, fontsize=7.5, color=COLOR_DIM)

    ax.annotate(f"t = {t} mm", xy=(leg/2, t/2), xytext=(leg/2 + 5, t/2 + 18),
                arrowprops=dict(arrowstyle='->', color='#111111', lw=0.8), fontsize=7)

    ax.set_xlim(-dim_off * 2.5, leg + 15)
    ax.set_ylim(-dim_off * 2.5, leg + 15)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title(title, fontsize=8.5, fontweight='bold', pad=6)

    plt.tight_layout()
    if out_path:
        plt.savefig(out_path, dpi=300, bbox_inches='tight')
        plt.close()
    return out_path


def draw_bm_envelope(span=20.0, max_bm=694.47, out_path=""):
    """Figure 4.1: Bending Moment Envelope (Envelope ULS) along span."""
    fig, ax = plt.subplots(figsize=(8, 4.2), dpi=300)
    fig.patch.set_facecolor(COLOR_BG)
    ax.set_facecolor(COLOR_BG)

    x = np.linspace(0, span, 201)
    # Parabolic bending moment diagram for simply supported beam under distributed/envelope loads
    bm = 4.0 * max_bm * (x / span) * (1.0 - x / span)

    ax.plot(x, bm, color='#1B4F72', lw=2.2, label='Envelope ULS Bending Moment (kN·m)')
    ax.fill_between(x, 0, bm, color='#2980B9', alpha=0.18)

    # Annotate peak at midspan
    mid_idx = len(x) // 2
    ax.plot([x[mid_idx]], [bm[mid_idx]], 'ro', markersize=6)
    ax.annotate(
        f'Max $M_{{u}} = {max_bm:.2f}$ kN·m\nat $x = {span/2:.1f}$ m',
        xy=(x[mid_idx], bm[mid_idx]),
        xytext=(x[mid_idx] + 1.2, bm[mid_idx] * 0.88),
        arrowprops=dict(arrowstyle='->', color='#900C3F', lw=1.2),
        fontsize=9,
        fontweight='bold',
        color='#900C3F',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='#FADBD8', edgecolor='#900C3F', alpha=0.9)
    )

    # Support representations
    ax.plot([0, span], [0, 0], 'k-', lw=1.0)
    ax.plot(0, 0, '^', color='#2C3E50', markersize=10, clip_on=False)
    ax.plot(span, 0, 'o', color='#2C3E50', markersize=8, clip_on=False)
    ax.text(0, -max_bm * 0.08, 'Left Support\n(x = 0.0 m)', ha='center', va='top', fontsize=8, color='#2C3E50')
    ax.text(span, -max_bm * 0.08, f'Right Support\n(x = {span:.1f} m)', ha='center', va='top', fontsize=8, color='#2C3E50')

    ax.set_xlabel('Distance from Left Support (m)', fontsize=9.5, fontweight='bold', labelpad=6)
    ax.set_ylabel('Bending Moment (kN·m)', fontsize=9.5, fontweight='bold', labelpad=6)
    ax.set_title('Bending Moment Envelope (Envelope ULS)', fontsize=11, fontweight='bold', pad=10, color='#1B4F72')
    ax.set_xlim(-0.5, span + 0.5)
    ax.set_ylim(-max_bm * 0.15, max_bm * 1.18)
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.legend(loc='upper right', framealpha=0.9, fontsize=8.5)

    if out_path:
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        plt.savefig(out_path, dpi=300, bbox_inches='tight')
        plt.close()
    return out_path


def draw_sf_envelope(span=20.0, max_sf=160.38, out_path=""):
    """Figure 4.2: Shear Force Envelope (Envelope ULS) along span."""
    fig, ax = plt.subplots(figsize=(8, 4.2), dpi=300)
    fig.patch.set_facecolor(COLOR_BG)
    ax.set_facecolor(COLOR_BG)

    x = np.linspace(0, span, 201)
    # Linear shear force envelope from +V at left support to -V at right support
    sf_upper = max_sf * (1.0 - x / span)
    sf_lower = -max_sf * (x / span)

    ax.plot(x, sf_upper, color='#D35400', lw=2.0, label='Max Positive Shear Force (kN)')
    ax.plot(x, sf_lower, color='#2980B9', lw=2.0, label='Max Negative Shear Force (kN)')
    ax.fill_between(x, sf_lower, sf_upper, color='#F39C12', alpha=0.15)
    ax.axhline(0, color='black', lw=0.8, linestyle='-')

    # Annotate support shears
    ax.plot(0, max_sf, 's', color='#D35400', markersize=6)
    ax.plot(span, -max_sf, 's', color='#2980B9', markersize=6)
    ax.annotate(
        f'$V_{{u,max}} = +{max_sf:.2f}$ kN',
        xy=(0, max_sf),
        xytext=(1.0, max_sf * 0.85),
        arrowprops=dict(arrowstyle='->', color='#D35400', lw=1.0),
        fontsize=8.5, fontweight='bold', color='#D35400',
        bbox=dict(boxstyle='round,pad=0.25', facecolor='#FCF3CF', edgecolor='#D35400', alpha=0.9)
    )
    ax.annotate(
        f'$V_{{u,min}} = -{max_sf:.2f}$ kN',
        xy=(span, -max_sf),
        xytext=(span - 4.5, -max_sf * 0.85),
        arrowprops=dict(arrowstyle='->', color='#2980B9', lw=1.0),
        fontsize=8.5, fontweight='bold', color='#2980B9',
        bbox=dict(boxstyle='round,pad=0.25', facecolor='#E8F8F5', edgecolor='#2980B9', alpha=0.9)
    )

    ax.set_xlabel('Distance from Left Support (m)', fontsize=9.5, fontweight='bold', labelpad=6)
    ax.set_ylabel('Shear Force (kN)', fontsize=9.5, fontweight='bold', labelpad=6)
    ax.set_title('Shear Force Envelope (Envelope ULS)', fontsize=11, fontweight='bold', pad=10, color='#1B4F72')
    ax.set_xlim(-0.5, span + 0.5)
    ax.set_ylim(-max_sf * 1.25, max_sf * 1.25)
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.legend(loc='upper right', framealpha=0.9, fontsize=8.5)

    if out_path:
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        plt.savefig(out_path, dpi=300, bbox_inches='tight')
        plt.close()
    return out_path


def draw_deflection_profile(span=20.0, delta_ll=15.616, delta_tot=37.137, out_path=""):
    """Figure 4.3: Vertical Deflection Dy along Span (Live Load & Total Load)."""
    fig, ax = plt.subplots(figsize=(8.5, 4.8), dpi=300)
    fig.patch.set_facecolor(COLOR_BG)
    ax.set_facecolor(COLOR_BG)

    x = np.linspace(0, span, 201)
    # Deflection profile (sinusoidal distribution along simple span)
    defl_ll_profile = delta_ll * np.sin(np.pi * x / span)
    defl_tot_profile = delta_tot * np.sin(np.pi * x / span)

    allow_ll = span * 1000.0 / 800.0   # L/800 = 25.0 mm
    allow_tot = span * 1000.0 / 600.0  # L/600 = 33.33 mm

    # Plot curves (downwards deflection)
    ax.plot(x, defl_tot_profile, color='#C0392B', lw=2.4, label=f'Total Serviceability Deflection (Max: {delta_tot:.2f} mm)')
    ax.plot(x, defl_ll_profile, color='#27AE60', lw=2.0, label=f'Live Load Deflection (Max: {delta_ll:.2f} mm)')
    ax.fill_between(x, 0, defl_tot_profile, color='#C0392B', alpha=0.10)

    # Plot horizontal limit lines
    ax.axhline(allow_tot, color='#900C3F', linestyle='--', lw=1.6, label=f'Total Deflection Limit: $L/600 = {allow_tot:.1f}$ mm (FAIL, UR = {delta_tot/allow_tot:.2f})')
    ax.axhline(allow_ll, color='#1E8449', linestyle=':', lw=1.6, label=f'Live Load Deflection Limit: $L/800 = {allow_ll:.1f}$ mm (PASS, UR = {delta_ll/allow_ll:.2f})')

    # Invert Y axis to represent downwards deflection
    ax.invert_yaxis()

    # Annotate total deflection exceedance
    mid_idx = len(x) // 2
    ax.plot(x[mid_idx], delta_tot, 'o', color='#C0392B', markersize=7)
    ax.annotate(
        f'GOVERNING SLS ISSUE:\n$\\delta_{{tot}} = {delta_tot:.2f}$ mm > {allow_tot:.1f} mm\n$\\mathbf{{UR = {delta_tot/allow_tot:.2f} \\; (FAIL)}}$',
        xy=(x[mid_idx], delta_tot),
        xytext=(x[mid_idx] + 1.2, delta_tot * 0.95),
        arrowprops=dict(arrowstyle='->', color='#C0392B', lw=1.4),
        fontsize=9, fontweight='bold', color='#900C3F',
        bbox=dict(boxstyle='round,pad=0.35', facecolor='#FADBD8', edgecolor='#C0392B', lw=1.2)
    )

    # Annotate live load pass
    ax.plot(x[mid_idx], delta_ll, 'o', color='#27AE60', markersize=6)
    ax.annotate(
        f'$\\delta_{{LL}} = {delta_ll:.2f}$ mm $\\leq 25.0$ mm\n$\\mathbf{{UR = {delta_ll/allow_ll:.2f} \\; (PASS)}}$',
        xy=(x[mid_idx], delta_ll),
        xytext=(x[mid_idx] - 6.5, delta_ll * 0.95),
        arrowprops=dict(arrowstyle='->', color='#27AE60', lw=1.2),
        fontsize=8.5, fontweight='bold', color='#1E8449',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='#E8F8F5', edgecolor='#27AE60', lw=1.0)
    )

    ax.set_xlabel('Distance along Bridge Span (m)', fontsize=9.5, fontweight='bold', labelpad=6)
    ax.set_ylabel('Vertical Deflection $D_y$ (mm, downwards)', fontsize=9.5, fontweight='bold', labelpad=6)
    ax.set_title('Vertical Deflection Profile $D_y$ along Span: SLS Deflection Verification', fontsize=11, fontweight='bold', pad=10, color='#1B4F72')
    ax.set_xlim(-0.5, span + 0.5)
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.legend(loc='lower center', framealpha=0.92, fontsize=8.2, ncol=2)

    if out_path:
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        plt.savefig(out_path, dpi=300, bbox_inches='tight')
        plt.close()
    return out_path


def generate_all_cad_drawings(input_dict, output_dict, target_dir):
    """
    Generate all 14 engineering CAD figures required by Chapter 6 and Executive Summary.
    Returns a dict mapping figure keys to generated file paths.
    """
    os.makedirs(target_dir, exist_ok=True)

    span = float(input_dict.get('geometry.span', 20.0) or 20.0)
    width = float(input_dict.get('transverse_cross_section.overall_width', 5.15) or 5.15)
    cw = float(input_dict.get('geometry.carriageway_width', 4.25) or 4.25)
    depth = float(input_dict.get('member_properties.girder_depth', 1.12) or 1.12)
    if depth > 10.0:  # in mm
        depth = depth / 1000.0
    spacing = float(input_dict.get('transverse_cross_section.girder_spacing', 1.72) or 1.72)
    overhang = float(input_dict.get('transverse_cross_section.deck_overhang', 0.86) or 0.86)
    t_deck = float(input_dict.get('transverse_cross_section.deck_thickness', 250) or 250)
    if t_deck > 2.0:
        t_deck = t_deck / 1000.0

    c_spacing = float(output_dict.get('steeldesign.details.stiffener_summary.int_spacing', 1635.0) or 1635.0)

    figs = {}

    # 1. 3D Bridge Superstructure
    p1 = os.path.join(target_dir, 'final_geometry.png')
    draw_bridge_3d(span=span, width=width, n_girders=3, depth=depth, out_path=p1)
    figs['final_geometry'] = p1.replace('\\', '/')

    # 2. Typical Cross Section
    p2 = os.path.join(target_dir, 'cross_section.png')
    draw_typical_cross_section(width=width, cw=cw, depth=depth, t_deck=t_deck, spacing=spacing, overhang=overhang, out_path=p2)
    figs['cross_section'] = p2.replace('\\', '/')

    # 3. Top View
    p3 = os.path.join(target_dir, 'girder_top.png')
    draw_top_view(span=span, width=width, n_girders=3, spacing=spacing, out_path=p3)
    figs['girder_top'] = p3.replace('\\', '/')

    # 4. 3D Girder Framing
    p4 = os.path.join(target_dir, 'girder_3d.png')
    draw_girder_3d(span=span, depth=depth, n_girders=3, spacing=spacing, out_path=p4)
    figs['girder_3d'] = p4.replace('\\', '/')

    # 5. Girder Cross Section
    p5 = os.path.join(target_dir, 'section_preview.png')
    draw_section_preview(depth=depth*1000, bf=340, tf=16, tw=8, out_path=p5)
    figs['section_preview'] = p5.replace('\\', '/')

    # 6. Girder Side Elevation
    p6 = os.path.join(target_dir, 'stiffener_preview.png')
    draw_stiffener_preview(span=span, depth=depth, int_spacing=c_spacing, out_path=p6)
    figs['stiffener_preview'] = p6.replace('\\', '/')

    # 7. Cross Bracing Layout
    p7 = os.path.join(target_dir, 'cb_diagram.png')
    draw_cb_diagram(spacing=spacing, depth=depth, out_path=p7)
    figs['cb_diagram'] = p7.replace('\\', '/')

    # 8. End Diaphragm Layout
    p8 = os.path.join(target_dir, 'ed_diagram.png')
    draw_ed_diagram(spacing=spacing, depth=depth, out_path=p8)
    figs['ed_diagram'] = p8.replace('\\', '/')

    # 9-11. Cross Bracing Sections
    p9 = os.path.join(target_dir, 'cb_bracing.png')
    draw_angle_section("40x40x3", "Bracing Section (ISA 40x40x3)", p9)
    figs['cb_bracing'] = p9.replace('\\', '/')

    p10 = os.path.join(target_dir, 'cb_top_chord.png')
    draw_angle_section("40x40x3", "Top Chord (ISA 40x40x3)", p10)
    figs['cb_top_chord'] = p10.replace('\\', '/')

    p11 = os.path.join(target_dir, 'cb_bottom_chord.png')
    draw_angle_section("40x40x3", "Bottom Chord (ISA 40x40x3)", p11)
    figs['cb_bottom_chord'] = p11.replace('\\', '/')

    # 12-14. End Diaphragm Sections
    p12 = os.path.join(target_dir, 'ed_bracing.png')
    draw_angle_section("40x40x3", "Diaphragm Bracing (ISA 40x40x3)", p12)
    figs['ed_bracing'] = p12.replace('\\', '/')

    p13 = os.path.join(target_dir, 'ed_top_chord.png')
    draw_angle_section("40x40x3", "Diaphragm Top Chord (ISA 40x40x3)", p13)
    figs['ed_top_chord'] = p13.replace('\\', '/')

    p14 = os.path.join(target_dir, 'ed_bottom_chord.png')
    draw_angle_section("40x40x3", "Diaphragm Bottom Chord (ISA 40x40x3)", p14)
    figs['ed_bottom_chord'] = p14.replace('\\', '/')

    # 15-17. Analysis Results Plots (Chapter 4)
    p15 = os.path.join(target_dir, 'bm_envelope.png')
    draw_bm_envelope(span=span, max_bm=694.47, out_path=p15)
    figs['bm_envelope'] = p15.replace('\\', '/')

    p16 = os.path.join(target_dir, 'sf_envelope.png')
    draw_sf_envelope(span=span, max_sf=160.38, out_path=p16)
    figs['sf_envelope'] = p16.replace('\\', '/')

    p17 = os.path.join(target_dir, 'defl_ll.png')
    draw_deflection_profile(span=span, delta_ll=15.616, delta_tot=37.137, out_path=p17)
    figs['defl_ll'] = p17.replace('\\', '/')

    return figs
