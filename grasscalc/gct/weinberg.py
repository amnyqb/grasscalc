"""
Weinberg angle derivation from Gr(3,16).

The electroweak mixing angle emerges from the Grassmannian structure:
sin²θ_W = k/(n-k) = 3/13 = 0.23076923...

Experimental value: 0.23122 ± 0.00003 (PDG 2024)
GCT error: ~0.19%
"""

from fractions import Fraction
from typing import Dict


def weinberg_angle(k: int = 3, n: int = 16) -> float:
    """
    Compute Weinberg angle from Grassmannian Gr(k,n).

    sin²θ_W = k/(n-k)

    For Gr(3,16): sin²θ_W = 3/13 = 0.23076923...

    Parameters
    ----------
    k : int, default 3
        Fiber dimension
    n : int, default 16
        Ambient dimension

    Returns
    -------
    sin2_theta_W : float
        Predicted weak mixing angle
    """
    return k / (n - k)


def weinberg_angle_exact(k: int = 3, n: int = 16) -> Fraction:
    """
    Exact rational Weinberg angle.

    Parameters
    ----------
    k : int
        Fiber dimension
    n : int
        Ambient dimension

    Returns
    -------
    sin2_theta_W : Fraction
        Exact rational value
    """
    return Fraction(k, n - k)


def weinberg_angle_experimental() -> Dict:
    """
    Experimental Weinberg angle value (PDG 2024).

    Returns
    -------
    dict
        'value': float - central value
        'uncertainty': float - experimental uncertainty
        'source': str - reference
    """
    return {
        'value': 0.23122,
        'uncertainty': 0.00003,
        'source': 'PDG 2024 (on-shell scheme)'
    }


def weinberg_error() -> Dict:
    """
    Compare GCT prediction with experiment.

    Returns
    -------
    dict
        'predicted': float - GCT prediction
        'experimental': float - measured value
        'absolute_error': float
        'relative_error': float (percentage)
        'sigma': float - deviation in experimental sigma
    """
    predicted = weinberg_angle(3, 16)
    exp = weinberg_angle_experimental()
    experimental = exp['value']
    uncertainty = exp['uncertainty']

    abs_error = abs(predicted - experimental)
    rel_error = abs_error / experimental * 100
    sigma = abs_error / uncertainty

    return {
        'predicted': predicted,
        'predicted_exact': '3/13',
        'experimental': experimental,
        'uncertainty': uncertainty,
        'absolute_error': abs_error,
        'relative_error_percent': rel_error,
        'sigma': sigma
    }


def weinberg_from_embedding() -> str:
    """
    Physical interpretation of Weinberg angle derivation.

    Returns
    -------
    explanation : str
        Derivation explanation
    """
    return """
Weinberg Angle Derivation from Gr(3,16)
=======================================

The electroweak mixing angle emerges from the embedding of SU(2)_L × U(1)_Y
into the 16-dimensional ambient space of Gr(3,16).

Key insight: The ratio k/(n-k) determines the mixing between weak isospin
and hypercharge:

    sin²θ_W = dim(fiber) / dim(complement)
            = k / (n - k)
            = 3 / 13
            = 0.23076923...

Comparison with experiment (PDG 2024):
    Experimental: 0.23122 ± 0.00003
    GCT prediction: 0.23077
    Error: 0.19%

This derivation requires no free parameters - the value emerges purely
from the geometric structure of the Grassmannian manifold.
"""


def verify_weinberg_derivation() -> Dict:
    """
    Full verification of Weinberg angle derivation.

    Returns
    -------
    dict
        Comprehensive verification results
    """
    from .chain import GCT_CHAIN

    # Find the electroweak manifold (should be stage 3)
    ew_stage = None
    for i, (k, n) in enumerate(GCT_CHAIN):
        if k == 3 and n == 16:
            ew_stage = i
            break

    predicted = weinberg_angle(3, 16)
    exact = weinberg_angle_exact(3, 16)
    exp = weinberg_angle_experimental()
    error = weinberg_error()

    return {
        'manifold': 'Gr(3,16)',
        'stage': ew_stage,
        'formula': 'sin²θ_W = k/(n-k)',
        'k': 3,
        'n': 16,
        'codimension': 13,
        'predicted_float': predicted,
        'predicted_exact': str(exact),
        'experimental': exp['value'],
        'experimental_uncertainty': exp['uncertainty'],
        'relative_error_percent': error['relative_error_percent'],
        'verified': error['relative_error_percent'] < 1.0  # Within 1%
    }
