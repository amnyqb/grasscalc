"""
GCT seven-manifold chain definition.

The chain is uniquely determined by four theorems:
- Hurwitz (division algebras)
- Takens (embedding)
- Green-Schwarz (anomaly cancellation)
- E₈ (root structure)
"""

from typing import List, Tuple, Dict

# The canonical GCT chain
GCT_CHAIN: List[Tuple[int, int]] = [
    (2, 5),    # Stage 0: Seed (Takens-minimal, D=6)
    (3, 5),    # Stage 1: Complex structure (D=6)
    (3, 7),    # Stage 2: Quaternionic (D=12)
    (3, 16),   # Stage 3: Electroweak — yields sin²θ_W (D=39)
    (7, 18),   # Stage 4: Octonionic bridge (D=77)
    (8, 24),   # Stage 5: E₈ half-spinor (D=128)
    (10, 34),  # Stage 6: E₈ roots (D=240)
]

# Expected dimensions for each manifold
GCT_DIMENSIONS = [6, 6, 12, 39, 77, 128, 240]


def gct_dimension(k: int, n: int) -> int:
    """
    Grassmannian dimension D = k(n-k).

    Parameters
    ----------
    k : int
        Fiber dimension
    n : int
        Ambient dimension

    Returns
    -------
    D : int
        Grassmannian dimension
    """
    return k * (n - k)


def gct_total_dimension(chain: List[Tuple[int, int]] = None) -> int:
    """
    Sum of dimensions for a chain.

    For GCT_CHAIN: returns 508 = 496 + 12.

    Parameters
    ----------
    chain : list of (k, n) tuples, optional
        Chain to sum (default: GCT_CHAIN)

    Returns
    -------
    total : int
        Sum of dimensions
    """
    if chain is None:
        chain = GCT_CHAIN
    return sum(gct_dimension(k, n) for k, n in chain)


def gct_manifolds() -> List[Dict]:
    """
    Get detailed information about each GCT manifold.

    Returns
    -------
    manifolds : list of dict
        Each dict contains: stage, k, n, D, codimension, name
    """
    names = [
        "Seed (Takens-minimal)",
        "Complex structure",
        "Quaternionic",
        "Electroweak (Weinberg)",
        "Octonionic bridge",
        "E₈ half-spinor",
        "E₈ roots"
    ]

    manifolds = []
    for i, (k, n) in enumerate(GCT_CHAIN):
        manifolds.append({
            'stage': i,
            'k': k,
            'n': n,
            'D': gct_dimension(k, n),
            'codimension': n - k,
            'name': names[i],
            'grassmannian': f"Gr({k},{n})"
        })

    return manifolds


def verify_chain_dimensions() -> Dict:
    """
    Verify that GCT chain dimensions match expectations.

    Returns
    -------
    dict
        'correct': bool
        'computed': list
        'expected': list
        'total': int
    """
    computed = [gct_dimension(k, n) for k, n in GCT_CHAIN]
    correct = (computed == GCT_DIMENSIONS)

    return {
        'correct': correct,
        'computed': computed,
        'expected': GCT_DIMENSIONS,
        'total': sum(computed)
    }


def chain_to_string(chain: List[Tuple[int, int]] = None) -> str:
    """
    Convert chain to readable string.

    Parameters
    ----------
    chain : list, optional
        Chain (default: GCT_CHAIN)

    Returns
    -------
    s : str
        Human-readable chain representation
    """
    if chain is None:
        chain = GCT_CHAIN

    parts = [f"Gr({k},{n})" for k, n in chain]
    return " → ".join(parts)


# Key constants
TOTAL_DIMENSION = 508
GAUGE_DIMENSION = 496  # dim(E₈ × E₈)
GRAVITY_DIMENSION = 12
E8_ROOT_DIMENSION = 240
E8_HALFSPINOR_DIMENSION = 128
