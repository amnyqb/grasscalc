"""
Representations for points on Grassmannian manifolds.

Supports multiple representations:
- Orthonormal basis U ∈ R^{n×k} (canonical)
- Projector P ∈ R^{n×n} with P² = P, P^T = P, rank(P) = k
- Stabilized basis for cross-manifold operations
"""

import numpy as np
from numpy.linalg import norm, matrix_rank
from typing import Optional, Union, Tuple
from dataclasses import dataclass, field

from .linalg import stable_qr, is_orthonormal


@dataclass
class GrassmannPoint:
    """
    A point on the Grassmannian manifold Gr(k, n).

    Represents a k-dimensional subspace of R^n.

    Parameters
    ----------
    basis : ndarray, shape (n, k)
        Orthonormal basis for the subspace
    k : int
        Fiber dimension (number of basis vectors)
    n : int
        Ambient dimension

    Attributes
    ----------
    dimension : int
        Grassmannian dimension k(n-k)
    codimension : int
        n - k
    """
    basis: np.ndarray
    k: int = field(init=False)
    n: int = field(init=False)

    def __post_init__(self):
        self.n, self.k = self.basis.shape
        # Ensure orthonormality
        if not is_orthonormal(self.basis):
            self.basis, _ = stable_qr(self.basis)

    @property
    def dimension(self) -> int:
        """Grassmannian dimension D = k(n-k)."""
        return self.k * (self.n - self.k)

    @property
    def codimension(self) -> int:
        """Codimension c = n - k."""
        return self.n - self.k

    @property
    def projector(self) -> np.ndarray:
        """Orthogonal projector P = U @ U^T."""
        return self.basis @ self.basis.T

    def stabilize(self, N: int) -> 'GrassmannPoint':
        """
        Embed into larger ambient space R^N.

        Parameters
        ----------
        N : int
            New ambient dimension (must be >= n)

        Returns
        -------
        GrassmannPoint
            Stabilized point in Gr(k, N)
        """
        if N < self.n:
            raise ValueError(f"N ({N}) must be >= n ({self.n})")
        if N == self.n:
            return self

        U_stab = np.zeros((N, self.k))
        U_stab[:self.n, :] = self.basis
        return GrassmannPoint(U_stab)

    def __repr__(self) -> str:
        return f"GrassmannPoint(k={self.k}, n={self.n}, dim={self.dimension})"

    @classmethod
    def from_projector(cls, P: np.ndarray, k: Optional[int] = None) -> 'GrassmannPoint':
        """
        Create from projector matrix.

        Parameters
        ----------
        P : ndarray, shape (n, n)
            Orthogonal projector (P² = P, P^T = P)
        k : int, optional
            Expected rank (computed if not provided)

        Returns
        -------
        GrassmannPoint
        """
        if k is None:
            k = int(round(np.trace(P)))

        # Extract basis via eigendecomposition
        eigenvalues, eigenvectors = np.linalg.eigh(P)
        # Sort by eigenvalue descending
        idx = np.argsort(eigenvalues)[::-1]
        basis = eigenvectors[:, idx[:k]]

        return cls(basis)

    @classmethod
    def from_vectors(cls, vectors: np.ndarray) -> 'GrassmannPoint':
        """
        Create from arbitrary spanning vectors (not necessarily orthonormal).

        Parameters
        ----------
        vectors : ndarray, shape (n, k)
            Vectors spanning the subspace

        Returns
        -------
        GrassmannPoint
        """
        basis, _ = stable_qr(vectors)
        return cls(basis)


def to_projector(U: np.ndarray) -> np.ndarray:
    """
    Convert orthonormal basis to projector.

    Parameters
    ----------
    U : ndarray, shape (n, k)
        Orthonormal basis

    Returns
    -------
    P : ndarray, shape (n, n)
        Orthogonal projector P = U @ U^T
    """
    return U @ U.T


def to_basis(P: np.ndarray, k: Optional[int] = None) -> np.ndarray:
    """
    Convert projector to orthonormal basis.

    Parameters
    ----------
    P : ndarray, shape (n, n)
        Orthogonal projector
    k : int, optional
        Expected rank (computed from trace if not provided)

    Returns
    -------
    U : ndarray, shape (n, k)
        Orthonormal basis
    """
    if k is None:
        k = int(round(np.trace(P)))

    eigenvalues, eigenvectors = np.linalg.eigh(P)
    idx = np.argsort(eigenvalues)[::-1]
    return eigenvectors[:, idx[:k]]


def stabilize(U: np.ndarray, n: int, N: int) -> np.ndarray:
    """
    Stabilize a basis from R^n to R^N.

    Embeds the subspace into larger ambient space by padding with zeros.

    Parameters
    ----------
    U : ndarray, shape (n, k)
        Orthonormal basis in R^n
    n : int
        Current ambient dimension (should match U.shape[0])
    N : int
        Target ambient dimension

    Returns
    -------
    U_stab : ndarray, shape (N, k)
        Stabilized basis
    """
    if N < n:
        raise ValueError(f"N ({N}) must be >= n ({n})")
    if N == n:
        return U.copy()

    k = U.shape[1]
    U_stab = np.zeros((N, k))
    U_stab[:n, :] = U
    return U_stab


def destabilize(U_stab: np.ndarray, n: int) -> np.ndarray:
    """
    Extract the active part of a stabilized basis.

    Parameters
    ----------
    U_stab : ndarray, shape (N, k)
        Stabilized basis
    n : int
        Original ambient dimension

    Returns
    -------
    U : ndarray, shape (n, k)
        Original basis (first n rows)
    """
    return U_stab[:n, :].copy()


def subspace_equal(U: np.ndarray, V: np.ndarray, tol: float = 1e-10) -> bool:
    """
    Check if two bases span the same subspace.

    Parameters
    ----------
    U, V : ndarray
        Orthonormal bases (must have same shape)
    tol : float
        Tolerance for comparison

    Returns
    -------
    bool
        True if span(U) = span(V)
    """
    if U.shape != V.shape:
        return False

    # Check that U^T V is orthogonal (singular values all 1)
    s = np.linalg.svd(U.T @ V, compute_uv=False)
    return np.allclose(s, 1.0, atol=tol)


def subspace_contains(U: np.ndarray, V: np.ndarray, tol: float = 1e-10) -> bool:
    """
    Check if span(U) ⊆ span(V).

    Parameters
    ----------
    U : ndarray, shape (n, k)
        Basis for potential subspace
    V : ndarray, shape (n, k')
        Basis for containing space
    tol : float
        Tolerance

    Returns
    -------
    bool
        True if span(U) ⊆ span(V)
    """
    # Project U onto span(V)
    P_V = V @ V.T
    U_proj = P_V @ U

    # Check if projection equals original
    return norm(U - U_proj) < tol * norm(U)
