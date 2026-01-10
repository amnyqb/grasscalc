"""Tests for grasscalc.core module."""

import numpy as np
import pytest
from numpy.testing import assert_allclose


class TestLinalg:
    """Tests for linear algebra utilities."""

    def test_qr_retraction(self):
        from grasscalc.core.linalg import qr_retraction, is_orthonormal

        n, k = 10, 3
        rng = np.random.default_rng(42)
        U = np.linalg.qr(rng.standard_normal((n, k)))[0]
        Xi = rng.standard_normal((n, k))
        Xi = Xi - U @ (U.T @ Xi)  # Project to tangent

        U_new = qr_retraction(U, 0.1 * Xi)
        assert U_new.shape == (n, k)
        assert is_orthonormal(U_new)

    def test_stable_qr(self):
        from grasscalc.core.linalg import stable_qr

        rng = np.random.default_rng(42)
        A = rng.standard_normal((10, 3))
        Q, R = stable_qr(A)

        assert_allclose(Q @ R, A, atol=1e-10)
        assert_allclose(Q.T @ Q, np.eye(3), atol=1e-10)
        assert np.all(np.diag(R) >= 0)  # Positive diagonal


class TestDistances:
    """Tests for distance functions."""

    def test_chordal_distance_self(self):
        from grasscalc.core.distances import chordal_distance_sq
        from grasscalc.core.random import sample_grassmann

        rng = np.random.default_rng(42)
        U = sample_grassmann(3, 7, rng)

        d2 = chordal_distance_sq(U, U)
        assert_allclose(d2, 0.0, atol=1e-10)

    def test_chordal_distance_symmetry(self):
        from grasscalc.core.distances import chordal_distance_sq
        from grasscalc.core.random import sample_grassmann

        rng = np.random.default_rng(42)
        U = sample_grassmann(3, 7, rng)
        V = sample_grassmann(3, 7, rng)

        d_UV = chordal_distance_sq(U, V)
        d_VU = chordal_distance_sq(V, U)
        assert_allclose(d_UV, d_VU, atol=1e-10)

    def test_principal_angles_range(self):
        from grasscalc.core.distances import principal_angles
        from grasscalc.core.random import sample_grassmann

        rng = np.random.default_rng(42)
        U = sample_grassmann(3, 7, rng)
        V = sample_grassmann(3, 7, rng)

        theta = principal_angles(U, V)
        assert len(theta) == 3
        assert np.all(theta >= 0)
        assert np.all(theta <= np.pi / 2)


class TestTangent:
    """Tests for tangent space operations."""

    def test_tangent_projection(self):
        from grasscalc.core.tangent import tangent_project, is_tangent
        from grasscalc.core.random import sample_grassmann

        rng = np.random.default_rng(42)
        U = sample_grassmann(3, 7, rng)
        A = rng.standard_normal((7, 3))

        Xi = tangent_project(U, A)
        assert is_tangent(U, Xi)

    def test_tangent_orthogonality(self):
        from grasscalc.core.tangent import tangent_project
        from grasscalc.core.random import sample_grassmann

        rng = np.random.default_rng(42)
        U = sample_grassmann(3, 7, rng)
        A = rng.standard_normal((7, 3))

        Xi = tangent_project(U, A)
        assert_allclose(U.T @ Xi, 0.0, atol=1e-10)


class TestSharpBound:
    """Tests for Sharp Bound Theorem."""

    def test_sharp_bound_inequality(self):
        """d² ≥ |k - k'| for random pairs."""
        from grasscalc.core.random import sample_grassmann
        from grasscalc.core.distances import chordal_distance_sq
        from grasscalc.core.representations import stabilize

        rng = np.random.default_rng(42)

        for _ in range(100):
            k1 = rng.integers(2, 6)
            n1 = rng.integers(k1 + 1, k1 + 10)
            k2 = rng.integers(2, 6)
            n2 = rng.integers(k2 + 1, k2 + 10)

            U = sample_grassmann(k1, n1, rng)
            V = sample_grassmann(k2, n2, rng)

            N = max(n1, n2)
            U_stab = stabilize(U, n1, N)
            V_stab = stabilize(V, n2, N)

            d2 = chordal_distance_sq(U_stab, V_stab)
            delta_k = abs(k1 - k2)

            assert d2 >= delta_k - 1e-10, f"Sharp bound violated: d²={d2}, |Δk|={delta_k}"

    def test_sharp_bound_saturation(self):
        """Containment should saturate the bound."""
        from grasscalc.core.random import sample_grassmann
        from grasscalc.layer2.sharp_bound import sharp_bound_check, find_optimal_successor

        rng = np.random.default_rng(42)
        U = sample_grassmann(3, 10, rng)

        # Find V ⊃ U with k=5
        V = find_optimal_successor(U, k_next=5, n_next=10)

        result = sharp_bound_check(U, V, N=10)
        assert result['saturated'], f"Expected saturation, gap={result['gap']}"
        assert_allclose(result['d2'], 2.0, atol=1e-8)  # |5-3| = 2


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
