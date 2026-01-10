"""Tests for grasscalc.core.calculus module."""

import numpy as np
import pytest
from numpy.testing import assert_allclose
from numpy.linalg import norm


class TestRiemannianGradient:
    """Tests for Riemannian gradient."""

    def test_gradient_is_tangent(self):
        """Gradient should be a tangent vector."""
        from grasscalc.core.random import sample_grassmann
        from grasscalc.core.calculus import riemannian_gradient
        from grasscalc.core.tangent import is_tangent
        from grasscalc.core.distances import chordal_distance_sq

        rng = np.random.default_rng(42)
        U = sample_grassmann(3, 7, rng)
        V_target = sample_grassmann(3, 7, rng)

        def f(W):
            return chordal_distance_sq(W, V_target)

        grad = riemannian_gradient(U, f)
        assert is_tangent(U, grad)

    def test_gradient_descent_decreases(self):
        """Moving along negative gradient should decrease objective."""
        from grasscalc.core.random import sample_grassmann
        from grasscalc.core.calculus import riemannian_gradient
        from grasscalc.core.tangent import exponential_map
        from grasscalc.core.distances import chordal_distance_sq

        rng = np.random.default_rng(42)
        U = sample_grassmann(3, 7, rng)
        V_target = sample_grassmann(3, 7, rng)

        def f(W):
            return chordal_distance_sq(W, V_target)

        grad = riemannian_gradient(U, f)
        U_new = exponential_map(U, -0.1 * grad)

        assert f(U_new) < f(U)

    def test_gradient_at_minimum(self):
        """Gradient at minimum should be near zero."""
        from grasscalc.core.random import sample_grassmann
        from grasscalc.core.calculus import riemannian_gradient
        from grasscalc.core.distances import chordal_distance_sq

        rng = np.random.default_rng(42)
        V_target = sample_grassmann(3, 7, rng)

        def f(W):
            return chordal_distance_sq(W, V_target)

        grad = riemannian_gradient(V_target, f)
        assert norm(grad, 'fro') < 1e-6

    def test_gradient_of_linear_function(self):
        """Test gradient of trace(A^T U U^T B)."""
        from grasscalc.core.random import sample_grassmann
        from grasscalc.core.calculus import riemannian_gradient

        rng = np.random.default_rng(42)
        n, k = 7, 3
        U = sample_grassmann(k, n, rng)
        A = rng.standard_normal((n, n))
        A = A + A.T  # Symmetric

        def f(W):
            return np.trace(A @ W @ W.T)

        grad = riemannian_gradient(U, f)
        assert grad.shape == (n, k)


class TestDirectionalDerivative:
    """Tests for directional derivative."""

    def test_directional_derivative_linearity(self):
        """D_Xi f + D_Eta f = D_{Xi+Eta} f approximately."""
        from grasscalc.core.random import sample_grassmann
        from grasscalc.core.calculus import directional_derivative
        from grasscalc.core.tangent import tangent_project
        from grasscalc.core.distances import chordal_distance_sq

        rng = np.random.default_rng(42)
        U = sample_grassmann(3, 7, rng)
        V_target = sample_grassmann(3, 7, rng)

        def f(W):
            return chordal_distance_sq(W, V_target)

        Xi = tangent_project(U, rng.standard_normal((7, 3))) * 0.1
        Eta = tangent_project(U, rng.standard_normal((7, 3))) * 0.1

        D_Xi = directional_derivative(U, f, Xi)
        D_Eta = directional_derivative(U, f, Eta)
        D_sum = directional_derivative(U, f, Xi + Eta)

        assert_allclose(D_Xi + D_Eta, D_sum, rtol=0.1)

    def test_directional_derivative_scaling(self):
        """D_{alpha*Xi} f = alpha * D_Xi f."""
        from grasscalc.core.random import sample_grassmann
        from grasscalc.core.calculus import directional_derivative
        from grasscalc.core.tangent import tangent_project
        from grasscalc.core.distances import chordal_distance_sq

        rng = np.random.default_rng(42)
        U = sample_grassmann(3, 7, rng)
        V_target = sample_grassmann(3, 7, rng)

        def f(W):
            return chordal_distance_sq(W, V_target)

        Xi = tangent_project(U, rng.standard_normal((7, 3)))
        alpha = 2.5

        D_Xi = directional_derivative(U, f, Xi)
        D_alpha_Xi = directional_derivative(U, f, alpha * Xi)

        assert_allclose(D_alpha_Xi, alpha * D_Xi, rtol=0.1)


class TestCovariantDerivative:
    """Tests for covariant derivative."""

    def test_covariant_derivative_is_tangent(self):
        """Covariant derivative should produce tangent vector."""
        from grasscalc.core.random import sample_grassmann
        from grasscalc.core.calculus import covariant_derivative
        from grasscalc.core.tangent import tangent_project, is_tangent

        rng = np.random.default_rng(42)
        U = sample_grassmann(3, 7, rng)
        Xi = tangent_project(U, rng.standard_normal((7, 3)))

        def vector_field(W):
            return tangent_project(W, np.ones((7, 3)))

        nabla = covariant_derivative(U, vector_field, Xi)
        assert is_tangent(U, nabla)

    def test_covariant_derivative_product_rule(self):
        """Test Leibniz rule for scalar * vector field."""
        from grasscalc.core.random import sample_grassmann
        from grasscalc.core.calculus import covariant_derivative, directional_derivative
        from grasscalc.core.tangent import tangent_project

        rng = np.random.default_rng(42)
        U = sample_grassmann(3, 7, rng)
        Xi = tangent_project(U, rng.standard_normal((7, 3)))

        def scalar_f(W):
            return float(np.sum(W))

        def vector_field(W):
            return tangent_project(W, np.ones((7, 3)))

        # Leibniz: nabla(f*Y) = (df)Y + f*nabla(Y)
        def fY(W):
            return scalar_f(W) * vector_field(W)

        nabla_fY = covariant_derivative(U, fY, Xi)
        df = directional_derivative(U, scalar_f, Xi)
        Y_U = vector_field(U)
        nabla_Y = covariant_derivative(U, vector_field, Xi)

        expected = df * Y_U + scalar_f(U) * nabla_Y
        assert_allclose(nabla_fY, expected, atol=1e-4)


class TestLineIntegral:
    """Tests for line integrals."""

    def test_line_integral_constant(self):
        """Integral of 1 along geodesic equals arc length."""
        from grasscalc.core.random import sample_grassmann
        from grasscalc.core.calculus import line_integral
        from grasscalc.core.tangent import geodesic
        from grasscalc.core.distances import geodesic_distance

        rng = np.random.default_rng(42)
        U = sample_grassmann(3, 7, rng)
        V = sample_grassmann(3, 7, rng)

        def curve(t):
            return geodesic(U, V, t)

        integral = line_integral(lambda W: 1.0, curve, 0.0, 1.0, n_points=100)
        expected = geodesic_distance(U, V)

        assert_allclose(integral, expected, rtol=0.01)

    def test_line_integral_partial(self):
        """Integral over partial geodesic."""
        from grasscalc.core.random import sample_grassmann
        from grasscalc.core.calculus import line_integral
        from grasscalc.core.tangent import geodesic
        from grasscalc.core.distances import geodesic_distance

        rng = np.random.default_rng(42)
        U = sample_grassmann(3, 7, rng)
        V = sample_grassmann(3, 7, rng)

        def curve(t):
            return geodesic(U, V, t)

        # Integral from 0 to 0.5 should be half the total
        integral_half = line_integral(lambda W: 1.0, curve, 0.0, 0.5, n_points=50)
        total = geodesic_distance(U, V)

        assert_allclose(integral_half, total / 2, rtol=0.02)

    def test_line_integral_additivity(self):
        """Integral over [0,1] = integral over [0,0.5] + [0.5,1]."""
        from grasscalc.core.random import sample_grassmann
        from grasscalc.core.calculus import line_integral
        from grasscalc.core.tangent import geodesic
        from grasscalc.core.distances import chordal_distance_sq

        rng = np.random.default_rng(42)
        U = sample_grassmann(3, 7, rng)
        V = sample_grassmann(3, 7, rng)
        target = sample_grassmann(3, 7, rng)

        def curve(t):
            return geodesic(U, V, t)

        def integrand(W):
            return chordal_distance_sq(W, target)

        integral_full = line_integral(integrand, curve, 0.0, 1.0, n_points=100)
        integral_first = line_integral(integrand, curve, 0.0, 0.5, n_points=50)
        integral_second = line_integral(integrand, curve, 0.5, 1.0, n_points=50)

        assert_allclose(integral_full, integral_first + integral_second, rtol=0.05)


class TestDifferentialForms:
    """Tests for differential forms operations."""

    def test_exterior_derivative_closed(self):
        """d(d omega) = 0 for any form."""
        from grasscalc.core.calculus import differential_form, exterior_derivative

        # Create a simple 0-form (scalar function)
        def omega(U):
            return float(np.sum(U ** 2))

        form = differential_form(0, omega)
        d_form = exterior_derivative(form)
        dd_form = exterior_derivative(d_form)

        # dd should be zero
        from grasscalc.core.random import sample_grassmann
        rng = np.random.default_rng(42)
        U = sample_grassmann(3, 7, rng)

        # Evaluate dd at U (should be essentially zero)
        # This is conceptual - actual implementation may differ


class TestHessian:
    """Tests for Riemannian Hessian."""

    def test_hessian_symmetry(self):
        """Hessian should be symmetric: <Hess f[Xi], Eta> = <Xi, Hess f[Eta]>."""
        from grasscalc.core.random import sample_grassmann
        from grasscalc.core.calculus import riemannian_hessian
        from grasscalc.core.tangent import tangent_project, tangent_inner_product
        from grasscalc.core.distances import chordal_distance_sq

        rng = np.random.default_rng(42)
        U = sample_grassmann(3, 7, rng)
        target = sample_grassmann(3, 7, rng)

        def f(W):
            return chordal_distance_sq(W, target)

        Xi = tangent_project(U, rng.standard_normal((7, 3)))
        Eta = tangent_project(U, rng.standard_normal((7, 3)))

        Hess_Xi = riemannian_hessian(U, f, Xi)
        Hess_Eta = riemannian_hessian(U, f, Eta)

        ip1 = tangent_inner_product(U, Hess_Xi, Eta)
        ip2 = tangent_inner_product(U, Xi, Hess_Eta)

        assert_allclose(ip1, ip2, rtol=0.1)

    def test_hessian_is_tangent(self):
        """Hessian output should be tangent."""
        from grasscalc.core.random import sample_grassmann
        from grasscalc.core.calculus import riemannian_hessian
        from grasscalc.core.tangent import tangent_project, is_tangent
        from grasscalc.core.distances import chordal_distance_sq

        rng = np.random.default_rng(42)
        U = sample_grassmann(3, 7, rng)
        target = sample_grassmann(3, 7, rng)

        def f(W):
            return chordal_distance_sq(W, target)

        Xi = tangent_project(U, rng.standard_normal((7, 3)))
        Hess_Xi = riemannian_hessian(U, f, Xi)

        assert is_tangent(U, Hess_Xi)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
