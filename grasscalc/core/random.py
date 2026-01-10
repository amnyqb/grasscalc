"""
Random sampling on Grassmannian manifolds.

Provides uniform sampling from Gr(k,n) and related distributions.
"""

import numpy as np
from numpy.linalg import qr
from typing import Optional

from .linalg import stable_qr


def sample_grassmann(
    k: int,
    n: int,
    rng: Optional[np.random.Generator] = None
) -> np.ndarray:
    """
    Sample uniformly from Grassmannian Gr(k,n).

    Uses the standard method: generate n×k Gaussian matrix and orthonormalize.

    Parameters
    ----------
    k : int
        Fiber dimension
    n : int
        Ambient dimension
    rng : Generator, optional
        Random number generator (uses default if not provided)

    Returns
    -------
    U : ndarray, shape (n, k)
        Orthonormal basis representing uniform sample from Gr(k,n)
    """
    if rng is None:
        rng = np.random.default_rng()

    if k > n:
        raise ValueError(f"k ({k}) cannot exceed n ({n})")
    if k < 1 or n < 1:
        raise ValueError("k and n must be positive")

    # Generate Gaussian random matrix
    A = rng.standard_normal((n, k))

    # Orthonormalize (Q factor gives uniform sample)
    U, _ = stable_qr(A)

    return U


def sample_tangent(
    U: np.ndarray,
    rng: Optional[np.random.Generator] = None,
    normalize: bool = True
) -> np.ndarray:
    """
    Sample a random tangent vector at U.

    Parameters
    ----------
    U : ndarray, shape (n, k)
        Base point on Grassmannian
    rng : Generator, optional
        Random number generator
    normalize : bool, default True
        If True, return unit norm tangent vector

    Returns
    -------
    Xi : ndarray, shape (n, k)
        Random tangent vector at U
    """
    if rng is None:
        rng = np.random.default_rng()

    n, k = U.shape

    # Generate random matrix
    A = rng.standard_normal((n, k))

    # Project to tangent space: Xi = A - U @ (U^T @ A)
    Xi = A - U @ (U.T @ A)

    if normalize:
        norm = np.linalg.norm(Xi, 'fro')
        if norm > 1e-14:
            Xi = Xi / norm

    return Xi


def sample_geodesic_endpoint(
    U: np.ndarray,
    distance: float,
    rng: Optional[np.random.Generator] = None
) -> np.ndarray:
    """
    Sample a point at specified geodesic distance from U.

    Parameters
    ----------
    U : ndarray, shape (n, k)
        Starting point
    distance : float
        Geodesic distance to sample at
    rng : Generator, optional
        Random number generator

    Returns
    -------
    V : ndarray, shape (n, k)
        Random point at specified distance from U
    """
    from .tangent import exponential_map

    # Sample random direction
    Xi = sample_tangent(U, rng, normalize=True)

    # Scale to desired distance
    Xi = distance * Xi

    # Exponentiate
    return exponential_map(U, Xi)


def sample_near(
    U: np.ndarray,
    epsilon: float,
    rng: Optional[np.random.Generator] = None
) -> np.ndarray:
    """
    Sample a point within epsilon distance of U.

    Samples uniformly in a geodesic ball.

    Parameters
    ----------
    U : ndarray, shape (n, k)
        Center point
    epsilon : float
        Maximum distance
    rng : Generator, optional
        Random number generator

    Returns
    -------
    V : ndarray, shape (n, k)
        Random point within epsilon of U
    """
    if rng is None:
        rng = np.random.default_rng()

    n, k = U.shape
    dim = k * (n - k)

    # Sample distance uniformly in ball (need r^dim weighting)
    r = epsilon * (rng.random() ** (1.0 / dim))

    return sample_geodesic_endpoint(U, r, rng)


def sample_batch(
    k: int,
    n: int,
    batch_size: int,
    rng: Optional[np.random.Generator] = None
) -> np.ndarray:
    """
    Sample a batch of points from Gr(k,n).

    Parameters
    ----------
    k : int
        Fiber dimension
    n : int
        Ambient dimension
    batch_size : int
        Number of samples
    rng : Generator, optional
        Random number generator

    Returns
    -------
    samples : ndarray, shape (batch_size, n, k)
        Batch of orthonormal bases
    """
    if rng is None:
        rng = np.random.default_rng()

    samples = np.zeros((batch_size, n, k))
    for i in range(batch_size):
        samples[i] = sample_grassmann(k, n, rng)

    return samples


def sample_with_containment(
    U: np.ndarray,
    k_new: int,
    rng: Optional[np.random.Generator] = None
) -> np.ndarray:
    """
    Sample a point V in Gr(k_new, n) with containment relation to U.

    If k_new > k: V ⊃ U (U contained in V)
    If k_new < k: V ⊂ U (V contained in U)

    Parameters
    ----------
    U : ndarray, shape (n, k)
        Reference point
    k_new : int
        Target fiber dimension
    rng : Generator, optional
        Random number generator

    Returns
    -------
    V : ndarray, shape (n, k_new)
        Point with containment relation to U
    """
    if rng is None:
        rng = np.random.default_rng()

    n, k = U.shape

    if k_new == k:
        return U.copy()

    if k_new > k:
        # Extend U with random orthogonal vectors
        extra = k_new - k
        A = rng.standard_normal((n, extra))
        # Project to orthogonal complement of U
        A = A - U @ (U.T @ A)
        Q, _ = stable_qr(A)
        V = np.hstack([U, Q])
        return V

    else:
        # Select random k_new-dimensional subspace of span(U)
        # Random rotation in span(U)
        R = rng.standard_normal((k, k_new))
        R, _ = stable_qr(R)
        V = U @ R
        V, _ = stable_qr(V)
        return V


def sample_path(
    U: np.ndarray,
    V: np.ndarray,
    n_points: int,
    rng: Optional[np.random.Generator] = None,
    noise: float = 0.0
) -> list:
    """
    Sample points along the geodesic from U to V.

    Parameters
    ----------
    U : ndarray
        Starting point
    V : ndarray
        Ending point
    n_points : int
        Number of points to sample (including endpoints)
    rng : Generator, optional
        For adding noise
    noise : float, default 0.0
        Standard deviation of Gaussian noise added to each point

    Returns
    -------
    path : list of ndarray
        Points along the geodesic
    """
    from .tangent import geodesic

    if rng is None:
        rng = np.random.default_rng()

    path = []
    for i in range(n_points):
        t = i / (n_points - 1) if n_points > 1 else 0.0
        W = geodesic(U, V, t)

        if noise > 0:
            Xi = sample_tangent(W, rng, normalize=True)
            from .linalg import qr_retraction
            W = qr_retraction(W, noise * Xi)

        path.append(W)

    return path
