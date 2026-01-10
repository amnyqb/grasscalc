"""
Macro-variable calculus for coarse-grained Grassmannian dynamics.

Defines macro variables:
- c(t) = n - k (codimension)
- D(t) = k(n-k) (Grassmannian dimension)
- ρ(t) = k/n (aspect ratio)
"""

import numpy as np
from typing import Dict, List, Tuple, Optional


def codimension(k: int, n: int) -> int:
    """Codimension c = n - k."""
    return n - k


def grassmann_dimension(k: int, n: int) -> int:
    """Grassmannian dimension D = k(n-k)."""
    return k * (n - k)


def aspect_ratio(k: int, n: int) -> float:
    """Aspect ratio ρ = k/n."""
    return k / n


def macro_variables(k: int, n: int) -> Dict:
    """
    Compute all macro variables for Gr(k,n).

    Parameters
    ----------
    k : int
        Fiber dimension
    n : int
        Ambient dimension

    Returns
    -------
    dict
        'k': int
        'n': int
        'c': int - codimension
        'D': int - Grassmannian dimension
        'rho': float - aspect ratio
        'complement_dim': int - k' = n - k
    """
    return {
        'k': k,
        'n': n,
        'c': n - k,
        'D': k * (n - k),
        'rho': k / n,
        'complement_dim': n - k
    }


def macro_trajectory(chain: List[Tuple[int, int]]) -> Dict:
    """
    Compute macro-variable trajectory along a chain.

    Parameters
    ----------
    chain : list of (k, n) tuples
        Grassmannian chain

    Returns
    -------
    dict
        'k': list
        'n': list
        'c': list
        'D': list
        'rho': list
        'total_D': int - sum of dimensions
    """
    k_list = [kn[0] for kn in chain]
    n_list = [kn[1] for kn in chain]
    c_list = [n - k for k, n in chain]
    D_list = [k * (n - k) for k, n in chain]
    rho_list = [k / n for k, n in chain]

    return {
        'k': k_list,
        'n': n_list,
        'c': c_list,
        'D': D_list,
        'rho': rho_list,
        'total_D': sum(D_list),
        'stages': len(chain)
    }


def delta_variables(chain: List[Tuple[int, int]]) -> Dict:
    """
    Compute increments Δk, Δn, Δc, ΔD along chain.

    Parameters
    ----------
    chain : list of (k, n) tuples

    Returns
    -------
    dict
        'delta_k': list
        'delta_n': list
        'delta_c': list
        'delta_D': list
    """
    if len(chain) < 2:
        return {'delta_k': [], 'delta_n': [], 'delta_c': [], 'delta_D': []}

    delta_k = []
    delta_n = []
    delta_c = []
    delta_D = []

    for i in range(1, len(chain)):
        k_prev, n_prev = chain[i-1]
        k_next, n_next = chain[i]

        delta_k.append(k_next - k_prev)
        delta_n.append(n_next - n_prev)
        delta_c.append((n_next - k_next) - (n_prev - k_prev))
        delta_D.append(k_next * (n_next - k_next) - k_prev * (n_prev - k_prev))

    return {
        'delta_k': delta_k,
        'delta_n': delta_n,
        'delta_c': delta_c,
        'delta_D': delta_D
    }


def effective_dimension(k: int, n: int, regime: str = 'bulk') -> float:
    """
    Effective dimension in various regimes.

    Parameters
    ----------
    k : int
        Fiber dimension
    n : int
        Ambient dimension
    regime : str
        'bulk': standard D = k(n-k)
        'edge_k': k << n regime, D ≈ k*n
        'edge_c': c << n regime, D ≈ c*n
        'symmetric': k = n/2 regime, D = n²/4

    Returns
    -------
    D_eff : float
        Effective dimension
    """
    c = n - k

    if regime == 'bulk':
        return k * c
    elif regime == 'edge_k':
        return k * n  # Leading term when k << c
    elif regime == 'edge_c':
        return c * n  # Leading term when c << k
    elif regime == 'symmetric':
        return n * n / 4  # Maximum at k = n/2
    else:
        raise ValueError(f"Unknown regime: {regime}")


def scale_factor(k1: int, n1: int, k2: int, n2: int) -> float:
    """
    Scale factor between two Grassmannians.

    λ = D_2 / D_1

    Parameters
    ----------
    k1, n1 : int
        First Grassmannian
    k2, n2 : int
        Second Grassmannian

    Returns
    -------
    lambda : float
        Scale factor
    """
    D1 = k1 * (n1 - k1)
    D2 = k2 * (n2 - k2)

    if D1 == 0:
        return float('inf') if D2 > 0 else 1.0

    return D2 / D1


def cumulative_dimension(chain: List[Tuple[int, int]]) -> List[int]:
    """
    Cumulative dimension along chain.

    Parameters
    ----------
    chain : list of (k, n) tuples

    Returns
    -------
    cum_D : list
        Cumulative sums of dimensions
    """
    D_list = [k * (n - k) for k, n in chain]
    return list(np.cumsum(D_list))
