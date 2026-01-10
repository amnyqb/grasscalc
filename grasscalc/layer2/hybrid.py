"""
Hybrid evolution combining within-stage flows and between-stage transitions.
"""

import numpy as np
from typing import Callable, Dict, List, Optional, Tuple
from dataclasses import dataclass, field

from ..core.representations import GrassmannPoint
from ..layer1.flows import run_gradient_flow, FlowResult
from .transition_action import optimal_transition
from .correspondences import transition_from_to


@dataclass
class HybridState:
    """State in hybrid evolution."""
    point: np.ndarray
    stage: int
    k: int
    n: int
    energy: float = 0.0
    metadata: Dict = field(default_factory=dict)


@dataclass
class HybridResult:
    """Result of hybrid chain evolution."""
    states: List[HybridState]
    transitions: List[Dict]
    flow_results: List[Optional[FlowResult]]
    total_action: float
    converged: bool


def run_hybrid_chain(
    chain_spec: List[Tuple[int, int]],  # [(k, n), ...]
    U0: Optional[np.ndarray] = None,
    objective: Optional[Callable] = None,
    transition_cost: Optional[Callable] = None,
    mu: float = 1.0,
    flow_steps: int = 100,
    n_candidates: int = 20,
    rng: Optional[np.random.Generator] = None
) -> HybridResult:
    """
    Run hybrid evolution: alternating flows and transitions.

    H_i = U_φ^T ∘ T_{i-1→i}

    Parameters
    ----------
    chain_spec : list of (k, n) tuples
        Grassmannian chain specification
    U0 : ndarray, optional
        Initial point (sampled if not provided)
    objective : callable, optional
        Within-stage objective (default: constant)
    transition_cost : callable, optional
        Between-stage cost (default: squared distance)
    mu : float
        Transition continuity weight
    flow_steps : int
        Steps per within-stage flow
    n_candidates : int
        Candidates per transition
    rng : Generator, optional
        Random generator

    Returns
    -------
    HybridResult
        Evolution results
    """
    from ..core.random import sample_grassmann

    if rng is None:
        rng = np.random.default_rng()

    if not chain_spec:
        raise ValueError("Empty chain specification")

    # Initialize
    k0, n0 = chain_spec[0]
    if U0 is None:
        U0 = sample_grassmann(k0, n0, rng)

    # Default functions
    if objective is None:
        objective = lambda U: 0.0

    if transition_cost is None:
        from ..core.distances import chordal_distance_sq
        transition_cost = chordal_distance_sq

    # Stage function: codimension
    def s_func(U):
        return U.shape[0] - U.shape[1]

    states = [HybridState(U0, 0, k0, n0)]
    transitions = []
    flow_results = []
    total_action = 0.0

    U = U0
    for i in range(1, len(chain_spec)):
        k_prev, n_prev = chain_spec[i-1]
        k_next, n_next = chain_spec[i]

        # Within-stage flow (optional)
        if flow_steps > 0:
            try:
                flow_result = run_gradient_flow(
                    U, objective, max_steps=flow_steps, tol=1e-8
                )
                U = flow_result.final_point
                flow_results.append(flow_result)
            except:
                flow_results.append(None)
        else:
            flow_results.append(None)

        # Between-stage transition
        candidates = transition_from_to(U, k_next, n_next, n_candidates, rng)

        if candidates:
            tau = n_next - k_next  # Target codimension
            N = max(n_prev, n_next)

            U_best, trans_result, _ = optimal_transition(
                U, candidates, s_func, tau, mu, N
            )

            transitions.append(trans_result)
            total_action += trans_result['J']
            U = U_best
        else:
            transitions.append({'error': 'no candidates'})

        states.append(HybridState(U, i, k_next, n_next))

    return HybridResult(
        states=states,
        transitions=transitions,
        flow_results=flow_results,
        total_action=total_action,
        converged=True
    )


def hybrid_operator(
    flow_operator: Callable,
    transition_operator: Callable,
    flow_time: float = 1.0
) -> Callable:
    """
    Construct hybrid operator H = U_φ^T ∘ T.

    Parameters
    ----------
    flow_operator : callable
        Within-stage flow U_φ^t
    transition_operator : callable
        Between-stage transition T
    flow_time : float
        Flow duration

    Returns
    -------
    H : callable
        Hybrid operator
    """
    def H(U):
        # First apply flow
        U_flowed = flow_operator(U, flow_time)
        # Then apply transition
        U_transitioned = transition_operator(U_flowed)
        return U_transitioned

    return H


def chain_composition(
    operators: List[Callable]
) -> Callable:
    """
    Compose a sequence of hybrid operators.

    Parameters
    ----------
    operators : list of callable
        H_1, H_2, ..., H_n

    Returns
    -------
    H_total : callable
        H_n ∘ ... ∘ H_1
    """
    def H_total(U):
        for H in operators:
            U = H(U)
        return U

    return H_total
