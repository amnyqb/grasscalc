"""Tests for grasscalc.layer1 module (within-manifold calculus)."""

import numpy as np
import pytest
from numpy.testing import assert_allclose
from numpy.linalg import norm


class TestObjectives:
    """Tests for objective functions."""

    def test_energy_overlap_basic(self):
        """Energy overlap should be non-negative and bound stage function."""
        from grasscalc.core.random import sample_grassmann
        from grasscalc.layer1.objectives import energy_overlap

        rng = np.random.default_rng(42)
        n, k, r = 10, 3, 4

        for _ in range(20):
            U = sample_grassmann(k, n, rng)
            U_R = sample_grassmann(r, n, rng)  # Reference subspace
            s, tau, E = energy_overlap(U, U_R)

            # Stage function should be in [0, k]
            assert 0 <= s <= k + 1e-10
            # Target is k
            assert tau == k
            # Energy is non-negative
            assert E >= 0

    def test_energy_overlap_aligned(self):
        """Self-aligned subspaces should have maximal overlap ratio."""
        from grasscalc.core.random import sample_grassmann
        from grasscalc.layer1.objectives import energy_overlap

        rng = np.random.default_rng(42)
        n, k = 10, 3

        U = sample_grassmann(k, n, rng)
        # Self-alignment: s = ||U^T U||_F² / k = ||I_k||_F² / k = k / k = 1
        s, tau, E = energy_overlap(U, U)
        # Perfect self-overlap gives s = 1 (normalized overlap)
        assert_allclose(s, 1.0, atol=1e-10)
        # Target is k for general case
        assert tau == k

    def test_rayleigh_quotient_eigenvalue(self):
        """Rayleigh quotient at eigenvector equals eigenvalue."""
        from grasscalc.layer1.objectives import rayleigh_quotient

        n = 10
        rng = np.random.default_rng(42)
        A = rng.standard_normal((n, n))
        A = A + A.T

        eigvals, eigvecs = np.linalg.eigh(A)

        # Take top eigenvector
        U = eigvecs[:, -1:].copy()
        R = rayleigh_quotient(U, A)
        assert_allclose(R, eigvals[-1], atol=1e-10)

    def test_distance_objective(self):
        """Test distance objective function."""
        from grasscalc.core.random import sample_grassmann
        from grasscalc.layer1.objectives import distance_objective
        from grasscalc.core.distances import chordal_distance_sq

        rng = np.random.default_rng(42)
        U = sample_grassmann(3, 7, rng)
        V = sample_grassmann(3, 7, rng)

        d1 = distance_objective(U, V)
        d2 = chordal_distance_sq(U, V)
        assert_allclose(d1, d2, atol=1e-10)


class TestGradientFlow:
    """Tests for gradient flow."""

    def test_gradient_flow_decreases(self):
        """Gradient flow should decrease objective."""
        from grasscalc.core.random import sample_grassmann
        from grasscalc.core.distances import chordal_distance_sq
        from grasscalc.layer1.flows import gradient_flow

        rng = np.random.default_rng(42)
        U = sample_grassmann(3, 7, rng)
        target = sample_grassmann(3, 7, rng)

        def f(W):
            return chordal_distance_sq(W, target)

        f_before = f(U)
        U_new, grad = gradient_flow(U, f, dt=0.1)
        f_after = f(U_new)

        assert f_after < f_before

    def test_run_gradient_flow_convergence(self):
        """Gradient flow should converge to minimum."""
        from grasscalc.core.random import sample_grassmann
        from grasscalc.core.distances import chordal_distance_sq
        from grasscalc.layer1.flows import run_gradient_flow

        rng = np.random.default_rng(42)
        U0 = sample_grassmann(3, 7, rng)
        target = sample_grassmann(3, 7, rng)

        def f(W):
            return chordal_distance_sq(W, target)

        result = run_gradient_flow(U0, f, max_steps=100, dt=0.1)

        # Should have final point
        assert result.final_point is not None
        # Should converge near target
        assert result.final_energy < 0.1

    def test_geodesic_flow_preserves_speed(self):
        """Geodesic flow should maintain constant speed."""
        from grasscalc.core.random import sample_grassmann
        from grasscalc.core.tangent import tangent_project
        from grasscalc.layer1.flows import geodesic_flow
        from grasscalc.core.distances import geodesic_distance

        rng = np.random.default_rng(42)
        U = sample_grassmann(3, 7, rng)
        Xi = tangent_project(U, rng.standard_normal((7, 3)))
        Xi = Xi / norm(Xi, 'fro')  # Unit speed

        # Move along geodesic
        t_values = [0.1, 0.2, 0.3]
        distances = []

        for t in t_values:
            V = geodesic_flow(U, Xi, t)
            d = geodesic_distance(U, V)
            distances.append(d)

        # Distances should be proportional to t
        for i, t in enumerate(t_values):
            assert_allclose(distances[i], t, atol=1e-10)


class TestOptimization:
    """Tests for optimization algorithms."""

    def test_minimize_convergence(self):
        """Optimizer should find minimum of distance function."""
        from grasscalc.core.random import sample_grassmann
        from grasscalc.core.distances import chordal_distance_sq, geodesic_distance
        from grasscalc.layer1.optim import minimize_on_grassmann

        rng = np.random.default_rng(42)
        U0 = sample_grassmann(3, 7, rng)
        target = sample_grassmann(3, 7, rng)

        def f(W):
            return chordal_distance_sq(W, target)

        result = minimize_on_grassmann(U0, f, method='gradient_descent', max_iter=200, dt=0.1)

        # Should be very close to target
        d = geodesic_distance(result.final_point, target)
        assert d < 0.1

    def test_rayleigh_quotient_optimization(self):
        """Minimizing -Rayleigh should find top eigenspace."""
        from grasscalc.core.random import sample_grassmann
        from grasscalc.layer1.objectives import rayleigh_quotient
        from grasscalc.layer1.optim import minimize_on_grassmann

        rng = np.random.default_rng(42)
        n, k = 10, 3
        A = rng.standard_normal((n, n))
        A = A + A.T

        eigvals = np.linalg.eigvalsh(A)
        expected = np.sum(eigvals[-k:])  # Sum of top k eigenvalues

        def f(W):
            return -rayleigh_quotient(W, A)

        U0 = sample_grassmann(k, n, rng)
        result = minimize_on_grassmann(U0, f, method='gradient_descent', max_iter=300, dt=0.05)

        achieved = rayleigh_quotient(result.final_point, A)
        assert_allclose(achieved, expected, rtol=0.1)

    def test_trust_region_step(self):
        """Trust region step should produce valid step."""
        from grasscalc.core.random import sample_grassmann
        from grasscalc.core.tangent import tangent_project
        from grasscalc.layer1.optim import trust_region_step

        rng = np.random.default_rng(42)
        U = sample_grassmann(3, 7, rng)

        # Create a gradient (tangent vector)
        grad = tangent_project(U, rng.standard_normal((7, 3)))

        step = trust_region_step(U, grad, delta=0.5)

        # Step should be a tangent vector
        assert step.shape == (7, 3)
        # Step norm should be bounded by delta
        assert norm(step, 'fro') <= 0.5 + 1e-10

    def test_conjugate_gradient_method(self):
        """CG optimization should converge."""
        from grasscalc.core.random import sample_grassmann
        from grasscalc.core.distances import chordal_distance_sq
        from grasscalc.layer1.optim import minimize_on_grassmann

        rng = np.random.default_rng(42)
        U0 = sample_grassmann(3, 7, rng)
        target = sample_grassmann(3, 7, rng)

        def f(W):
            return chordal_distance_sq(W, target)

        result = minimize_on_grassmann(U0, f, method='conjugate_gradient', max_iter=100)
        assert result.final_energy < 0.5  # Should have made progress


class TestHamiltonianFlow:
    """Tests for Hamiltonian dynamics."""

    def test_hamiltonian_flow_runs(self):
        """Hamiltonian flow should produce valid output."""
        from grasscalc.core.random import sample_grassmann
        from grasscalc.core.tangent import tangent_project
        from grasscalc.layer1.flows import hamiltonian_flow

        rng = np.random.default_rng(42)
        n, k = 7, 3
        U = sample_grassmann(k, n, rng)
        P = tangent_project(U, rng.standard_normal((n, k)))

        # Simple Hamiltonian: kinetic energy only
        def H(W, Mom):
            return 0.5 * np.sum(Mom ** 2)

        # hamiltonian_flow returns (positions_list, momenta_list)
        positions, momenta = hamiltonian_flow(U, P, H, dt=0.01, n_steps=10)

        # Get final position and momentum
        U_new = positions[-1]
        P_new = momenta[-1]

        assert U_new.shape == (n, k)
        assert P_new.shape == (n, k)
        # Should still be orthonormal
        assert_allclose(U_new.T @ U_new, np.eye(k), atol=1e-10)

    def test_hamiltonian_flow_trajectory(self):
        """Hamiltonian flow should return trajectory of expected length."""
        from grasscalc.core.random import sample_grassmann
        from grasscalc.core.tangent import tangent_project
        from grasscalc.layer1.flows import hamiltonian_flow

        rng = np.random.default_rng(42)
        n, k = 7, 3
        U = sample_grassmann(k, n, rng)
        P = tangent_project(U, rng.standard_normal((n, k)))

        def H(W, Mom):
            return 0.5 * np.sum(Mom ** 2)

        n_steps = 20
        positions, momenta = hamiltonian_flow(U, P, H, dt=0.01, n_steps=n_steps)

        # Should have n_steps + 1 points (including initial)
        assert len(positions) == n_steps + 1
        assert len(momenta) == n_steps + 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
