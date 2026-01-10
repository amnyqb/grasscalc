"""
Visualization utilities for Grassmannian manifolds.

This module provides plotting functions for:
- Optimization trajectories
- Distance matrices
- Principal angle distributions
- GCT chain diagrams
"""

from .plotting import (
    plot_optimization_convergence,
    plot_distance_matrix,
    plot_principal_angles,
    plot_geodesic_path,
    plot_gct_chain,
    plot_weinberg_comparison,
)

__all__ = [
    'plot_optimization_convergence',
    'plot_distance_matrix',
    'plot_principal_angles',
    'plot_geodesic_path',
    'plot_gct_chain',
    'plot_weinberg_comparison',
]
