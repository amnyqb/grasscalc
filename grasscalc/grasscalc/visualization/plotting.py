"""
Plotting utilities for Grassmannian manifolds.
"""

import numpy as np
from typing import List, Optional, Tuple, Dict, Any

# Optional matplotlib import
try:
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
    import matplotlib.patches as mpatches
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


def _check_matplotlib():
    """Check if matplotlib is available."""
    if not HAS_MATPLOTLIB:
        raise ImportError(
            "matplotlib is required for visualization. "
            "Install with: pip install matplotlib"
        )


def plot_optimization_convergence(
    energies: List[float],
    gradient_norms: Optional[List[float]] = None,
    title: str = "Optimization Convergence",
    figsize: Tuple[int, int] = (10, 4),
    log_scale: bool = True,
    save_path: Optional[str] = None
) -> Any:
    """
    Plot optimization convergence curves.

    Parameters
    ----------
    energies : list of float
        Objective values at each iteration
    gradient_norms : list of float, optional
        Gradient norms at each iteration
    title : str
        Plot title
    figsize : tuple
        Figure size (width, height)
    log_scale : bool
        Use logarithmic y-axis
    save_path : str, optional
        Path to save figure

    Returns
    -------
    fig : matplotlib Figure
    """
    _check_matplotlib()

    n_plots = 2 if gradient_norms is not None else 1
    fig, axes = plt.subplots(1, n_plots, figsize=figsize)

    if n_plots == 1:
        axes = [axes]

    # Energy plot
    ax = axes[0]
    if log_scale and min(energies) > 0:
        ax.semilogy(energies, 'b-', linewidth=2)
    else:
        ax.plot(energies, 'b-', linewidth=2)
    ax.set_xlabel('Iteration', fontsize=11)
    ax.set_ylabel('Objective', fontsize=11)
    ax.set_title('Objective Value', fontsize=12)
    ax.grid(True, alpha=0.3)

    # Gradient norm plot
    if gradient_norms is not None:
        ax = axes[1]
        if log_scale and min(gradient_norms) > 0:
            ax.semilogy(gradient_norms, 'r-', linewidth=2)
        else:
            ax.plot(gradient_norms, 'r-', linewidth=2)
        ax.set_xlabel('Iteration', fontsize=11)
        ax.set_ylabel('Gradient Norm', fontsize=11)
        ax.set_title('Gradient Norm', fontsize=12)
        ax.grid(True, alpha=0.3)

    fig.suptitle(title, fontsize=14)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')

    return fig


def plot_distance_matrix(
    points: List[np.ndarray],
    distance_fn=None,
    labels: Optional[List[str]] = None,
    title: str = "Pairwise Distances",
    cmap: str = "viridis",
    figsize: Tuple[int, int] = (8, 6),
    save_path: Optional[str] = None
) -> Any:
    """
    Plot pairwise distance matrix between Grassmannian points.

    Parameters
    ----------
    points : list of ndarray
        Points on Grassmannian
    distance_fn : callable, optional
        Distance function (default: geodesic_distance)
    labels : list of str, optional
        Labels for each point
    title : str
        Plot title
    cmap : str
        Colormap name
    figsize : tuple
        Figure size
    save_path : str, optional
        Path to save figure

    Returns
    -------
    fig : matplotlib Figure
    """
    _check_matplotlib()

    if distance_fn is None:
        from ..core.distances import geodesic_distance
        distance_fn = geodesic_distance

    n = len(points)
    D = np.zeros((n, n))

    for i in range(n):
        for j in range(i + 1, n):
            d = distance_fn(points[i], points[j])
            D[i, j] = d
            D[j, i] = d

    fig, ax = plt.subplots(figsize=figsize)
    im = ax.imshow(D, cmap=cmap)

    if labels:
        ax.set_xticks(range(n))
        ax.set_yticks(range(n))
        ax.set_xticklabels(labels, rotation=45, ha='right')
        ax.set_yticklabels(labels)

    plt.colorbar(im, ax=ax, label='Distance')
    ax.set_title(title, fontsize=14)

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')

    return fig


def plot_principal_angles(
    U: np.ndarray,
    V: np.ndarray,
    title: str = "Principal Angles",
    figsize: Tuple[int, int] = (8, 5),
    save_path: Optional[str] = None
) -> Any:
    """
    Plot principal angles between two subspaces.

    Parameters
    ----------
    U, V : ndarray
        Orthonormal bases for two subspaces
    title : str
        Plot title
    figsize : tuple
        Figure size
    save_path : str, optional
        Path to save figure

    Returns
    -------
    fig : matplotlib Figure
    """
    _check_matplotlib()

    from ..core.distances import principal_angles

    angles = principal_angles(U, V)
    angles_deg = np.rad2deg(angles)
    k = len(angles)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)

    # Bar chart
    ax1.bar(range(1, k + 1), angles_deg, color='steelblue', edgecolor='navy')
    ax1.set_xlabel('Principal Angle Index', fontsize=11)
    ax1.set_ylabel('Angle (degrees)', fontsize=11)
    ax1.set_title('Principal Angles', fontsize=12)
    ax1.set_xticks(range(1, k + 1))
    ax1.set_ylim(0, 90)
    ax1.grid(True, alpha=0.3, axis='y')

    # Cumulative
    cumulative = np.cumsum(angles ** 2)
    ax2.plot(range(1, k + 1), cumulative, 'ro-', linewidth=2, markersize=8)
    ax2.set_xlabel('Principal Angle Index', fontsize=11)
    ax2.set_ylabel(r'$\sum \theta_i^2$ (radians$^2$)', fontsize=11)
    ax2.set_title('Cumulative Squared Angles', fontsize=12)
    ax2.set_xticks(range(1, k + 1))
    ax2.grid(True, alpha=0.3)

    fig.suptitle(title, fontsize=14)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')

    return fig


def plot_geodesic_path(
    U: np.ndarray,
    V: np.ndarray,
    n_points: int = 11,
    reference: Optional[np.ndarray] = None,
    title: str = "Geodesic Path",
    figsize: Tuple[int, int] = (10, 5),
    save_path: Optional[str] = None
) -> Any:
    """
    Plot properties along geodesic from U to V.

    Parameters
    ----------
    U, V : ndarray
        Start and end points
    n_points : int
        Number of points along geodesic
    reference : ndarray, optional
        Reference point to measure distance to
    title : str
        Plot title
    figsize : tuple
        Figure size
    save_path : str, optional
        Path to save figure

    Returns
    -------
    fig : matplotlib Figure
    """
    _check_matplotlib()

    from ..core.tangent import geodesic
    from ..core.distances import geodesic_distance, chordal_distance

    t_values = np.linspace(0, 1, n_points)
    points = [geodesic(U, V, t) for t in t_values]

    # Distances from U
    d_from_U = [geodesic_distance(U, W) for W in points]
    d_total = geodesic_distance(U, V)

    fig, axes = plt.subplots(1, 2 if reference is None else 3, figsize=figsize)

    # Distance from U
    ax = axes[0]
    ax.plot(t_values, d_from_U, 'b-', linewidth=2, label='Actual')
    ax.plot(t_values, t_values * d_total, 'r--', linewidth=2, label='Expected (linear)')
    ax.set_xlabel('t', fontsize=11)
    ax.set_ylabel('Distance from U', fontsize=11)
    ax.set_title('Distance Along Geodesic', fontsize=12)
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Chordal vs geodesic
    ax = axes[1]
    d_chord = [chordal_distance(U, W) for W in points]
    ax.plot(t_values, d_from_U, 'b-', linewidth=2, label='Geodesic')
    ax.plot(t_values, d_chord, 'g--', linewidth=2, label='Chordal')
    ax.set_xlabel('t', fontsize=11)
    ax.set_ylabel('Distance', fontsize=11)
    ax.set_title('Geodesic vs Chordal Distance', fontsize=12)
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Distance to reference
    if reference is not None:
        ax = axes[2]
        d_ref = [geodesic_distance(W, reference) for W in points]
        ax.plot(t_values, d_ref, 'm-', linewidth=2)
        ax.set_xlabel('t', fontsize=11)
        ax.set_ylabel('Distance to Reference', fontsize=11)
        ax.set_title('Distance to Reference Point', fontsize=12)
        ax.grid(True, alpha=0.3)

    fig.suptitle(title, fontsize=14)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')

    return fig


def plot_gct_chain(
    figsize: Tuple[int, int] = (12, 6),
    save_path: Optional[str] = None
) -> Any:
    """
    Plot the GCT chain diagram.

    Parameters
    ----------
    figsize : tuple
        Figure size
    save_path : str, optional
        Path to save figure

    Returns
    -------
    fig : matplotlib Figure
    """
    _check_matplotlib()

    from ..gct.chain import GCT_CHAIN

    fig, ax = plt.subplots(figsize=figsize)

    # Chain data
    n_values = [gr['n'] for gr in GCT_CHAIN]
    k = GCT_CHAIN[0]['k']
    dims = [k * (n - k) for n in n_values]

    # Positions
    x_positions = np.linspace(0.1, 0.9, len(n_values))
    y_center = 0.5

    # Draw boxes
    box_width = 0.12
    box_height = 0.25

    for i, (x, n, dim) in enumerate(zip(x_positions, n_values, dims)):
        # Box
        box = FancyBboxPatch(
            (x - box_width/2, y_center - box_height/2),
            box_width, box_height,
            boxstyle="round,pad=0.02,rounding_size=0.02",
            facecolor='lightsteelblue',
            edgecolor='navy',
            linewidth=2
        )
        ax.add_patch(box)

        # Text
        ax.text(x, y_center + 0.02, f"Gr({k},{n})",
                ha='center', va='center', fontsize=12, fontweight='bold')
        ax.text(x, y_center - 0.06, f"dim={dim}",
                ha='center', va='center', fontsize=10)

    # Draw arrows
    for i in range(len(n_values) - 1):
        x1 = x_positions[i] + box_width/2
        x2 = x_positions[i+1] - box_width/2

        ax.annotate('', xy=(x2, y_center), xytext=(x1, y_center),
                   arrowprops=dict(arrowstyle='->', color='darkred', lw=2))

        # Delta n label
        delta_n = n_values[i] - n_values[i+1]
        ax.text((x1 + x2) / 2, y_center + 0.08, f"Δn={delta_n}",
               ha='center', va='bottom', fontsize=9, color='darkred')

    # Title and labels
    ax.set_title("GCT Chain: Grassmannian Cascade", fontsize=16, fontweight='bold')
    ax.text(0.5, 0.15, f"Total dimension: {sum(dims)}",
            ha='center', fontsize=12, transform=ax.transAxes)
    ax.text(0.5, 0.08, f"Fiber dimension k = {k} throughout",
            ha='center', fontsize=10, style='italic', transform=ax.transAxes)

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')

    return fig


def plot_weinberg_comparison(
    figsize: Tuple[int, int] = (8, 5),
    save_path: Optional[str] = None
) -> Any:
    """
    Plot comparison of GCT Weinberg angle prediction with experiment.

    Parameters
    ----------
    figsize : tuple
        Figure size
    save_path : str, optional
        Path to save figure

    Returns
    -------
    fig : matplotlib Figure
    """
    _check_matplotlib()

    from ..gct.weinberg import (
        sin2_weinberg_numeric, WEINBERG_EXPERIMENTAL
    )

    gct_value = sin2_weinberg_numeric()
    exp_value = WEINBERG_EXPERIMENTAL
    exp_error = 0.00016

    fig, ax = plt.subplots(figsize=figsize)

    # Values to compare
    values = {
        'GCT (3/13)': (gct_value, None),
        'Experiment': (exp_value, exp_error),
        'LEP': (0.23153, 0.00016),
        'SLD': (0.23098, 0.00026),
    }

    x_positions = np.arange(len(values))
    colors = ['steelblue', 'forestgreen', 'coral', 'orchid']

    for i, (name, (val, err)) in enumerate(values.items()):
        if err:
            ax.errorbar(i, val, yerr=err, fmt='o', markersize=10,
                       capsize=6, color=colors[i], label=f'{name}: {val:.5f}')
        else:
            ax.plot(i, val, 's', markersize=12, color=colors[i],
                   label=f'{name}: {val:.5f}')

    # Reference lines
    ax.axhline(y=gct_value, color='steelblue', linestyle='--', alpha=0.4)

    ax.set_xticks(x_positions)
    ax.set_xticklabels(list(values.keys()), fontsize=11)
    ax.set_ylabel(r'$\sin^2\theta_W$', fontsize=12)
    ax.set_title('Weinberg Angle: GCT Prediction vs Measurements', fontsize=14)
    ax.legend(loc='upper right', fontsize=10)
    ax.grid(True, alpha=0.3, axis='y')
    ax.set_ylim(0.228, 0.234)

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')

    return fig
