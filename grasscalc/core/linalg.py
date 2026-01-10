"""
Linear algebra utilities for Grassmannian computations.

Provides numerically stable implementations of:
- QR decomposition with sign stabilization
- SVD with consistent sign conventions
- Gram-Schmidt orthonormalization
- Retraction operations
"""

import numpy as np
from numpy.linalg import qr, svd, norm
from typing import Tuple, Optional


def stable_qr(A: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute QR decomposition with sign stabilization.

    Ensures Q has positive diagonal elements in R, making the
    decomposition unique and numerically consistent.

    Parameters
    ----------
    A : ndarray, shape (n, k)
        Matrix to decompose

    Returns
    -------
    Q : ndarray, shape (n, k)
        Orthonormal columns
    R : ndarray, shape (k, k)
        Upper triangular with positive diagonal
    """
    Q, R = qr(A, mode='reduced')

    # Sign stabilization: ensure positive diagonal in R
    signs = np.sign(np.diag(R))
    signs[signs == 0] = 1  # Handle exact zeros

    Q = Q * signs
    R = R * signs[:, np.newaxis]

    return Q, R


def qr_retraction(U: np.ndarray, Xi: np.ndarray) -> np.ndarray:
    """
    QR retraction on the Grassmannian.

    Maps a tangent vector Xi at U to a new point on Gr(k,n).
    This is the standard retraction used in Grassmannian optimization.

    Parameters
    ----------
    U : ndarray, shape (n, k)
        Current point (orthonormal basis)
    Xi : ndarray, shape (n, k)
        Tangent vector at U (satisfies U^T Xi = 0)

    Returns
    -------
    U_new : ndarray, shape (n, k)
        New orthonormal basis representing the retracted point

    Notes
    -----
    Retr_U(Xi) = qf(U + Xi) where qf is the Q-factor of QR.
    """
    Q, _ = stable_qr(U + Xi)
    return Q


def svd_stable(A: np.ndarray, full_matrices: bool = False) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Compute SVD with consistent sign conventions.

    Ensures reproducible results by fixing signs of singular vectors.

    Parameters
    ----------
    A : ndarray
        Matrix to decompose
    full_matrices : bool, default False
        If True, return full U and Vh matrices

    Returns
    -------
    U : ndarray
        Left singular vectors
    s : ndarray
        Singular values (non-negative, descending)
    Vh : ndarray
        Right singular vectors (conjugate transpose)
    """
    U, s, Vh = svd(A, full_matrices=full_matrices)

    # Sign stabilization: ensure first nonzero element of each column of U is positive
    for i in range(U.shape[1]):
        col = U[:, i]
        first_nonzero_idx = np.argmax(np.abs(col) > 1e-14)
        if col[first_nonzero_idx] < 0:
            U[:, i] *= -1
            Vh[i, :] *= -1

    return U, s, Vh


def gram_schmidt(A: np.ndarray, tol: float = 1e-14) -> np.ndarray:
    """
    Modified Gram-Schmidt orthonormalization.

    More numerically stable than classical Gram-Schmidt.

    Parameters
    ----------
    A : ndarray, shape (n, k)
        Input matrix with k columns to orthonormalize
    tol : float, default 1e-14
        Tolerance for detecting zero vectors

    Returns
    -------
    Q : ndarray, shape (n, k)
        Orthonormal matrix with same span as A

    Raises
    ------
    ValueError
        If columns of A are linearly dependent
    """
    n, k = A.shape
    Q = np.zeros((n, k), dtype=A.dtype)

    for j in range(k):
        v = A[:, j].copy()

        # Subtract projections onto previous vectors
        for i in range(j):
            v -= np.dot(Q[:, i], v) * Q[:, i]

        v_norm = norm(v)
        if v_norm < tol:
            raise ValueError(f"Column {j} is linearly dependent on previous columns")

        Q[:, j] = v / v_norm

    return Q


def orthonormalize(U: np.ndarray) -> np.ndarray:
    """
    Ensure a basis matrix is orthonormal.

    Parameters
    ----------
    U : ndarray, shape (n, k)
        Basis matrix (possibly not perfectly orthonormal due to numerical drift)

    Returns
    -------
    U_orth : ndarray, shape (n, k)
        Orthonormal basis spanning the same subspace
    """
    Q, _ = stable_qr(U)
    return Q


def is_orthonormal(U: np.ndarray, tol: float = 1e-10) -> bool:
    """
    Check if a matrix has orthonormal columns.

    Parameters
    ----------
    U : ndarray, shape (n, k)
        Matrix to check
    tol : float, default 1e-10
        Tolerance for deviation from identity

    Returns
    -------
    bool
        True if U^T U ≈ I_k within tolerance
    """
    k = U.shape[1]
    UtU = U.T @ U
    return norm(UtU - np.eye(k)) < tol


def project_to_orthogonal_complement(v: np.ndarray, U: np.ndarray) -> np.ndarray:
    """
    Project vector v onto the orthogonal complement of span(U).

    Parameters
    ----------
    v : ndarray, shape (n,) or (n, 1)
        Vector to project
    U : ndarray, shape (n, k)
        Orthonormal basis

    Returns
    -------
    v_perp : ndarray
        Component of v orthogonal to span(U)
    """
    v = v.flatten()
    return v - U @ (U.T @ v)


def extend_orthonormal_basis(U: np.ndarray, k_new: int) -> np.ndarray:
    """
    Extend an orthonormal basis to span a larger subspace.

    Parameters
    ----------
    U : ndarray, shape (n, k)
        Current orthonormal basis
    k_new : int
        Target dimension (must be > k)

    Returns
    -------
    U_ext : ndarray, shape (n, k_new)
        Extended orthonormal basis with U as first k columns

    Raises
    ------
    ValueError
        If k_new <= k or k_new > n
    """
    n, k = U.shape
    if k_new <= k:
        raise ValueError(f"k_new ({k_new}) must be greater than k ({k})")
    if k_new > n:
        raise ValueError(f"k_new ({k_new}) cannot exceed n ({n})")

    # Generate random vectors and orthonormalize
    rng = np.random.default_rng()
    extra_vectors = rng.standard_normal((n, k_new - k))

    # Project onto orthogonal complement of U
    extra_vectors = extra_vectors - U @ (U.T @ extra_vectors)

    # Orthonormalize the extra vectors
    Q_extra, _ = stable_qr(extra_vectors)

    return np.hstack([U, Q_extra])
