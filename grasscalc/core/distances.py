"""
Distance metrics on Grassmannian manifolds.

Implements:
- Chordal (projector) distance
- Principal angles
- Geodesic distance
- Frobenius distance
"""

import numpy as np
from numpy.linalg import norm, svd
from typing import Tuple, Union


def principal_angles(U: np.ndarray, V: np.ndarray) -> np.ndarray:
    """
    Compute principal angles between two subspaces.

    The principal angles θ₁ ≤ θ₂ ≤ ... ≤ θ_min(k,k') are defined by:
    cos(θᵢ) = σᵢ(U^T V)

    where σᵢ are the singular values of U^T V.

    Parameters
    ----------
    U : ndarray, shape (n, k)
        Orthonormal basis for first subspace
    V : ndarray, shape (n, k')
        Orthonormal basis for second subspace

    Returns
    -------
    theta : ndarray, shape (min(k, k'),)
        Principal angles in [0, π/2], ascending order
    """
    # Compute singular values of U^T V
    sigma = svd(U.T @ V, compute_uv=False)

    # Clamp to [0, 1] for numerical stability
    sigma = np.clip(sigma, 0.0, 1.0)

    # Convert to angles
    theta = np.arccos(sigma)

    return np.sort(theta)


def chordal_distance_sq(U: np.ndarray, V: np.ndarray) -> float:
    """
    Squared chordal (projector) distance between subspaces.

    Defined as:
    d²(U, V) = k + k' - 2||U^T V||_F²
             = ||P_U - P_V||_F²

    This metric works across different k values (different Grassmannians).

    Parameters
    ----------
    U : ndarray, shape (N, k)
        Orthonormal basis for first subspace
    V : ndarray, shape (N, k')
        Orthonormal basis for second subspace

    Returns
    -------
    d2 : float
        Squared chordal distance

    Notes
    -----
    For same k: d² = 2 * sum(sin²(θᵢ)) where θᵢ are principal angles.
    For different k: d² ≥ |k - k'| (Sharp Bound Theorem).
    """
    k = U.shape[1]
    k_prime = V.shape[1]

    UtV = U.T @ V
    frobenius_sq = np.sum(UtV ** 2)

    d2 = k + k_prime - 2 * frobenius_sq
    return max(0.0, d2)  # Ensure non-negative due to numerical errors


def chordal_distance(U: np.ndarray, V: np.ndarray) -> float:
    """
    Chordal distance between subspaces.

    Parameters
    ----------
    U, V : ndarray
        Orthonormal bases

    Returns
    -------
    d : float
        Chordal distance
    """
    return np.sqrt(chordal_distance_sq(U, V))


def geodesic_distance(U: np.ndarray, V: np.ndarray) -> float:
    """
    Geodesic distance on Grassmannian (same k only).

    Defined as:
    d_geo(U, V) = ||θ||₂ = sqrt(sum(θᵢ²))

    where θᵢ are the principal angles.

    Parameters
    ----------
    U : ndarray, shape (n, k)
        Orthonormal basis for first subspace
    V : ndarray, shape (n, k)
        Orthonormal basis for second subspace (same k required)

    Returns
    -------
    d : float
        Geodesic distance

    Raises
    ------
    ValueError
        If U and V have different k
    """
    if U.shape[1] != V.shape[1]:
        raise ValueError(
            f"Geodesic distance requires same k. Got {U.shape[1]} and {V.shape[1]}"
        )

    theta = principal_angles(U, V)
    return norm(theta)


def geodesic_distance_sq(U: np.ndarray, V: np.ndarray) -> float:
    """
    Squared geodesic distance.

    Parameters
    ----------
    U, V : ndarray
        Orthonormal bases with same k

    Returns
    -------
    d2 : float
        Squared geodesic distance = sum(θᵢ²)
    """
    theta = principal_angles(U, V)
    return np.sum(theta ** 2)


def frobenius_distance(U: np.ndarray, V: np.ndarray) -> float:
    """
    Frobenius distance between projectors.

    ||P_U - P_V||_F = sqrt(chordal_distance_sq(U, V))

    Parameters
    ----------
    U, V : ndarray
        Orthonormal bases

    Returns
    -------
    d : float
        Frobenius distance
    """
    return chordal_distance(U, V)


def projection_distance(U: np.ndarray, V: np.ndarray) -> float:
    """
    Projection distance (operator norm).

    ||P_U - P_V||₂ = sin(θ_max)

    where θ_max is the largest principal angle.

    Parameters
    ----------
    U, V : ndarray
        Orthonormal bases (same k)

    Returns
    -------
    d : float
        Projection distance
    """
    theta = principal_angles(U, V)
    if len(theta) == 0:
        return 0.0
    return np.sin(theta[-1])


def gap_distance(U: np.ndarray, V: np.ndarray) -> float:
    """
    Gap (containment) distance.

    Measures how far U and V are from having containment relation.
    Gap = 0 iff span(U) ⊆ span(V) or span(V) ⊆ span(U).

    Parameters
    ----------
    U : ndarray, shape (n, k)
        First basis
    V : ndarray, shape (n, k')
        Second basis

    Returns
    -------
    gap : float
        Containment gap
    """
    k, k_prime = U.shape[1], V.shape[1]
    d2 = chordal_distance_sq(U, V)

    # Sharp bound: d² ≥ |k - k'|
    # Gap is the excess over the bound
    return d2 - abs(k - k_prime)


def binet_cauchy_distance(U: np.ndarray, V: np.ndarray) -> float:
    """
    Binet-Cauchy distance.

    d_BC = sqrt(1 - det(U^T V)²) for same k.

    Parameters
    ----------
    U, V : ndarray
        Orthonormal bases with same k

    Returns
    -------
    d : float
        Binet-Cauchy distance in [0, 1]
    """
    if U.shape[1] != V.shape[1]:
        raise ValueError("Binet-Cauchy distance requires same k")

    det_sq = np.linalg.det(U.T @ V) ** 2
    return np.sqrt(max(0.0, 1.0 - det_sq))


def asimov_distance(U: np.ndarray, V: np.ndarray) -> float:
    """
    Asimov distance (maximum principal angle).

    d_A = θ_max = max principal angle

    Parameters
    ----------
    U, V : ndarray
        Orthonormal bases

    Returns
    -------
    d : float
        Asimov distance in [0, π/2]
    """
    theta = principal_angles(U, V)
    if len(theta) == 0:
        return 0.0
    return theta[-1]


def martin_distance(U: np.ndarray, V: np.ndarray) -> float:
    """
    Martin distance.

    d_M = sqrt(-2 * log(prod(cos(θᵢ))))

    Parameters
    ----------
    U, V : ndarray
        Orthonormal bases with same k

    Returns
    -------
    d : float
        Martin distance
    """
    if U.shape[1] != V.shape[1]:
        raise ValueError("Martin distance requires same k")

    theta = principal_angles(U, V)
    cos_theta = np.cos(theta)

    # Handle zero angles
    cos_theta = np.maximum(cos_theta, 1e-15)

    return np.sqrt(-2 * np.sum(np.log(cos_theta)))
