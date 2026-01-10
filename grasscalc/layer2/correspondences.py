"""
Correspondences between Grassmannians.

Implements primitive correspondences:
- C⁺: Raise-k (incidence) - W is successor of V iff V ⊂ W
- C↑: Raise-n (stabilization) - embed into larger ambient space
"""

import numpy as np
from numpy.linalg import qr
from typing import List, Optional, Tuple

from ..core.linalg import stable_qr, extend_orthonormal_basis
from ..core.representations import stabilize


def raise_k_successors(
    U: np.ndarray,
    k_next: int,
    n_candidates: int = 10,
    rng: Optional[np.random.Generator] = None
) -> List[np.ndarray]:
    """
    Generate successors W ⊃ U with dim(W) = k_next (Raise-k correspondence C⁺).

    For k_next > k: W contains U as a subspace.
    For k_next < k: W is contained in U.

    Parameters
    ----------
    U : ndarray, shape (n, k)
        Current subspace basis
    k_next : int
        Target dimension
    n_candidates : int
        Number of candidates to generate
    rng : Generator, optional
        Random number generator

    Returns
    -------
    successors : list of ndarray
        List of candidate successors, each shape (n, k_next)
    """
    if rng is None:
        rng = np.random.default_rng()

    n, k = U.shape
    successors = []

    if k_next == k:
        # Same dimension - return U itself
        return [U.copy()]

    elif k_next > k:
        # Extend U: add random orthogonal vectors
        for _ in range(n_candidates):
            extra = k_next - k
            # Random vectors
            A = rng.standard_normal((n, extra))
            # Project to orthogonal complement of U
            A = A - U @ (U.T @ A)
            # Orthonormalize
            if np.linalg.norm(A) > 1e-10:
                Q, _ = stable_qr(A)
                W = np.hstack([U, Q])
                successors.append(W)

    else:
        # Contract U: random k_next-dimensional subspaces of span(U)
        for _ in range(n_candidates):
            # Random rotation within span(U)
            R = rng.standard_normal((k, k_next))
            R, _ = stable_qr(R)
            W = U @ R
            W, _ = stable_qr(W)
            successors.append(W)

    return successors


def raise_n_successors(
    U: np.ndarray,
    n_next: int
) -> np.ndarray:
    """
    Stabilize U into larger ambient R^{n_next} (Raise-n correspondence C↑).

    This achieves d² = 0 (no change in k, just embedding).

    Parameters
    ----------
    U : ndarray, shape (n, k)
        Current subspace basis
    n_next : int
        Target ambient dimension (must be >= n)

    Returns
    -------
    V : ndarray, shape (n_next, k)
        Stabilized basis
    """
    n, k = U.shape

    if n_next < n:
        raise ValueError(f"n_next ({n_next}) must be >= n ({n})")

    if n_next == n:
        return U.copy()

    return stabilize(U, n, n_next)


def compose_correspondences(
    U: np.ndarray,
    transitions: List[Tuple[str, dict]],
    rng: Optional[np.random.Generator] = None
) -> List[np.ndarray]:
    """
    Compose multiple primitive correspondences.

    Parameters
    ----------
    U : ndarray
        Starting subspace
    transitions : list of (type, params) tuples
        type: 'raise_k' or 'raise_n'
        params: dict with 'k_next' or 'n_next'
    rng : Generator, optional
        Random number generator

    Returns
    -------
    results : list of ndarray
        Resulting subspaces after composition
    """
    if rng is None:
        rng = np.random.default_rng()

    current = [U.copy()]

    for trans_type, params in transitions:
        next_gen = []

        for V in current:
            if trans_type == 'raise_k':
                k_next = params.get('k_next')
                n_cand = params.get('n_candidates', 1)
                successors = raise_k_successors(V, k_next, n_cand, rng)
                next_gen.extend(successors)

            elif trans_type == 'raise_n':
                n_next = params.get('n_next')
                W = raise_n_successors(V, n_next)
                next_gen.append(W)

            else:
                raise ValueError(f"Unknown transition type: {trans_type}")

        current = next_gen

    return current


def incidence_variety(k: int, k_prime: int, n: int) -> str:
    """
    Describe the incidence variety between Gr(k,n) and Gr(k',n).

    Parameters
    ----------
    k, k_prime : int
        Fiber dimensions
    n : int
        Ambient dimension

    Returns
    -------
    description : str
        Mathematical description
    """
    if k < k_prime:
        return f"I(k,k') = {{(V,W) : V ⊂ W}} ⊂ Gr({k},{n}) × Gr({k_prime},{n})"
    elif k > k_prime:
        return f"I(k,k') = {{(V,W) : W ⊂ V}} ⊂ Gr({k},{n}) × Gr({k_prime},{n})"
    else:
        return f"Diagonal: V = W in Gr({k},{n})"


def transition_from_to(
    U: np.ndarray,
    k_target: int,
    n_target: int,
    n_candidates: int = 10,
    rng: Optional[np.random.Generator] = None
) -> List[np.ndarray]:
    """
    Generate candidates for transition from Gr(k,n) to Gr(k',n').

    Combines raise-k and raise-n as needed.

    Parameters
    ----------
    U : ndarray, shape (n, k)
        Current point
    k_target : int
        Target fiber dimension
    n_target : int
        Target ambient dimension
    n_candidates : int
        Number of candidates
    rng : Generator, optional
        Random generator

    Returns
    -------
    candidates : list of ndarray
        Candidate points in Gr(k_target, n_target)
    """
    if rng is None:
        rng = np.random.default_rng()

    n, k = U.shape
    N = max(n, n_target)

    # First stabilize to common ambient
    U_stab = stabilize(U, n, N)

    # Generate k-changes
    if k_target != k:
        intermediates = raise_k_successors(U_stab, k_target, n_candidates, rng)
    else:
        intermediates = [U_stab]

    # Then adjust ambient dimension
    candidates = []
    for W in intermediates:
        if N == n_target:
            candidates.append(W)
        elif N > n_target:
            # Truncate (project to first n_target coords)
            W_trunc = W[:n_target, :]
            W_trunc, _ = stable_qr(W_trunc)
            candidates.append(W_trunc)
        else:
            # Extend with zeros
            W_ext = stabilize(W, N, n_target)
            candidates.append(W_ext)

    return candidates
