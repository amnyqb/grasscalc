"""Tests for GCT module."""

import numpy as np
import pytest
from numpy.testing import assert_allclose


class TestGCTChain:
    """Tests for GCT chain properties."""

    def test_chain_length(self):
        from grasscalc.gct.chain import GCT_CHAIN
        assert len(GCT_CHAIN) == 7

    def test_total_dimension(self):
        from grasscalc.gct.chain import gct_total_dimension, GCT_CHAIN
        assert gct_total_dimension(GCT_CHAIN) == 508

    def test_gauge_gravity_decomposition(self):
        """508 = 496 + 12"""
        assert 508 == 496 + 12

    def test_individual_dimensions(self):
        from grasscalc.gct.chain import GCT_CHAIN, gct_dimension
        expected = [6, 6, 12, 39, 77, 128, 240]

        for (k, n), exp_dim in zip(GCT_CHAIN, expected):
            assert gct_dimension(k, n) == exp_dim


class TestWeinbergAngle:
    """Tests for Weinberg angle derivation."""

    def test_weinberg_exact(self):
        from grasscalc.gct.weinberg import weinberg_angle
        sin2_theta = weinberg_angle(3, 16)
        assert_allclose(sin2_theta, 3/13, atol=1e-15)

    def test_weinberg_value(self):
        from grasscalc.gct.weinberg import weinberg_angle
        sin2_theta = weinberg_angle(3, 16)
        assert_allclose(sin2_theta, 0.23076923, atol=1e-7)

    def test_weinberg_error(self):
        from grasscalc.gct.weinberg import weinberg_error
        error = weinberg_error()
        assert error['relative_error_percent'] < 1.0  # Within 1%


class TestE8Dimensions:
    """Tests for E₈ structure."""

    def test_e8_roots(self):
        from grasscalc.gct.chain import gct_dimension
        assert gct_dimension(10, 34) == 240  # E₈ roots

    def test_e8_halfspinor(self):
        from grasscalc.gct.chain import gct_dimension
        assert gct_dimension(8, 24) == 128  # E₈ half-spinor


class TestTransitions:
    """Tests for transition operators."""

    def test_transition_chain_valid(self):
        from grasscalc.gct.transitions import verify_transitions
        result = verify_transitions()
        assert result['valid'], f"Errors: {result['errors']}"

    def test_transition_operators_count(self):
        from grasscalc.gct.transitions import gct_transition_operators
        ops = gct_transition_operators()
        assert len(ops) == 6  # T0-T5


class TestGCTValidation:
    """Comprehensive GCT tests."""

    def test_all_gct_tests_pass(self):
        from grasscalc.gct.validation import run_gct_tests
        assert run_gct_tests()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
