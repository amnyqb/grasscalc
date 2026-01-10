"""
Layer 2: Between-manifold transition calculus.

Operations between Grassmannians:
- Correspondences (raise-k, raise-n)
- Sharp Bound Theorem
- Transition actions and operators
- Hybrid evolution
- Macro-variable calculus
"""

from .correspondences import raise_k_successors, raise_n_successors, compose_correspondences
from .sharp_bound import (
    sharp_bound_check, sharp_bound_gap, is_saturated,
    is_containment, find_optimal_successor
)
from .transition_action import transition_action, optimal_transition
from .operators import minplus_operator, argmin_transition
from .hybrid import run_hybrid_chain, HybridState
from .macro import macro_variables, codimension, grassmann_dimension

__all__ = [
    'raise_k_successors', 'raise_n_successors', 'compose_correspondences',
    'sharp_bound_check', 'sharp_bound_gap', 'is_saturated',
    'is_containment', 'find_optimal_successor',
    'transition_action', 'optimal_transition',
    'minplus_operator', 'argmin_transition',
    'run_hybrid_chain', 'HybridState',
    'macro_variables', 'codimension', 'grassmann_dimension',
]
