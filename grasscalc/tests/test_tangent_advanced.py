"""Advanced tests for tangent space operations including exp/log maps."""

import numpy as np
import pytest
from numpy.testing import assert_allclose
from numpy.linalg import norm


class TestExponentialMap:
    """Tests for exponential map."""

    def test_exp_at_zero(self):
        """Exp of zero tangent should return base point."""
        from grasscalc.core.random import sample_grassmann
        from grasscalc.core.tangent import exponential_map

        rng = np.random.default_rng(42)
        U = sample_grassmann(3, 7, rng)
        Xi = np.zeros((7, 3))

        V = exponential_map(U, Xi)
        assert_allclose(U @ U.T, V @ V.T, atol=1e-14)

    def test_exp_small_tangent(self):
        """Exp of small tangent should be close to base."""
        from grasscalc.core.random import sample_grassmann
        from grasscalc.core.tangent import exponential_map, tangent_project
        from grasscalc.core.distances import geodesic_distance

        rng = np.random.default_rng(42)
        U = sample_grassmann(3, 7, rng)
        Xi = tangent_project(U, rng.standard_normal((7, 3)))
        Xi = Xi / norm(Xi, 'fro') * 0.001  # Very small

        V = exponential_map(U, Xi)
        d = geodesic_distance(U, V)
        assert d < 0.01

    def test_exp_preserves_orthonormality(self):
        """Result of exp should be orthonormal."""
        from grasscalc.core.random import sample_grassmann
        from grasscalc.core.tangent import exponential_map, tangent_project

        rng = np.random.default_rng(42)
        for _ in range(10):
            U = sample_grassmann(3, 7, rng)
            Xi = tangent_project(U, rng.standard_normal((7, 3)))
            Xi = Xi / norm(Xi, 'fro') * rng.uniform(0.1, 2.0)

            V = exponential_map(U, Xi)
            assert_allclose(V.T @ V, np.eye(3), atol=1e-12)

    @pytest.mark.parametrize("k,n", [(2, 5), (3, 7), (4, 10), (5, 12)])
    def test_exp_various_dimensions(self, k, n):
        """Test exp map across different dimensions."""
        from grasscalc.core.random import sample_grassmann
        from grasscalc.core.tangent import exponential_map, tangent_project

        rng = np.random.default_rng(42)
        U = sample_grassmann(k, n, rng)
        Xi = tangent_project(U, rng.standard_normal((n, k)))

        V = exponential_map(U, Xi)
        assert V.shape == (n, k)
        assert_allclose(V.T @ V, np.eye(k), atol=1e-12)


class TestLogarithmMap:
    """Tests for logarithm map."""

    def test_log_same_point(self):
        """Log from U to U should be zero."""
        from grasscalc.core.random import sample_grassmann
        from grasscalc.core.tangent import logarithm_map

        rng = np.random.default_rng(42)
        U = sample_grassmann(3, 7, rng)

        Xi = logarithm_map(U, U)
        assert_allclose(Xi, 0.0, atol=1e-12)

    def test_log_is_tangent(self):
        """Log should produce a tangent vector."""
        from grasscalc.core.random import sample_grassmann
        from grasscalc.core.tangent import logarithm_map, is_tangent

        rng = np.random.default_rng(42)
        U = sample_grassmann(3, 7, rng)
        V = sample_grassmann(3, 7, rng)

        Xi = logarithm_map(U, V)
        assert is_tangent(U, Xi)

    def test_log_norm_equals_distance(self):
        """||log(U, V)||_F should equal geodesic distance."""
        from grasscalc.core.random import sample_grassmann
        from grasscalc.core.tangent import logarithm_map
        from grasscalc.core.distances import geodesic_distance

        rng = np.random.default_rng(42)
        for _ in range(20):
            U = sample_grassmann(3, 7, rng)
            V = sample_grassmann(3, 7, rng)

            Xi = logarithm_map(U, V)
            d = geodesic_distance(U, V)
            assert_allclose(norm(Xi, 'fro'), d, atol=1e-12)


class TestExpLogRoundtrip:
    """Tests for exp/log roundtrip consistency."""

    def test_log_then_exp(self):
        """Exp(Log(U, V)) should recover V."""
        from grasscalc.core.random import sample_grassmann
        from grasscalc.core.tangent import exponential_map, logarithm_map

        rng = np.random.default_rng(42)
        for _ in range(20):
            U = sample_grassmann(3, 7, rng)
            V = sample_grassmann(3, 7, rng)

            Xi = logarithm_map(U, V)
            V_recovered = exponential_map(U, Xi)

            # Compare projectors
            P_V = V @ V.T
            P_recovered = V_recovered @ V_recovered.T
            assert_allclose(P_V, P_recovered, atol=1e-12)

    def test_exp_then_log(self):
        """Log(U, Exp(U, Xi)) should recover Xi."""
        from grasscalc.core.random import sample_grassmann
        from grasscalc.core.tangent import exponential_map, logarithm_map, tangent_project

        rng = np.random.default_rng(42)
        for _ in range(20):
            U = sample_grassmann(3, 7, rng)
            Xi = tangent_project(U, rng.standard_normal((7, 3)))
            Xi = Xi / norm(Xi, 'fro') * rng.uniform(0.1, 1.5)

            V = exponential_map(U, Xi)
            Xi_recovered = logarithm_map(U, V)

            assert_allclose(Xi, Xi_recovered, atol=1e-12)


class TestGeodesic:
    """Tests for geodesic interpolation."""

    def test_geodesic_endpoints(self):
        """Geodesic at t=0 and t=1 should be U and V."""
        from grasscalc.core.random import sample_grassmann
        from grasscalc.core.tangent import geodesic

        rng = np.random.default_rng(42)
        U = sample_grassmann(3, 7, rng)
        V = sample_grassmann(3, 7, rng)

        W0 = geodesic(U, V, 0.0)
        W1 = geodesic(U, V, 1.0)

        assert_allclose(U @ U.T, W0 @ W0.T, atol=1e-12)
        assert_allclose(V @ V.T, W1 @ W1.T, atol=1e-12)

    def test_geodesic_midpoint(self):
        """Midpoint should be equidistant from endpoints."""
        from grasscalc.core.random import sample_grassmann
        from grasscalc.core.tangent import geodesic
        from grasscalc.core.distances import geodesic_distance

        rng = np.random.default_rng(42)
        for _ in range(10):
            U = sample_grassmann(3, 7, rng)
            V = sample_grassmann(3, 7, rng)

            W = geodesic(U, V, 0.5)
            d_UV = geodesic_distance(U, V)
            d_UW = geodesic_distance(U, W)
            d_WV = geodesic_distance(W, V)

            assert_allclose(d_UW, d_UV / 2, atol=1e-10)
            assert_allclose(d_WV, d_UV / 2, atol=1e-10)

    def test_geodesic_quarter_points(self):
        """Test geodesic at t=0.25, 0.5, 0.75."""
        from grasscalc.core.random import sample_grassmann
        from grasscalc.core.tangent import geodesic
        from grasscalc.core.distances import geodesic_distance

        rng = np.random.default_rng(42)
        U = sample_grassmann(3, 7, rng)
        V = sample_grassmann(3, 7, rng)
        d_total = geodesic_distance(U, V)

        for t in [0.25, 0.5, 0.75]:
            W = geodesic(U, V, t)
            d = geodesic_distance(U, W)
            assert_allclose(d, t * d_total, atol=1e-10)


class TestParallelTransport:
    """Tests for parallel transport."""

    def test_transport_preserves_norm(self):
        """Parallel transport should preserve tangent vector norm."""
        from grasscalc.core.random import sample_grassmann
        from grasscalc.core.tangent import parallel_transport, tangent_project

        rng = np.random.default_rng(42)
        for _ in range(10):
            U = sample_grassmann(3, 7, rng)
            V = sample_grassmann(3, 7, rng)
            Xi = tangent_project(U, rng.standard_normal((7, 3)))

            Xi_V = parallel_transport(U, V, Xi)
            assert_allclose(norm(Xi, 'fro'), norm(Xi_V, 'fro'), atol=1e-10)

    def test_transport_preserves_inner_product(self):
        """Parallel transport should preserve inner products."""
        from grasscalc.core.random import sample_grassmann
        from grasscalc.core.tangent import parallel_transport, tangent_project, tangent_inner_product

        rng = np.random.default_rng(42)
        for _ in range(10):
            U = sample_grassmann(3, 7, rng)
            V = sample_grassmann(3, 7, rng)
            Xi = tangent_project(U, rng.standard_normal((7, 3)))
            Eta = tangent_project(U, rng.standard_normal((7, 3)))

            ip_before = tangent_inner_product(U, Xi, Eta)

            Xi_V = parallel_transport(U, V, Xi)
            Eta_V = parallel_transport(U, V, Eta)

            ip_after = tangent_inner_product(V, Xi_V, Eta_V)
            assert_allclose(ip_before, ip_after, atol=1e-10)

    def test_transport_is_tangent(self):
        """Transported vector should be tangent at destination."""
        from grasscalc.core.random import sample_grassmann
        from grasscalc.core.tangent import parallel_transport, tangent_project, is_tangent

        rng = np.random.default_rng(42)
        U = sample_grassmann(3, 7, rng)
        V = sample_grassmann(3, 7, rng)
        Xi = tangent_project(U, rng.standard_normal((7, 3)))

        Xi_V = parallel_transport(U, V, Xi)
        assert is_tangent(V, Xi_V)


class TestCurvature:
    """Tests for curvature computations."""

    def test_curvature_antisymmetry(self):
        """R(X,Y)Z = -R(Y,X)Z."""
        from grasscalc.core.random import sample_grassmann
        from grasscalc.core.tangent import curvature_tensor, tangent_project

        rng = np.random.default_rng(42)
        U = sample_grassmann(3, 7, rng)
        X = tangent_project(U, rng.standard_normal((7, 3)))
        Y = tangent_project(U, rng.standard_normal((7, 3)))
        Z = tangent_project(U, rng.standard_normal((7, 3)))

        R_XY_Z = curvature_tensor(U, X, Y, Z)
        R_YX_Z = curvature_tensor(U, Y, X, Z)

        assert_allclose(R_XY_Z, -R_YX_Z, atol=1e-10)

    def test_sectional_curvature_bounds(self):
        """Sectional curvature should be in [0, 2] for Grassmannians."""
        from grasscalc.core.random import sample_grassmann
        from grasscalc.core.tangent import sectional_curvature, tangent_project, tangent_inner_product

        rng = np.random.default_rng(42)
        for _ in range(20):
            U = sample_grassmann(3, 7, rng)

            # Create orthonormal tangent vectors
            X = tangent_project(U, rng.standard_normal((7, 3)))
            X = X / norm(X, 'fro')

            Y = tangent_project(U, rng.standard_normal((7, 3)))
            Y = Y - X * tangent_inner_product(U, X, Y)
            if norm(Y, 'fro') > 1e-10:
                Y = Y / norm(Y, 'fro')

                K = sectional_curvature(U, X, Y)
                assert 0 <= K <= 2 + 1e-10, f"K = {K} out of bounds"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
