"""
GCT transition operators T0-T5.

Each transition is derived from established mathematics:
- T0: Grassmannian duality
- T1: Takens embedding
- T2: Endomorphism completeness
- T3: Division algebra ladder
- T4: Minimal Seed theorem
- T5: E₈ closure + Green-Schwarz
"""

from typing import Dict, List
from dataclasses import dataclass


@dataclass
class TransitionOperator:
    """A GCT transition operator."""
    name: str
    source: tuple  # (k, n)
    target: tuple  # (k', n')
    delta_k: int
    delta_n: int
    formula: str
    derivation_source: str
    status: str = "Derived"


# Define the six transition operators
T0 = TransitionOperator(
    name="T0",
    source=(2, 5),
    target=(3, 5),
    delta_k=1,
    delta_n=0,
    formula="Δn = 0",
    derivation_source="Grassmannian duality: Gr(k,n) ≅ Gr(n-k,n)"
)

T1 = TransitionOperator(
    name="T1",
    source=(3, 5),
    target=(3, 7),
    delta_k=0,
    delta_n=2,
    formula="Δn = 2Δk (with Δk=1 from T0)",
    derivation_source="Takens embedding theorem: n ≥ 2k+1"
)

T2 = TransitionOperator(
    name="T2",
    source=(3, 7),
    target=(3, 16),
    delta_k=0,
    delta_n=9,
    formula="Δn = k² = 9",
    derivation_source="Endomorphism Completeness: dim(End(Im(H))) = 9"
)

T3 = TransitionOperator(
    name="T3",
    source=(3, 16),
    target=(7, 18),
    delta_k=4,
    delta_n=2,
    formula="Δk = dim(H) = 4, Δn = dim(C) = 2",
    derivation_source="Division algebra ladder"
)

T4 = TransitionOperator(
    name="T4",
    source=(7, 18),
    target=(8, 24),
    delta_k=1,
    delta_n=6,
    formula="Δn = D₁ = 6",
    derivation_source="Minimal Seed theorem: D₁ = dim(Gr(2,5)) = 6"
)

T5 = TransitionOperator(
    name="T5",
    source=(8, 24),
    target=(10, 34),
    delta_k=2,
    delta_n=10,
    formula="Δn = Δk + dim(O) = 2 + 8 = 10",
    derivation_source="E₈ closure + Green-Schwarz anomaly cancellation"
)


def gct_transition_operators() -> List[TransitionOperator]:
    """
    Return all GCT transition operators.

    Returns
    -------
    operators : list of TransitionOperator
        T0 through T5
    """
    return [T0, T1, T2, T3, T4, T5]


def transition_table() -> List[Dict]:
    """
    Return transition operators as table data.

    Returns
    -------
    table : list of dict
        Each dict represents one row of the transition table
    """
    operators = gct_transition_operators()
    return [
        {
            'T': op.name,
            'transition': f"Gr{op.source} → Gr{op.target}",
            'delta_k': op.delta_k,
            'delta_n': op.delta_n,
            'formula': op.formula,
            'derivation_source': op.derivation_source,
            'status': op.status
        }
        for op in operators
    ]


def verify_transitions() -> Dict:
    """
    Verify that transitions connect correctly.

    Returns
    -------
    dict
        'valid': bool
        'chain_from_transitions': list of (k,n)
        'errors': list
    """
    from .chain import GCT_CHAIN

    operators = gct_transition_operators()
    errors = []

    # Build chain from transitions
    chain = [operators[0].source]  # Start with T0 source
    for op in operators:
        if chain[-1] != op.source:
            errors.append(f"{op.name}: Expected source {chain[-1]}, got {op.source}")
        chain.append(op.target)

    # Compare with GCT_CHAIN
    if chain != GCT_CHAIN:
        errors.append(f"Chain mismatch: {chain} vs {GCT_CHAIN}")

    # Verify deltas
    for op in operators:
        k_s, n_s = op.source
        k_t, n_t = op.target
        if k_t - k_s != op.delta_k:
            errors.append(f"{op.name}: Δk mismatch")
        if n_t - n_s != op.delta_n:
            errors.append(f"{op.name}: Δn mismatch")

    return {
        'valid': len(errors) == 0,
        'chain_from_transitions': chain,
        'errors': errors
    }


def print_transition_table():
    """Print formatted transition table."""
    table = transition_table()
    print("GCT Transition Operators (All Derived)")
    print("=" * 80)
    print(f"{'T':<4} {'Transition':<25} {'Δk':<4} {'Δn':<4} {'Formula':<20} {'Source'}")
    print("-" * 80)
    for row in table:
        print(f"{row['T']:<4} {row['transition']:<25} {row['delta_k']:<4} {row['delta_n']:<4} "
              f"{row['formula']:<20} {row['derivation_source'][:30]}")
