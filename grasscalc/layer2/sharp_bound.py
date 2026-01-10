"""
Sharp Bound Theorem implementation.

Theorem (Al Yaquob, 2026):
For V ∈ Gr(k,n) and W ∈ Gr(k',n') embedded in common ambient R^N:

    d²(V, W) ≥ |k - k'|

with equality if and only if one subspace contains the other (V ⊂ W or W ⊂ V).
"""

import numpy as np
from numpy.linalg import norm, svd
from typing import Dict, Optional, Tuple

from ..core.distances import chordal_distance_sq
from ..core.representations import stabilize, subspace_contains


def sharp_bound_check(
    U: np.ndarray,
    V: np.ndarray,
    N: Optional[int] = None,
    tol: float = 1e-10
) -> Dict:
    """
    Verify the Sharp Bound Theorem for two subspaces.

    d²(U, V) ≥ |k - k'| with equality iff containment.

    Parameters
    ----------
    U : ndarray, shape (n, k)
        First subspace basis
    V : ndarray, shape (n', k')
        Second subspace basis
    N : int, optional
        Common ambient dimension (max of n, n' if not specified)
    tol : float
        Tolerance for saturation check

    Returns
    -------
    dict
        'd2': float - squared chordal distance
        'delta_k': int - |k - k'|
        'lower_bound': int - = delta_k
        'gap': float - d² - |k - k'|
        'saturated': bool - gap < tol
        'theorem_satisfied': bool - gap >= 0
    """
    n, k = U.shape
    n_prime, k_prime = V.shape

    if N is None:
        N = max(n, n_prime)

    # Stabilize to common ambient space
    U_stab = stabilize(U, n, N)
    V_stab = stabilize(V, n_prime, N)

    # Compute squared distance
    d2 = chordal_distance_sq(U_stab, V_stab)

    # Compute gap
    delta_k = abs(k - k_prime)
    gap = d2 - delta_k

    return {
        'd2': d2,
        'delta_k': delta_k,
        'lower_bound': delta_k,
        'gap': gap,
        'saturated': gap < tol,
        'theorem_satisfied': gap >= -tol  # Allow small numerical error
    }


def sharp_bound_gap(U: np.ndarray, V: np.ndarray, N: Optional[int] = None) -> float:
    """
    Compute gap from sharp bound: d²(U,V) - |k - k'|.

    Parameters
    ----------
    U, V : ndarray
        Subspace bases
    N : int, optional
        Ambient dimension

    Returns
    -------
    gap : float
        Excess over sharp bound (0 if saturated)
    """
    result = sharp_bound_check(U, V, N)
    return result['gap']


def is_saturated(
    U: np.ndarray,
    V: np.ndarray,
    N: Optional[int] = None,
    tol: float = 1e-10
) -> bool:
    """
    Check if the sharp bound is saturated (d² = |k - k'|).

    Saturation implies containment.

    Parameters
    ----------
    U, V : ndarray
        Subspace bases
    N : int, optional
        Ambient dimension
    tol : float
        Tolerance

    Returns
    -------
    bool
        True if bound is saturated
    """
    result = sharp_bound_check(U, V, N, tol)
    return result['saturated']


def is_containment(
    U: np.ndarray,
    V: np.ndarray,
    tol: float = 1e-10
) -> Dict:
    """
    Check if span(U) ⊂ span(V) or span(V) ⊂ span(U).

    Parameters
    ----------
    U : ndarray, shape (n, k)
        First subspace basis
    V : ndarray, shape (n, k')
        Second subspace basis
    tol : float
        Tolerance

    Returns
    -------
    dict
        'is_contained': bool - True if containment holds
        'direction': str - 'U_in_V', 'V_in_U', or 'none'
        'residual': float - measure of containment quality
    """
    # Stabilize to same ambient if needed
    n, k = U.shape
    n_prime, k_prime = V.shape
    N = max(n, n_prime)

    U_stab = stabilize(U, n, N) if n < N else U
    V_stab = stabilize(V, n_prime, N) if n_prime < N else V

    # Check U ⊂ V: project U onto span(V) and check if unchanged
    P_V = V_stab @ V_stab.T
    U_proj = P_V @ U_stab
    residual_U_in_V = norm(U_stab - U_proj, 'fro')

    # Check V ⊂ U: project V onto span(U)
    P_U = U_stab @ U_stab.T
    V_proj = P_U @ V_stab
    residual_V_in_U = norm(V_stab - V_proj, 'fro')

    # Normalize residuals
    residual_U_in_V /= max(norm(U_stab, 'fro'), 1e-14)
    residual_V_in_U /= max(norm(V_stab, 'fro'), 1e-14)

    U_in_V = residual_U_in_V < tol
    V_in_U = residual_V_in_U < tol

    if U_in_V and not V_in_U:
        direction = 'U_in_V'
        residual = residual_U_in_V
    elif V_in_U and not U_in_V:
        direction = 'V_in_U'
        residual = residual_V_in_U
    elif U_in_V and V_in_U:
        # Equal subspaces (if k = k')
        direction = 'equal' if k == k_prime else 'both'
        residual = min(residual_U_in_V, residual_V_in_U)
    else:
        direction = 'none'
        residual = min(residual_U_in_V, residual_V_in_U)

    return {
        'is_contained': U_in_V or V_in_U,
        'direction': direction,
        'residual': residual,
        'U_in_V': U_in_V,
        'V_in_U': V_in_U
    }


def find_optimal_successor(
    U: np.ndarray,
    k_next: int,
    n_next: int,
    constraint: str = 'containment'
) -> np.ndarray:
    """
    Find W ∈ Gr(k', n') achieving d² = |k' - k| (sharp bound saturation).

    Parameters
    ----------
    U : ndarray, shape (n, k)
        Current subspace
    k_next : int
        Target fiber dimension
    n_next : int
        Target ambient dimension
    constraint : str
        'containment': W ⊃ U (for k_next > k) or W ⊂ U (for k_next < k)
        'minimal': minimize distance without containment constraint

    Returns
    -------
    W : ndarray, shape (n_next, k_next)
        Optimal successor achieving sharp bound
    """
    from ..core.linalg import stable_qr, extend_orthonormal_basis
    from ..core.random import sample_grassmann

    n, k = U.shape
    N = max(n, n_next)

    # Stabilize U to ambient N
    U_stab = stabilize(U, n, N)

    if constraint == 'containment':
        if k_next > k:
            # Extend U to larger subspace
            W = extend_orthonormal_basis(U_stab, k_next)
        elif k_next < k:
            # Contract U to smaller subspace
            # Take first k_next columns (any k_next-subspace of span(U) works)
            W = U_stab[:, :k_next].copy()
            W, _ = stable_qr(W)
        else:
            # Same k
            W = U_stab.copy()

        # Trim to n_next if needed
        if N > n_next:
            # Project to first n_next dimensions
            W = W[:n_next, :]
            W, _ = stable_qr(W)

    elif constraint == 'minimal':
        # For minimal distance without containment, start with containment solution
        # and it's already optimal (sharp bound is achieved with containment)
        return find_optimal_successor(U, k_next, n_next, 'containment')

    else:
        raise ValueError(f"Unknown constraint: {constraint}")

    return W


def verify_sharp_bound_batch(
    pairs: list,
    N: int,
    tol: float = 1e-10
) -> Dict:
    """
    Verify sharp bound for a batch of subspace pairs.

    Parameters
    ----------
    pairs : list of (U, V) tuples
        Pairs of subspace bases
    N : int
        Common ambient dimension
    tol : float
        Tolerance

    Returns
    -------
    dict
        'all_satisfied': bool
        'num_saturated': int
        'results': list of individual check results
    """
    results = []
    num_saturated = 0

    for U, V in pairs:
        result = sharp_bound_check(U, V, N, tol)
        results.append(result)
        if result['saturated']:
            num_saturated += 1

    all_satisfied = all(r['theorem_satisfied'] for r in results)

    return {
        'all_satisfied': all_satisfied,
        'num_saturated': num_saturated,
        'num_pairs': len(pairs),
        'results': results
    }
