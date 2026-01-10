"""
Objective functions for optimization on Grassmannians.
"""

import numpy as np
from numpy.linalg import norm, svd
from typing import Tuple, Callable, Optional


def energy_overlap(
    U: np.ndarray,
    U_R: np.ndarray,
    N: Optional[int] = None,
    r: Optional[int] = None,
    k: Optional[int] = None
) -> Tuple[float, float, float]:
    """
    Compute overlap energy between subspace U and reference U_R.

    The stage function s(U) measures overlap with reference:
    s = ||P_U P_R||_F² / r = ||U^T U_R||_F² / r

    Energy E = (s - τ)² measures deviation from target.

    Parameters
    ----------
    U : ndarray, shape (n, k)
        Current subspace basis
    U_R : ndarray, shape (N, r)
        Reference subspace basis
    N : int, optional
        Ambient dimension (inferred if not provided)
    r : int, optional
        Reference dimension (inferred if not provided)
    k : int, optional
        Fiber dimension (inferred if not provided)

    Returns
    -------
    s : float
        Stage function value (overlap measure)
    tau : float
        Target value (= k for exact alignment)
    E : float
        Energy (s - tau)²
    """
    if k is None:
        k = U.shape[1]
    if r is None:
        r = U_R.shape[1]

    # Compute overlap
    UtU_R = U.T @ U_R
    overlap_sq = np.sum(UtU_R ** 2)

    s = overlap_sq / r
    tau = float(k)  # Target: full alignment
    E = (s - tau) ** 2

    return s, tau, E


def stage_function(
    U: np.ndarray,
    reference: Optional[np.ndarray] = None,
    mode: str = 'dimension'
) -> float:
    """
    Generic stage function s: Gr(k,n) → R.

    Parameters
    ----------
    U : ndarray, shape (n, k)
        Point on Grassmannian
    reference : ndarray, optional
        Reference point for overlap mode
    mode : str
        'dimension': s = k
        'codimension': s = n - k
        'overlap': s = ||U^T reference||_F² / r

    Returns
    -------
    s : float
        Stage function value
    """
    n, k = U.shape

    if mode == 'dimension':
        return float(k)
    elif mode == 'codimension':
        return float(n - k)
    elif mode == 'overlap':
        if reference is None:
            raise ValueError("Reference required for overlap mode")
        r = reference.shape[1]
        return np.sum((U.T @ reference) ** 2) / r
    else:
        raise ValueError(f"Unknown mode: {mode}")


def rayleigh_quotient(U: np.ndarray, A: np.ndarray) -> float:
    """
    Rayleigh quotient for symmetric matrix A.

    R(U) = trace(U^T A U) / trace(U^T U) = trace(U^T A U)

    Minimizing gives the k smallest eigenvalues.

    Parameters
    ----------
    U : ndarray, shape (n, k)
        Point on Grassmannian
    A : ndarray, shape (n, n)
        Symmetric matrix

    Returns
    -------
    R : float
        Rayleigh quotient
    """
    return np.trace(U.T @ A @ U)


def rayleigh_gradient(U: np.ndarray, A: np.ndarray) -> np.ndarray:
    """
    Riemannian gradient of Rayleigh quotient.

    grad R = 2 * (I - U U^T) A U

    Parameters
    ----------
    U : ndarray
        Point on Grassmannian
    A : ndarray
        Symmetric matrix

    Returns
    -------
    grad : ndarray
        Riemannian gradient
    """
    AU = A @ U
    return 2 * (AU - U @ (U.T @ AU))


def distance_objective(U: np.ndarray, V: np.ndarray) -> float:
    """
    Squared chordal distance as objective function.

    Parameters
    ----------
    U : ndarray
        Variable point
    V : ndarray
        Fixed target

    Returns
    -------
    d2 : float
        Squared distance
    """
    from ..core.distances import chordal_distance_sq
    return chordal_distance_sq(U, V)


def distance_gradient(U: np.ndarray, V: np.ndarray) -> np.ndarray:
    """
    Riemannian gradient of squared distance to V.

    Parameters
    ----------
    U : ndarray
        Variable point
    V : ndarray
        Fixed target

    Returns
    -------
    grad : ndarray
        Riemannian gradient
    """
    # grad d²(U, V) = -2 (I - U U^T) V V^T U = -2 tangent_project(U, V V^T U)
    VVtU = V @ (V.T @ U)
    return -2 * (VVtU - U @ (U.T @ VVtU))


def projection_energy(U: np.ndarray, target_projector: np.ndarray) -> float:
    """
    Energy measuring deviation from target projector.

    E = ||P_U - P_target||_F²

    Parameters
    ----------
    U : ndarray, shape (n, k)
        Current point
    target_projector : ndarray, shape (n, n)
        Target projector matrix

    Returns
    -------
    E : float
        Projection energy
    """
    P_U = U @ U.T
    return np.sum((P_U - target_projector) ** 2)


def make_objective(
    objective_type: str,
    **kwargs
) -> Callable[[np.ndarray], float]:
    """
    Factory for creating objective functions.

    Parameters
    ----------
    objective_type : str
        'rayleigh', 'distance', 'overlap', 'projection'
    **kwargs
        Parameters for the objective

    Returns
    -------
    f : callable
        Objective function f: Gr(k,n) → R
    """
    if objective_type == 'rayleigh':
        A = kwargs['A']
        return lambda U: rayleigh_quotient(U, A)

    elif objective_type == 'distance':
        V = kwargs['target']
        return lambda U: distance_objective(U, V)

    elif objective_type == 'overlap':
        reference = kwargs['reference']
        return lambda U: -np.sum((U.T @ reference) ** 2)  # Negative for maximization

    elif objective_type == 'projection':
        P = kwargs['projector']
        return lambda U: projection_energy(U, P)

    else:
        raise ValueError(f"Unknown objective type: {objective_type}")
