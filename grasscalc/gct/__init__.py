"""
GCT Module: Grassmannian Cosmological Theory.

Implements the seven-manifold chain from GCT:
Gr(2,5) → Gr(3,5) → Gr(3,7) → Gr(3,16) → Gr(7,18) → Gr(8,24) → Gr(10,34)

Key results:
- Total dimension: 508 = 496 + 12 (gauge + gravity)
- Weinberg angle: sin²θ_W = k/(n-k) = 3/13 = 0.23077 from Gr(3,16)
"""

from .chain import GCT_CHAIN, gct_dimension, gct_total_dimension, gct_manifolds
from .weinberg import weinberg_angle, weinberg_angle_experimental, weinberg_error
from .transitions import gct_transition_operators, T0, T1, T2, T3, T4, T5
from .validation import verify_gct_dimensions, verify_gct_chain, run_gct_tests
from .physics import division_algebra_map, hurwitz_dimensions, DIVISION_ALGEBRAS

__all__ = [
    'GCT_CHAIN', 'gct_dimension', 'gct_total_dimension', 'gct_manifolds',
    'weinberg_angle', 'weinberg_angle_experimental', 'weinberg_error',
    'gct_transition_operators', 'T0', 'T1', 'T2', 'T3', 'T4', 'T5',
    'verify_gct_dimensions', 'verify_gct_chain', 'run_gct_tests',
    'division_algebra_map', 'hurwitz_dimensions', 'DIVISION_ALGEBRAS',
]
