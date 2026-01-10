"""
Layer 1: Within-manifold calculus.

Operations on a single Grassmannian Gr(k,n):
- Objective functions
- Gradient flows
- Optimization
"""

from .objectives import energy_overlap, stage_function, rayleigh_quotient
from .flows import gradient_flow, run_gradient_flow, geodesic_flow, hamiltonian_flow
from .optim import minimize_on_grassmann, trust_region_step, conjugate_gradient_step

__all__ = [
    'energy_overlap', 'stage_function', 'rayleigh_quotient',
    'gradient_flow', 'run_gradient_flow', 'geodesic_flow', 'hamiltonian_flow',
    'minimize_on_grassmann', 'trust_region_step', 'conjugate_gradient_step',
]
