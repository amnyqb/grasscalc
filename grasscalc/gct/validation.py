"""
GCT validation tests.
"""

from typing import Dict, List
from .chain import GCT_CHAIN, gct_dimension, gct_total_dimension
from .weinberg import weinberg_angle, weinberg_angle_experimental
from .transitions import gct_transition_operators, verify_transitions


def verify_gct_dimensions() -> Dict:
    """
    Verify 508 = 496 + 12 decomposition.

    Returns
    -------
    dict
        'total': int (should be 508)
        'gauge': int (496 = dim(E₈ × E₈))
        'gravity': int (12)
        'verified': bool
    """
    total = gct_total_dimension(GCT_CHAIN)
    gauge = 496  # dim(E₈ × E₈)
    gravity = 12

    return {
        'total': total,
        'gauge': gauge,
        'gravity': gravity,
        'sum_check': gauge + gravity,
        'verified': total == 508 and gauge + gravity == 508
    }


def verify_individual_dimensions() -> Dict:
    """
    Verify each manifold's dimension.

    Returns
    -------
    dict with verification results
    """
    expected = [6, 6, 12, 39, 77, 128, 240]
    computed = [gct_dimension(k, n) for k, n in GCT_CHAIN]

    results = []
    for i, ((k, n), exp, comp) in enumerate(zip(GCT_CHAIN, expected, computed)):
        results.append({
            'stage': i,
            'manifold': f'Gr({k},{n})',
            'expected': exp,
            'computed': comp,
            'match': exp == comp
        })

    return {
        'all_match': all(r['match'] for r in results),
        'results': results
    }


def verify_weinberg() -> Dict:
    """
    Verify Weinberg angle prediction.

    Returns
    -------
    dict with Weinberg angle verification
    """
    predicted = weinberg_angle(3, 16)
    exp = weinberg_angle_experimental()

    error_percent = abs(predicted - exp['value']) / exp['value'] * 100

    return {
        'predicted': predicted,
        'predicted_exact': '3/13',
        'experimental': exp['value'],
        'error_percent': error_percent,
        'within_1_percent': error_percent < 1.0
    }


def verify_e8_dimensions() -> Dict:
    """
    Verify E₈-related dimensions.

    Returns
    -------
    dict with E₈ verification
    """
    # Stage 6: Gr(10,34) should have D = 240 (E₈ roots)
    k6, n6 = GCT_CHAIN[6]
    D6 = gct_dimension(k6, n6)

    # Stage 5: Gr(8,24) should have D = 128 (E₈ half-spinor)
    k5, n5 = GCT_CHAIN[5]
    D5 = gct_dimension(k5, n5)

    return {
        'e8_roots': {
            'manifold': f'Gr({k6},{n6})',
            'dimension': D6,
            'expected': 240,
            'verified': D6 == 240
        },
        'e8_halfspinor': {
            'manifold': f'Gr({k5},{n5})',
            'dimension': D5,
            'expected': 128,
            'verified': D5 == 128
        }
    }


def verify_gct_chain() -> Dict:
    """
    Comprehensive GCT chain verification.

    Returns
    -------
    dict with all verification results
    """
    return {
        'dimensions': verify_gct_dimensions(),
        'individual': verify_individual_dimensions(),
        'weinberg': verify_weinberg(),
        'e8': verify_e8_dimensions(),
        'transitions': verify_transitions()
    }


def run_gct_tests() -> bool:
    """
    Run all GCT tests and return pass/fail.

    Returns
    -------
    bool
        True if all tests pass
    """
    results = verify_gct_chain()

    tests_passed = (
        results['dimensions']['verified'] and
        results['individual']['all_match'] and
        results['weinberg']['within_1_percent'] and
        results['e8']['e8_roots']['verified'] and
        results['e8']['e8_halfspinor']['verified'] and
        results['transitions']['valid']
    )

    return tests_passed


def print_verification_report():
    """Print formatted verification report."""
    results = verify_gct_chain()

    print("GCT Verification Report")
    print("=" * 60)

    # Dimensions
    dim = results['dimensions']
    print(f"\n1. Total Dimension: {dim['total']} = {dim['gauge']} + {dim['gravity']}")
    print(f"   Verified: {'✓' if dim['verified'] else '✗'}")

    # Individual dimensions
    ind = results['individual']
    print(f"\n2. Individual Dimensions: {'All match ✓' if ind['all_match'] else 'Mismatch ✗'}")
    for r in ind['results']:
        status = '✓' if r['match'] else '✗'
        print(f"   Stage {r['stage']}: {r['manifold']} → D={r['computed']} {status}")

    # Weinberg
    w = results['weinberg']
    print(f"\n3. Weinberg Angle: sin²θ_W = {w['predicted_exact']} = {w['predicted']:.6f}")
    print(f"   Experimental: {w['experimental']}")
    print(f"   Error: {w['error_percent']:.2f}%")
    print(f"   Within 1%: {'✓' if w['within_1_percent'] else '✗'}")

    # E8
    e8 = results['e8']
    print(f"\n4. E₈ Dimensions:")
    print(f"   Roots (240): {'✓' if e8['e8_roots']['verified'] else '✗'}")
    print(f"   Half-spinor (128): {'✓' if e8['e8_halfspinor']['verified'] else '✗'}")

    # Transitions
    trans = results['transitions']
    print(f"\n5. Transitions: {'Valid ✓' if trans['valid'] else 'Invalid ✗'}")

    # Overall
    passed = run_gct_tests()
    print(f"\n{'='*60}")
    print(f"Overall: {'ALL TESTS PASSED ✓' if passed else 'SOME TESTS FAILED ✗'}")
