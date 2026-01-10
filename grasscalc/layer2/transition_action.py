"""
Transition action and optimal transitions between Grassmannians.

The transition action measures the cost of moving from one Grassmannian to another:
J(W | V) = (s(W) - τ)² + μ·d²(V, W)
"""

import numpy as np
from typing import Callable, Dict, Optional, List

from ..core.distances import chordal_distance_sq
from ..core.representations import stabilize
from .sharp_bound import sharp_bound_check


def transition_action(
    U_prev: np.ndarray,
    U_next: np.ndarray,
    s_func: Callable[[np.ndarray], float],
    tau_next: float,
    mu: float,
    N: Optional[int] = None
) -> Dict:
    """
    Compute transition action J(W|V) = (s(W) - τ)² + μ·d²(V,W).

    Parameters
    ----------
    U_prev : ndarray, shape (n, k)
        Previous state
    U_next : ndarray, shape (n', k')
        Candidate next state
    s_func : callable
        Stage function s: Gr(k',n') → R
    tau_next : float
        Target value for s
    mu : float
        Continuity weight
    N : int, optional
        Ambient dimension for distance computation

    Returns
    -------
    dict
        'J': float - total action
        'misfit': float - (s - τ)²
        'continuity': float - μ·d²
        'd2': float - raw squared distance
        'delta_k': int - |k' - k|
        'sharp_gap': float - d² - |k' - k|
        'saturated': bool - True if sharp_gap < tol
    """
    n, k = U_prev.shape
    n_prime, k_prime = U_next.shape

    if N is None:
        N = max(n, n_prime)

    # Stabilize to common ambient
    U_prev_stab = stabilize(U_prev, n, N)
    U_next_stab = stabilize(U_next, n_prime, N)

    # Compute stage function and misfit
    s = s_func(U_next)
    misfit = (s - tau_next) ** 2

    # Compute distance and continuity cost
    d2 = chordal_distance_sq(U_prev_stab, U_next_stab)
    continuity = mu * d2

    # Total action
    J = misfit + continuity

    # Sharp bound info
    delta_k = abs(k_prime - k)
    sharp_gap = d2 - delta_k

    return {
        'J': J,
        'misfit': misfit,
        'continuity': continuity,
        'd2': d2,
        's': s,
        'tau': tau_next,
        'delta_k': delta_k,
        'sharp_gap': sharp_gap,
        'saturated': sharp_gap < 1e-10
    }


def optimal_transition(
    U_prev: np.ndarray,
    candidates: List[np.ndarray],
    s_func: Callable[[np.ndarray], float],
    tau_next: float,
    mu: float,
    N: Optional[int] = None
) -> tuple:
    """
    Find optimal transition among candidates.

    W* = argmin_W J(W | V)

    Parameters
    ----------
    U_prev : ndarray
        Previous state
    candidates : list of ndarray
        Candidate next states
    s_func : callable
        Stage function
    tau_next : float
        Target stage value
    mu : float
        Continuity weight
    N : int, optional
        Ambient dimension

    Returns
    -------
    best_candidate : ndarray
        Optimal next state
    best_result : dict
        Action details for best candidate
    all_results : list
        Action details for all candidates
    """
    if not candidates:
        raise ValueError("No candidates provided")

    all_results = []
    best_J = float('inf')
    best_idx = 0

    for i, U_next in enumerate(candidates):
        result = transition_action(U_prev, U_next, s_func, tau_next, mu, N)
        all_results.append(result)

        if result['J'] < best_J:
            best_J = result['J']
            best_idx = i

    return candidates[best_idx], all_results[best_idx], all_results


def batch_transition_actions(
    U_prev: np.ndarray,
    candidates: List[np.ndarray],
    s_func: Callable[[np.ndarray], float],
    tau_next: float,
    mu: float,
    N: Optional[int] = None
) -> np.ndarray:
    """
    Compute transition actions for a batch of candidates efficiently.

    Parameters
    ----------
    U_prev : ndarray
        Previous state
    candidates : list of ndarray
        Candidate states
    s_func : callable
        Stage function
    tau_next : float
        Target
    mu : float
        Weight
    N : int, optional
        Ambient dimension

    Returns
    -------
    actions : ndarray
        Array of J values for each candidate
    """
    actions = np.zeros(len(candidates))

    for i, U_next in enumerate(candidates):
        result = transition_action(U_prev, U_next, s_func, tau_next, mu, N)
        actions[i] = result['J']

    return actions


def greedy_transition_chain(
    U0: np.ndarray,
    targets: List[tuple],  # List of (k_next, n_next, tau_next)
    s_func: Callable[[np.ndarray], float],
    mu: float,
    n_candidates: int = 20,
    rng: Optional[np.random.Generator] = None
) -> Dict:
    """
    Greedy construction of transition chain.

    Parameters
    ----------
    U0 : ndarray
        Initial state
    targets : list of tuples
        Each tuple: (k_next, n_next, tau_next)
    s_func : callable
        Stage function
    mu : float
        Continuity weight
    n_candidates : int
        Candidates per transition
    rng : Generator, optional
        Random generator

    Returns
    -------
    dict
        'chain': list of states
        'actions': list of action results
        'total_action': float
    """
    from .correspondences import transition_from_to

    if rng is None:
        rng = np.random.default_rng()

    chain = [U0]
    actions = []
    total_action = 0.0

    U = U0
    for k_next, n_next, tau_next in targets:
        # Generate candidates
        candidates = transition_from_to(U, k_next, n_next, n_candidates, rng)

        if not candidates:
            raise ValueError(f"No candidates for transition to ({k_next}, {n_next})")

        # Select optimal
        N = max(U.shape[0], n_next)
        U_best, result, _ = optimal_transition(U, candidates, s_func, tau_next, mu, N)

        chain.append(U_best)
        actions.append(result)
        total_action += result['J']
        U = U_best

    return {
        'chain': chain,
        'actions': actions,
        'total_action': total_action
    }
