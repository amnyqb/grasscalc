"""
Transition operators for between-manifold calculus.

Implements min-plus (Bellman) operators and argmin transitions.
"""

import numpy as np
from typing import Callable, Dict, List, Optional, Tuple

from .transition_action import transition_action


def minplus_operator(
    V_prev: np.ndarray,
    candidates: List[np.ndarray],
    cost_fn: Callable[[np.ndarray, np.ndarray], float],
    f: Optional[Callable[[np.ndarray], float]] = None
) -> float:
    """
    Min-plus (Bellman) operator on observables.

    (T f)(V) = min_W [c(V,W) + f(W)]

    Parameters
    ----------
    V_prev : ndarray
        Current state
    candidates : list of ndarray
        Candidate next states
    cost_fn : callable
        Cost function c(V, W) → R
    f : callable, optional
        Observable function. If None, uses f = 0.

    Returns
    -------
    value : float
        (T f)(V)
    """
    if not candidates:
        return float('inf')

    values = []
    for W in candidates:
        c = cost_fn(V_prev, W)
        f_W = f(W) if f is not None else 0.0
        values.append(c + f_W)

    return min(values)


def argmin_transition(
    V_prev: np.ndarray,
    candidates: List[np.ndarray],
    cost_fn: Callable[[np.ndarray, np.ndarray], float]
) -> Tuple[np.ndarray, Dict]:
    """
    Deterministic argmin transition on states.

    W* = argmin_W c(V, W)

    Parameters
    ----------
    V_prev : ndarray
        Current state
    candidates : list of ndarray
        Candidate next states
    cost_fn : callable
        Cost function c(V, W) → R

    Returns
    -------
    W_opt : ndarray
        Optimal next state
    info : dict
        'cost': optimal cost
        'index': index of optimal candidate
        'all_costs': list of all costs
    """
    if not candidates:
        raise ValueError("No candidates provided")

    costs = [cost_fn(V_prev, W) for W in candidates]
    idx = int(np.argmin(costs))

    return candidates[idx], {
        'cost': costs[idx],
        'index': idx,
        'all_costs': costs
    }


def bellman_iteration(
    states: List[np.ndarray],
    transition_graph: Dict[int, List[int]],
    cost_matrix: np.ndarray,
    f0: np.ndarray,
    n_iter: int = 100
) -> np.ndarray:
    """
    Value iteration for Bellman equation on finite state space.

    f_{k+1}(i) = min_j [c(i,j) + f_k(j)]

    Parameters
    ----------
    states : list of ndarray
        State space
    transition_graph : dict
        i -> list of reachable j indices
    cost_matrix : ndarray, shape (n_states, n_states)
        c[i,j] = cost from i to j (inf if not connected)
    f0 : ndarray, shape (n_states,)
        Initial value function
    n_iter : int
        Number of iterations

    Returns
    -------
    f : ndarray
        Converged value function
    """
    n = len(states)
    f = f0.copy()

    for _ in range(n_iter):
        f_new = np.zeros(n)
        for i in range(n):
            successors = transition_graph.get(i, [])
            if successors:
                values = [cost_matrix[i, j] + f[j] for j in successors]
                f_new[i] = min(values)
            else:
                f_new[i] = f[i]

        if np.allclose(f, f_new):
            break
        f = f_new

    return f


def policy_from_value(
    states: List[np.ndarray],
    transition_graph: Dict[int, List[int]],
    cost_matrix: np.ndarray,
    value_fn: np.ndarray
) -> Dict[int, int]:
    """
    Extract greedy policy from value function.

    π(i) = argmin_j [c(i,j) + V(j)]

    Parameters
    ----------
    states : list
        State space
    transition_graph : dict
        Connectivity
    cost_matrix : ndarray
        Costs
    value_fn : ndarray
        Value function

    Returns
    -------
    policy : dict
        i -> j mapping
    """
    n = len(states)
    policy = {}

    for i in range(n):
        successors = transition_graph.get(i, [])
        if successors:
            values = [(cost_matrix[i, j] + value_fn[j], j) for j in successors]
            _, best_j = min(values)
            policy[i] = best_j

    return policy


def compose_operators(
    operators: List[Callable],
    initial_value: float = 0.0
) -> Callable:
    """
    Compose a sequence of transition operators.

    (T_n ∘ ... ∘ T_1)(f)(V) = T_n(...T_1(f)...)(V)

    Parameters
    ----------
    operators : list of callable
        Operators T_i
    initial_value : float
        Initial value for terminal states

    Returns
    -------
    composed : callable
        Composed operator
    """
    def composed(f):
        result = f
        for T in reversed(operators):
            result = lambda V, r=result, op=T: op(V, r)
        return result

    return composed
