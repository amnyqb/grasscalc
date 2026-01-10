"""
Tangent space operations on Grassmannian manifolds.

The tangent space T_U Gr(k,n) at a point U consists of matrices Xi
satisfying U^T Xi = 0 (horizontal space model).
"""

import numpy as np
from numpy.linalg import norm, svd
from typing import Tuple, Optional


def tangent_project(U: np.ndarray, A: np.ndarray) -> np.ndarray:
    """
    Project a matrix onto the tangent space at U.

    The tangent space at U ∈ Gr(k,n) consists of matrices Xi with U^T Xi = 0.
    Projection: Xi = A - U @ sym(U^T A) = (I - U U^T) A

    Parameters
    ----------
    U : ndarray, shape (n, k)
        Orthonormal basis representing point on Grassmannian
    A : ndarray, shape (n, k)
        Matrix to project

    Returns
    -------
    Xi : ndarray, shape (n, k)
        Tangent vector satisfying U^T Xi = 0
    """
    # Xi = A - U @ (U^T @ A)
    return A - U @ (U.T @ A)


def horizontal_lift(U: np.ndarray, A: np.ndarray) -> np.ndarray:
    """
    Compute the horizontal lift of a matrix to the tangent space.

    Alias for tangent_project, using terminology from fiber bundle theory.

    Parameters
    ----------
    U : ndarray, shape (n, k)
        Base point
    A : ndarray, shape (n, k)
        Matrix to lift

    Returns
    -------
    Xi : ndarray
        Horizontal tangent vector
    """
    return tangent_project(U, A)


def tangent_inner_product(U: np.ndarray, Xi: np.ndarray, Eta: np.ndarray) -> float:
    """
    Riemannian inner product on the tangent space.

    For the canonical metric: <Xi, Eta>_U = trace(Xi^T Eta)

    Parameters
    ----------
    U : ndarray, shape (n, k)
        Base point (not used for canonical metric, included for API consistency)
    Xi : ndarray, shape (n, k)
        First tangent vector
    Eta : ndarray, shape (n, k)
        Second tangent vector

    Returns
    -------
    inner : float
        Inner product
    """
    return np.trace(Xi.T @ Eta)


def tangent_norm(U: np.ndarray, Xi: np.ndarray) -> float:
    """
    Riemannian norm of a tangent vector.

    ||Xi||_U = sqrt(<Xi, Xi>_U) = ||Xi||_F

    Parameters
    ----------
    U : ndarray, shape (n, k)
        Base point
    Xi : ndarray, shape (n, k)
        Tangent vector

    Returns
    -------
    norm : float
        Riemannian norm
    """
    return norm(Xi, 'fro')


def is_tangent(U: np.ndarray, Xi: np.ndarray, tol: float = 1e-10) -> bool:
    """
    Check if Xi is a valid tangent vector at U.

    Parameters
    ----------
    U : ndarray, shape (n, k)
        Base point
    Xi : ndarray, shape (n, k)
        Candidate tangent vector
    tol : float
        Tolerance

    Returns
    -------
    bool
        True if U^T Xi ≈ 0
    """
    return norm(U.T @ Xi) < tol


def random_tangent(U: np.ndarray, rng: Optional[np.random.Generator] = None) -> np.ndarray:
    """
    Generate a random unit tangent vector at U.

    Parameters
    ----------
    U : ndarray, shape (n, k)
        Base point
    rng : Generator, optional
        Random number generator

    Returns
    -------
    Xi : ndarray, shape (n, k)
        Random unit tangent vector
    """
    if rng is None:
        rng = np.random.default_rng()

    n, k = U.shape
    A = rng.standard_normal((n, k))
    Xi = tangent_project(U, A)

    # Normalize to unit norm
    Xi_norm = tangent_norm(U, Xi)
    if Xi_norm > 1e-14:
        Xi = Xi / Xi_norm

    return Xi


def parallel_transport(U: np.ndarray, V: np.ndarray, Xi: np.ndarray) -> np.ndarray:
    """
    Parallel transport of tangent vector from U to V along geodesic.

    Uses the closed-form expression for Grassmannian parallel transport.

    Parameters
    ----------
    U : ndarray, shape (n, k)
        Starting point
    V : ndarray, shape (n, k)
        Ending point (same k)
    Xi : ndarray, shape (n, k)
        Tangent vector at U

    Returns
    -------
    Xi_V : ndarray, shape (n, k)
        Parallel transported tangent vector at V
    """
    if U.shape[1] != V.shape[1]:
        raise ValueError("Parallel transport requires same k")

    n, k = U.shape

    # Get geodesic parameters via SVD of M = U^T @ V
    M = U.T @ V
    Um, cos_theta, Vmt = svd(M, full_matrices=False)
    Vm = Vmt.T

    # Compute angles
    cos_theta = np.clip(cos_theta, -1.0, 1.0)
    theta = np.arccos(cos_theta)
    sin_theta = np.sin(theta)

    # Compute the orthonormal directions W in the complement of U
    V_perp_aligned = V @ Vm - U @ (Um * cos_theta)
    W = np.zeros_like(V_perp_aligned)
    for i in range(k):
        if sin_theta[i] > 1e-10:
            W[:, i] = V_perp_aligned[:, i] / sin_theta[i]

    # At point V, the analogous directions are:
    # The "U direction" at U (which is U @ Um) becomes the "V direction" at V (V @ Vm)
    # The "W direction" at U becomes W_V at V (orthogonal to V)

    # For parallel transport, components in the U@Um / W plane get rotated,
    # while components orthogonal to this plane are unchanged

    # Express Xi in the W basis (Xi is tangent at U, so Xi = (I - UU^T) @ something)
    # Component of Xi along each W column
    Xi_W_coeff = W.T @ Xi  # k x k matrix

    # Component of Xi orthogonal to W (and to U)
    Xi_rest = Xi - W @ Xi_W_coeff

    # After parallel transport:
    # - Xi_rest (orthogonal to geodesic direction) gets projected to tangent at V
    # - Xi_W components get rotated

    # The W directions at V: W_V = (I - VV^T) @ W (project W to orthogonal complement of V)
    W_at_V = W - V @ (V.T @ W)

    # Orthonormalize W_at_V
    for i in range(k):
        if sin_theta[i] > 1e-10:
            # The transported W[:,i] should have unit norm if original was unit
            w_norm = norm(W_at_V[:, i])
            if w_norm > 1e-10:
                W_at_V[:, i] = W_at_V[:, i] / w_norm

    # Construct transported tangent vector
    Xi_V = Xi_rest - V @ (V.T @ Xi_rest) + W_at_V @ Xi_W_coeff

    return tangent_project(V, Xi_V)


def exponential_map(U: np.ndarray, Xi: np.ndarray) -> np.ndarray:
    """
    Riemannian exponential map on the Grassmannian.

    Exp_U(Xi) computes the endpoint of the geodesic starting at U
    with initial velocity Xi.

    Uses the standard formula based on SVD of the tangent vector.

    Parameters
    ----------
    U : ndarray, shape (n, k)
        Base point
    Xi : ndarray, shape (n, k)
        Tangent vector at U

    Returns
    -------
    V : ndarray, shape (n, k)
        Endpoint of geodesic
    """
    n, k = U.shape

    # Handle zero tangent vector
    Xi_norm = norm(Xi, 'fro')
    if Xi_norm < 1e-14:
        return U.copy()

    # Thin SVD: Xi = W @ S @ Vt where W is n×k, S is k×k, Vt is k×k
    W, s, Vt = svd(Xi, full_matrices=False)

    # The geodesic is:
    # gamma(t) = U @ V @ cos(t*S) @ Vt + W @ sin(t*S) @ Vt
    # At t=1: gamma(1) = U @ V @ cos(S) @ Vt + W @ sin(S) @ Vt
    V_mat = Vt.T  # k x k

    cos_s = np.diag(np.cos(s))
    sin_s = np.diag(np.sin(s))

    # Result: gamma(1) = [U @ V, W] @ [[cos(S)], [sin(S)]] @ Vt
    result = U @ V_mat @ cos_s @ Vt + W @ sin_s @ Vt

    # Orthonormalize
    result, _ = np.linalg.qr(result)

    return result


def logarithm_map(U: np.ndarray, V: np.ndarray) -> np.ndarray:
    """
    Riemannian logarithm map on the Grassmannian.

    Log_U(V) computes the initial velocity of the geodesic from U to V.

    Parameters
    ----------
    U : ndarray, shape (n, k)
        Base point
    V : ndarray, shape (n, k)
        Target point (same k)

    Returns
    -------
    Xi : ndarray, shape (n, k)
        Tangent vector at U such that Exp_U(Xi) = V
    """
    if U.shape[1] != V.shape[1]:
        raise ValueError("Logarithm map requires same k")

    n, k = U.shape

    # Use SVD of M = U^T @ V to get consistent bases
    M = U.T @ V  # k x k
    Um, cos_theta, Vmt = svd(M, full_matrices=False)

    # Clamp cos values and compute angles
    cos_theta = np.clip(cos_theta, -1.0, 1.0)
    theta = np.arccos(cos_theta)

    # Compute the tangent directions in aligned basis
    # V_perp in the Vm basis: (I - UU^T) @ V @ Vm
    Vm = Vmt.T
    V_perp_aligned = V @ Vm - U @ (Um * cos_theta)  # n x k

    # Normalize columns to get unit directions (handle zero angles)
    sin_theta = np.sin(theta)
    W = np.zeros_like(V_perp_aligned)
    for i in range(k):
        if sin_theta[i] > 1e-10:
            W[:, i] = V_perp_aligned[:, i] / sin_theta[i]
        else:
            # Zero angle: arbitrary orthogonal direction
            W[:, i] = V_perp_aligned[:, i]

    # Tangent vector: Xi = W @ diag(theta) @ Um^T
    # This ensures exp_U(Xi) aligns with V
    Xi = W @ np.diag(theta) @ Um.T

    return Xi


def geodesic(U: np.ndarray, V: np.ndarray, t: float) -> np.ndarray:
    """
    Point on geodesic from U to V at parameter t.

    Parameters
    ----------
    U : ndarray, shape (n, k)
        Starting point
    V : ndarray, shape (n, k)
        Ending point
    t : float
        Parameter in [0, 1], where t=0 gives U and t=1 gives V

    Returns
    -------
    W : ndarray, shape (n, k)
        Point on geodesic at parameter t
    """
    if t == 0:
        return U.copy()
    if t == 1:
        return V.copy()

    # Compute initial velocity
    Xi = logarithm_map(U, V)

    # Scale and exponentiate
    return exponential_map(U, t * Xi)


def curvature_tensor(U: np.ndarray, Xi: np.ndarray, Eta: np.ndarray, Zeta: np.ndarray) -> np.ndarray:
    """
    Riemannian curvature tensor R(Xi, Eta)Zeta at U.

    For the Grassmannian with canonical metric:
    R(Xi, Eta)Zeta = [[Xi, Eta], Zeta]
    where [A, B] = AB - BA is the commutator.

    Parameters
    ----------
    U : ndarray, shape (n, k)
        Base point
    Xi, Eta, Zeta : ndarray, shape (n, k)
        Tangent vectors at U

    Returns
    -------
    R_XiEta_Zeta : ndarray, shape (n, k)
        Curvature tensor applied to Zeta
    """
    # Compute shape operators
    A_Xi = U @ Xi.T + Xi @ U.T  # Shape operator for Xi
    A_Eta = U @ Eta.T + Eta @ U.T  # Shape operator for Eta

    # Commutator
    commutator = A_Xi @ A_Eta - A_Eta @ A_Xi

    # Apply to Zeta and project to tangent space
    result = commutator @ Zeta
    return tangent_project(U, result)


def sectional_curvature(U: np.ndarray, Xi: np.ndarray, Eta: np.ndarray) -> float:
    """
    Sectional curvature of the plane spanned by Xi and Eta.

    Parameters
    ----------
    U : ndarray, shape (n, k)
        Base point
    Xi, Eta : ndarray, shape (n, k)
        Orthonormal tangent vectors spanning the plane

    Returns
    -------
    K : float
        Sectional curvature
    """
    R_XiEta_Eta = curvature_tensor(U, Xi, Eta, Eta)
    numerator = tangent_inner_product(U, R_XiEta_Eta, Xi)

    # Denominator: <Xi,Xi><Eta,Eta> - <Xi,Eta>^2
    Xi_norm_sq = tangent_inner_product(U, Xi, Xi)
    Eta_norm_sq = tangent_inner_product(U, Eta, Eta)
    Xi_Eta = tangent_inner_product(U, Xi, Eta)
    denominator = Xi_norm_sq * Eta_norm_sq - Xi_Eta ** 2

    if abs(denominator) < 1e-14:
        return 0.0

    return numerator / denominator
