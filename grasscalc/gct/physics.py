"""
Physical interpretations and division algebra connections.
"""

from typing import Dict, List

# Division algebras and their dimensions
DIVISION_ALGEBRAS = {
    'R': {'name': 'Real numbers', 'dim': 1, 'symbol': 'ℝ'},
    'C': {'name': 'Complex numbers', 'dim': 2, 'symbol': 'ℂ'},
    'H': {'name': 'Quaternions', 'dim': 4, 'symbol': 'ℍ'},
    'O': {'name': 'Octonions', 'dim': 8, 'symbol': '𝕆'},
}


def hurwitz_dimensions() -> List[int]:
    """
    Return Hurwitz-allowed fiber dimensions.

    From Hurwitz theorem: k ∈ {1, 2, 3, 4, 7, 8} from division algebras,
    plus k=10 (superstring critical dimension = 8+2).

    For GCT: k ∈ {2, 3, 7, 8, 10}

    Returns
    -------
    list of int
        Allowed k values
    """
    return [2, 3, 7, 8, 10]


def division_algebra_map() -> Dict:
    """
    Map GCT fiber dimensions to division algebra structures.

    Returns
    -------
    dict
        k → division algebra interpretation
    """
    return {
        2: {
            'algebra': 'C',
            'description': 'dim(C) = 2',
            'physical': 'Complex structure'
        },
        3: {
            'algebra': 'Im(H)',
            'description': 'dim(Im(H)) = 3 (quaternion imaginaries)',
            'physical': 'Electroweak fiber'
        },
        7: {
            'algebra': 'Im(O)',
            'description': 'dim(Im(O)) = 7 (octonion imaginaries)',
            'physical': 'Octonionic bridge'
        },
        8: {
            'algebra': 'O',
            'description': 'dim(O) = 8',
            'physical': 'E₈ half-spinor connection'
        },
        10: {
            'algebra': 'O + C',
            'description': 'dim(O) + dim(C) = 8 + 2 = 10',
            'physical': 'Superstring critical dimension'
        }
    }


def takens_minimal(k: int) -> int:
    """
    Minimal ambient dimension from Takens embedding theorem.

    n ≥ 2k + 1 for dynamical reconstruction.

    Parameters
    ----------
    k : int
        Fiber dimension

    Returns
    -------
    n_min : int
        Minimal ambient dimension
    """
    return 2 * k + 1


def green_schwarz_constraint() -> Dict:
    """
    Green-Schwarz anomaly cancellation constraint.

    Total dimension must equal 508 = 496 + 12 for anomaly-free theory.

    Returns
    -------
    dict
        Constraint details
    """
    return {
        'total': 508,
        'gauge': 496,
        'gravity': 12,
        'gauge_group': 'E₈ × E₈ (or SO(32))',
        'explanation': 'Anomaly cancellation in D=10 superstring theory'
    }


def e8_structure() -> Dict:
    """
    E₈ Lie algebra structure.

    Returns
    -------
    dict
        E₈ properties
    """
    return {
        'rank': 8,
        'dimension': 248,
        'roots': 240,
        'half_spinor': 128,
        'adjoint': 248,
        'simple': True,
        'exceptional': True
    }


def gct_physics_interpretation() -> Dict:
    """
    Physical interpretation of GCT manifold chain.

    Returns
    -------
    dict
        Stage → physical interpretation
    """
    return {
        0: {
            'manifold': 'Gr(2,5)',
            'dimension': 6,
            'physics': 'Seed manifold, Takens-minimal complex structure',
            'role': 'Starting point for dimensional evolution'
        },
        1: {
            'manifold': 'Gr(3,5)',
            'dimension': 6,
            'physics': 'Grassmannian dual of seed',
            'role': 'Complex structure preservation'
        },
        2: {
            'manifold': 'Gr(3,7)',
            'dimension': 12,
            'physics': 'Quaternionic structure emergence',
            'role': 'SU(2) gauge structure'
        },
        3: {
            'manifold': 'Gr(3,16)',
            'dimension': 39,
            'physics': 'Electroweak unification scale',
            'role': 'Yields sin²θ_W = 3/13'
        },
        4: {
            'manifold': 'Gr(7,18)',
            'dimension': 77,
            'physics': 'Octonionic bridge',
            'role': 'Connects electroweak to E₈'
        },
        5: {
            'manifold': 'Gr(8,24)',
            'dimension': 128,
            'physics': 'E₈ half-spinor representation',
            'role': 'Chiral fermion structure'
        },
        6: {
            'manifold': 'Gr(10,34)',
            'dimension': 240,
            'physics': 'E₈ root system',
            'role': 'Full gauge content, superstring dimension'
        }
    }


def print_physics_summary():
    """Print physics interpretation summary."""
    print("GCT Physical Interpretation")
    print("=" * 70)

    interp = gct_physics_interpretation()
    for stage, info in interp.items():
        print(f"\nStage {stage}: {info['manifold']} (D={info['dimension']})")
        print(f"  Physics: {info['physics']}")
        print(f"  Role: {info['role']}")

    print("\n" + "=" * 70)
    gs = green_schwarz_constraint()
    print(f"Green-Schwarz: {gs['total']} = {gs['gauge']} + {gs['gravity']}")
    print(f"  Gauge: {gs['gauge_group']}")
