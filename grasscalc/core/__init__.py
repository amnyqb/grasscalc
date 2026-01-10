"""
Core module for Grassmannian geometry operations.

Provides:
- Linear algebra utilities (QR, SVD)
- Point representations (basis, projector)
- Distance metrics (chordal, geodesic, principal angles)
- Tangent space operations
- Calculus operations (derivatives, integrals, forms)
- Random sampling
"""

from .linalg import qr_retraction, svd_stable, gram_schmidt, stable_qr
from .representations import GrassmannPoint, to_projector, to_basis, stabilize
from .distances import chordal_distance_sq, principal_angles, geodesic_distance, frobenius_distance
from .tangent import tangent_project, tangent_inner_product, tangent_norm, horizontal_lift
from .random import sample_grassmann, sample_tangent
from .calculus import (
    riemannian_gradient, riemannian_hessian, directional_derivative,
    partial_derivative, covariant_derivative, lie_derivative,
    line_integral, surface_integral, volume_element, integrate_over_geodesic,
    differential_form, exterior_derivative, wedge_product, pullback, pushforward,
)

__all__ = [
    'qr_retraction', 'svd_stable', 'gram_schmidt', 'stable_qr',
    'GrassmannPoint', 'to_projector', 'to_basis', 'stabilize',
    'chordal_distance_sq', 'principal_angles', 'geodesic_distance', 'frobenius_distance',
    'tangent_project', 'tangent_inner_product', 'tangent_norm', 'horizontal_lift',
    'sample_grassmann', 'sample_tangent',
    'riemannian_gradient', 'riemannian_hessian', 'directional_derivative',
    'partial_derivative', 'covariant_derivative', 'lie_derivative',
    'line_integral', 'surface_integral', 'volume_element', 'integrate_over_geodesic',
    'differential_form', 'exterior_derivative', 'wedge_product', 'pullback', 'pushforward',
]
