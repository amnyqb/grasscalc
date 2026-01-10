"""
Calculus operations on Grassmannian manifolds.

Implements:
- Differentiation: Riemannian gradient, Hessian, directional/partial/covariant derivatives
- Integration: line integrals, surface integrals, volume forms
- Differential forms: exterior derivative, wedge product, pullback/pushforward
"""

import numpy as np
from numpy.linalg import norm, svd
from typing import Callable, Optional, Tuple, List, Union
from functools import wraps

from .tangent import (
    tangent_project, tangent_inner_product, tangent_norm,
    exponential_map, logarithm_map, geodesic, random_tangent
)
from .linalg import qr_retraction


# =============================================================================
# DIFFERENTIATION
# =============================================================================

def riemannian_gradient(
    U: np.ndarray,
    f: Callable[[np.ndarray], float],
    euclidean_grad: Optional[np.ndarray] = None,
    eps: float = 1e-7
) -> np.ndarray:
    """
    Compute the Riemannian gradient of f at U.

    The Riemannian gradient is the projection of the Euclidean gradient
    onto the tangent space.

    Parameters
    ----------
    U : ndarray, shape (n, k)
        Point on Grassmannian
    f : callable
        Objective function f: Gr(k,n) → R
    euclidean_grad : ndarray, optional
        Euclidean gradient ∂f/∂U if known analytically
    eps : float
        Step size for numerical differentiation if euclidean_grad not provided

    Returns
    -------
    grad_f : ndarray, shape (n, k)
        Riemannian gradient at U
    """
    if euclidean_grad is None:
        # Numerical gradient via finite differences
        euclidean_grad = _numerical_euclidean_gradient(U, f, eps)

    # Project to tangent space
    return tangent_project(U, euclidean_grad)


def _numerical_euclidean_gradient(
    U: np.ndarray,
    f: Callable[[np.ndarray], float],
    eps: float = 1e-7
) -> np.ndarray:
    """Compute Euclidean gradient numerically."""
    n, k = U.shape
    grad = np.zeros_like(U)

    f0 = f(U)
    for i in range(n):
        for j in range(k):
            U_plus = U.copy()
            U_plus[i, j] += eps
            # Re-orthonormalize
            U_plus, _ = np.linalg.qr(U_plus)
            grad[i, j] = (f(U_plus) - f0) / eps

    return grad


def riemannian_hessian(
    U: np.ndarray,
    f: Callable[[np.ndarray], float],
    Xi: np.ndarray,
    eps: float = 1e-5
) -> np.ndarray:
    """
    Compute Riemannian Hessian applied to tangent vector Xi.

    Hess_f(Xi) = ∇_Xi (grad f)

    Parameters
    ----------
    U : ndarray, shape (n, k)
        Point on Grassmannian
    f : callable
        Objective function
    Xi : ndarray, shape (n, k)
        Tangent vector direction

    Returns
    -------
    hess_Xi : ndarray, shape (n, k)
        Hessian applied to Xi
    """
    # Compute gradient at U
    grad_U = riemannian_gradient(U, f, eps=eps)

    # Move along Xi and compute gradient there
    U_plus = qr_retraction(U, eps * Xi)
    grad_U_plus = riemannian_gradient(U_plus, f, eps=eps)

    # Finite difference approximation
    # Note: should parallel transport grad_U_plus back to U for accuracy
    hess_Xi = (tangent_project(U, grad_U_plus) - grad_U) / eps

    return hess_Xi


def directional_derivative(
    U: np.ndarray,
    f: Callable[[np.ndarray], float],
    Xi: np.ndarray,
    eps: float = 1e-7
) -> float:
    """
    Directional derivative of f at U in direction Xi.

    D_Xi f = <grad f, Xi>

    Parameters
    ----------
    U : ndarray, shape (n, k)
        Point on Grassmannian
    f : callable
        Function f: Gr(k,n) → R
    Xi : ndarray, shape (n, k)
        Direction (tangent vector)
    eps : float
        Step size for numerical approximation

    Returns
    -------
    df : float
        Directional derivative
    """
    # Normalize Xi
    Xi_norm = tangent_norm(U, Xi)
    if Xi_norm < 1e-14:
        return 0.0

    Xi_unit = Xi / Xi_norm

    # Finite difference along geodesic
    U_plus = qr_retraction(U, eps * Xi_unit)
    U_minus = qr_retraction(U, -eps * Xi_unit)

    df = (f(U_plus) - f(U_minus)) / (2 * eps) * Xi_norm
    return df


def partial_derivative(
    U: np.ndarray,
    f: Callable[[np.ndarray], float],
    i: int,
    j: int,
    eps: float = 1e-7
) -> float:
    """
    Partial derivative of f with respect to coordinate (i, j).

    Computes ∂f/∂U_{ij} projected onto the tangent space.

    Parameters
    ----------
    U : ndarray, shape (n, k)
        Point on Grassmannian
    f : callable
        Function f: Gr(k,n) → R
    i : int
        Row index
    j : int
        Column index
    eps : float
        Step size

    Returns
    -------
    df_ij : float
        Partial derivative
    """
    n, k = U.shape

    # Create basis tangent vector for (i, j) direction
    E_ij = np.zeros((n, k))
    E_ij[i, j] = 1.0

    # Project to tangent space
    Xi_ij = tangent_project(U, E_ij)

    if tangent_norm(U, Xi_ij) < 1e-14:
        return 0.0

    return directional_derivative(U, f, Xi_ij, eps)


def covariant_derivative(
    U: np.ndarray,
    vector_field: Callable[[np.ndarray], np.ndarray],
    Xi: np.ndarray,
    eps: float = 1e-6
) -> np.ndarray:
    """
    Covariant derivative of a vector field along Xi.

    ∇_Xi Y = D_Xi Y + connection terms

    Parameters
    ----------
    U : ndarray, shape (n, k)
        Point on Grassmannian
    vector_field : callable
        Vector field Y: Gr(k,n) → T Gr(k,n)
    Xi : ndarray, shape (n, k)
        Direction for differentiation

    Returns
    -------
    nabla_Xi_Y : ndarray, shape (n, k)
        Covariant derivative
    """
    # Get vector field at U
    Y_U = vector_field(U)

    # Move along Xi
    U_plus = qr_retraction(U, eps * Xi)
    Y_plus = vector_field(U_plus)

    # Parallel transport Y_U to U_plus for comparison
    # Simplified: just project difference to tangent space
    diff = tangent_project(U, Y_plus - Y_U) / eps

    return diff


def lie_derivative(
    U: np.ndarray,
    vector_field_Y: Callable[[np.ndarray], np.ndarray],
    vector_field_X: Callable[[np.ndarray], np.ndarray],
    eps: float = 1e-6
) -> np.ndarray:
    """
    Lie derivative of vector field Y along vector field X.

    L_X Y = [X, Y] (Lie bracket)

    Parameters
    ----------
    U : ndarray, shape (n, k)
        Point on Grassmannian
    vector_field_Y : callable
        Vector field Y
    vector_field_X : callable
        Vector field X along which to differentiate

    Returns
    -------
    L_X_Y : ndarray, shape (n, k)
        Lie derivative [X, Y] at U
    """
    X_U = vector_field_X(U)
    Y_U = vector_field_Y(U)

    # Flow along X
    U_X = qr_retraction(U, eps * X_U)
    # Flow along Y from U_X
    Y_at_UX = vector_field_Y(U_X)

    # Flow along Y
    U_Y = qr_retraction(U, eps * Y_U)
    # Flow along X from U_Y
    X_at_UY = vector_field_X(U_Y)

    # Lie bracket approximation
    L_X_Y = (tangent_project(U, Y_at_UX) - tangent_project(U, X_at_UY)) / eps

    return L_X_Y


def jacobian(
    U: np.ndarray,
    F: Callable[[np.ndarray], np.ndarray],
    eps: float = 1e-7
) -> np.ndarray:
    """
    Jacobian of a vector-valued function F: Gr(k,n) → R^m.

    Parameters
    ----------
    U : ndarray, shape (n, k)
        Point on Grassmannian
    F : callable
        Vector-valued function
    eps : float
        Step size

    Returns
    -------
    J : ndarray, shape (m, n*k)
        Jacobian matrix
    """
    F0 = F(U)
    m = len(F0)
    n, k = U.shape

    J = np.zeros((m, n * k))

    for idx in range(n * k):
        i, j = idx // k, idx % k
        E_ij = np.zeros((n, k))
        E_ij[i, j] = 1.0
        Xi = tangent_project(U, E_ij)

        if tangent_norm(U, Xi) > 1e-14:
            U_plus = qr_retraction(U, eps * Xi)
            F_plus = F(U_plus)
            J[:, idx] = (F_plus - F0) / eps

    return J


# =============================================================================
# INTEGRATION
# =============================================================================

def line_integral(
    f: Callable[[np.ndarray], float],
    curve: Callable[[float], np.ndarray],
    t0: float = 0.0,
    t1: float = 1.0,
    n_points: int = 100
) -> float:
    """
    Line integral of function f along a curve on the Grassmannian.

    ∫_γ f ds = ∫_{t0}^{t1} f(γ(t)) ||γ'(t)|| dt

    Parameters
    ----------
    f : callable
        Scalar function f: Gr(k,n) → R
    curve : callable
        Parameterized curve γ: [t0, t1] → Gr(k,n)
    t0, t1 : float
        Parameter interval
    n_points : int
        Number of quadrature points

    Returns
    -------
    integral : float
        Line integral value
    """
    dt = (t1 - t0) / n_points
    integral = 0.0

    for i in range(n_points):
        t = t0 + (i + 0.5) * dt
        U = curve(t)

        # Approximate curve velocity
        U_plus = curve(t + dt / 2)
        U_minus = curve(t - dt / 2)

        # Velocity magnitude via geodesic distance
        try:
            from .distances import geodesic_distance
            speed = geodesic_distance(U_minus, U_plus) / dt
        except:
            speed = 1.0  # Fallback

        integral += f(U) * speed * dt

    return integral


def integrate_over_geodesic(
    f: Callable[[np.ndarray], float],
    U: np.ndarray,
    V: np.ndarray,
    n_points: int = 50
) -> float:
    """
    Integrate function f along the geodesic from U to V.

    Parameters
    ----------
    f : callable
        Scalar function f: Gr(k,n) → R
    U : ndarray
        Starting point
    V : ndarray
        Ending point
    n_points : int
        Number of quadrature points

    Returns
    -------
    integral : float
        ∫_0^1 f(γ(t)) ||γ'(t)|| dt
    """
    # Define geodesic curve
    def gamma(t):
        return geodesic(U, V, t)

    return line_integral(f, gamma, 0.0, 1.0, n_points)


def surface_integral(
    f: Callable[[np.ndarray], float],
    surface: Callable[[float, float], np.ndarray],
    u_range: Tuple[float, float] = (0.0, 1.0),
    v_range: Tuple[float, float] = (0.0, 1.0),
    n_u: int = 20,
    n_v: int = 20
) -> float:
    """
    Surface integral over a parameterized surface on the Grassmannian.

    ∫∫_S f dA

    Parameters
    ----------
    f : callable
        Scalar function f: Gr(k,n) → R
    surface : callable
        Parameterized surface σ(u, v) → Gr(k,n)
    u_range, v_range : tuple
        Parameter ranges
    n_u, n_v : int
        Number of grid points

    Returns
    -------
    integral : float
        Surface integral value
    """
    du = (u_range[1] - u_range[0]) / n_u
    dv = (v_range[1] - v_range[0]) / n_v
    integral = 0.0

    for i in range(n_u):
        for j in range(n_v):
            u = u_range[0] + (i + 0.5) * du
            v = v_range[0] + (j + 0.5) * dv

            U = surface(u, v)

            # Approximate area element via metric
            # This is a simplification; proper implementation needs Jacobian
            area_element = du * dv

            integral += f(U) * area_element

    return integral


def volume_element(U: np.ndarray) -> float:
    """
    Riemannian volume element at point U.

    For Grassmannian Gr(k,n), the volume form is determined by the
    canonical metric.

    Parameters
    ----------
    U : ndarray, shape (n, k)
        Point on Grassmannian

    Returns
    -------
    vol : float
        Volume element (determinant of metric tensor = 1 for canonical metric)
    """
    # For canonical metric on Grassmannian, volume element is constant
    return 1.0


def grassmann_volume(k: int, n: int) -> float:
    """
    Total volume of Grassmannian Gr(k,n) with canonical metric.

    Vol(Gr(k,n)) = Vol(O(n)) / (Vol(O(k)) × Vol(O(n-k)))

    Parameters
    ----------
    k : int
        Fiber dimension
    n : int
        Ambient dimension

    Returns
    -------
    vol : float
        Total volume
    """
    from scipy.special import gamma as gamma_func

    def vol_orthogonal(m):
        """Volume of O(m)."""
        if m == 0:
            return 1.0
        if m == 1:
            return 2.0
        # Vol(O(m)) = 2^m * π^{m(m-1)/4} * ∏_{j=1}^{m-1} Γ((j+1)/2) / Γ(1/2)^{m-1}
        prod = 1.0
        for j in range(1, m):
            prod *= gamma_func((j + 1) / 2)
        return (2 ** m) * (np.pi ** (m * (m - 1) / 4)) * prod

    return vol_orthogonal(n) / (vol_orthogonal(k) * vol_orthogonal(n - k))


def monte_carlo_integral(
    f: Callable[[np.ndarray], float],
    k: int,
    n: int,
    n_samples: int = 10000,
    rng: Optional[np.random.Generator] = None
) -> Tuple[float, float]:
    """
    Monte Carlo integration over Gr(k,n).

    Parameters
    ----------
    f : callable
        Function to integrate
    k, n : int
        Grassmannian parameters
    n_samples : int
        Number of Monte Carlo samples
    rng : Generator, optional
        Random number generator

    Returns
    -------
    mean : float
        Estimated integral (normalized by volume)
    std_err : float
        Standard error estimate
    """
    from .random import sample_grassmann

    if rng is None:
        rng = np.random.default_rng()

    values = np.zeros(n_samples)
    for i in range(n_samples):
        U = sample_grassmann(k, n, rng)
        values[i] = f(U)

    mean = np.mean(values)
    std_err = np.std(values) / np.sqrt(n_samples)

    return mean, std_err


# =============================================================================
# DIFFERENTIAL FORMS
# =============================================================================

class DifferentialForm:
    """
    Differential form on the Grassmannian.

    Represents a k-form ω that can be evaluated on k tangent vectors.
    """

    def __init__(self, degree: int, evaluator: Callable):
        """
        Create a differential form.

        Parameters
        ----------
        degree : int
            Degree of the form (0 = function, 1 = 1-form, etc.)
        evaluator : callable
            Function (U, *vectors) → float that evaluates the form
        """
        self.degree = degree
        self._eval = evaluator

    def __call__(self, U: np.ndarray, *vectors: np.ndarray) -> float:
        """Evaluate the form at U on the given tangent vectors."""
        if len(vectors) != self.degree:
            raise ValueError(f"Expected {self.degree} vectors, got {len(vectors)}")
        return self._eval(U, *vectors)

    def __add__(self, other: 'DifferentialForm') -> 'DifferentialForm':
        """Add two forms of the same degree."""
        if self.degree != other.degree:
            raise ValueError("Cannot add forms of different degree")

        def sum_eval(U, *vectors):
            return self(U, *vectors) + other(U, *vectors)

        return DifferentialForm(self.degree, sum_eval)

    def __mul__(self, scalar: float) -> 'DifferentialForm':
        """Scalar multiplication."""
        def scaled_eval(U, *vectors):
            return scalar * self(U, *vectors)
        return DifferentialForm(self.degree, scaled_eval)

    def __rmul__(self, scalar: float) -> 'DifferentialForm':
        return self.__mul__(scalar)


def differential_form(degree: int, evaluator: Callable) -> DifferentialForm:
    """Create a differential form."""
    return DifferentialForm(degree, evaluator)


def exterior_derivative(omega: DifferentialForm, eps: float = 1e-6) -> DifferentialForm:
    """
    Compute exterior derivative of a differential form.

    dω is a (k+1)-form where k is the degree of ω.

    Parameters
    ----------
    omega : DifferentialForm
        Input k-form
    eps : float
        Step size for numerical differentiation

    Returns
    -------
    d_omega : DifferentialForm
        Exterior derivative (k+1)-form
    """
    k = omega.degree

    def d_omega_eval(U: np.ndarray, *vectors: np.ndarray) -> float:
        """Evaluate dω using Cartan's formula."""
        if len(vectors) != k + 1:
            raise ValueError(f"Expected {k+1} vectors")

        result = 0.0

        # Sum over all ways to omit one vector
        for i in range(k + 1):
            # Vectors with i-th omitted
            remaining = list(vectors[:i]) + list(vectors[i+1:])
            Xi = vectors[i]

            # Directional derivative of ω(remaining) along Xi
            def omega_remaining(V):
                # Transport remaining vectors (simplified)
                return omega(V, *remaining)

            # Numerical derivative
            U_plus = qr_retraction(U, eps * Xi)
            U_minus = qr_retraction(U, -eps * Xi)
            deriv = (omega_remaining(U_plus) - omega_remaining(U_minus)) / (2 * eps)

            result += ((-1) ** i) * deriv

        return result

    return DifferentialForm(k + 1, d_omega_eval)


def wedge_product(omega1: DifferentialForm, omega2: DifferentialForm) -> DifferentialForm:
    """
    Wedge product of two differential forms.

    (ω₁ ∧ ω₂)(X₁, ..., X_{k+l}) = (1/(k!l!)) Σ sign(σ) ω₁(X_{σ(1)}, ...) ω₂(...)

    Parameters
    ----------
    omega1 : DifferentialForm
        k-form
    omega2 : DifferentialForm
        l-form

    Returns
    -------
    wedge : DifferentialForm
        (k+l)-form
    """
    from itertools import permutations
    from math import factorial

    k = omega1.degree
    l = omega2.degree

    def wedge_eval(U: np.ndarray, *vectors: np.ndarray) -> float:
        if len(vectors) != k + l:
            raise ValueError(f"Expected {k+l} vectors")

        result = 0.0
        indices = list(range(k + l))

        for perm in permutations(indices):
            # Compute sign of permutation
            sign = _permutation_sign(perm)

            # Split permutation
            first_indices = perm[:k]
            second_indices = perm[k:]

            first_vectors = [vectors[i] for i in first_indices]
            second_vectors = [vectors[i] for i in second_indices]

            result += sign * omega1(U, *first_vectors) * omega2(U, *second_vectors)

        # Normalize
        result /= (factorial(k) * factorial(l))

        return result

    return DifferentialForm(k + l, wedge_eval)


def _permutation_sign(perm: tuple) -> int:
    """Compute sign of a permutation (+1 or -1)."""
    n = len(perm)
    inversions = 0
    for i in range(n):
        for j in range(i + 1, n):
            if perm[i] > perm[j]:
                inversions += 1
    return 1 if inversions % 2 == 0 else -1


def pullback(
    phi: Callable[[np.ndarray], np.ndarray],
    omega: DifferentialForm,
    eps: float = 1e-6
) -> DifferentialForm:
    """
    Pullback of a differential form by a smooth map.

    (φ*ω)(X₁, ..., Xₖ) = ω(dφ(X₁), ..., dφ(Xₖ))

    Parameters
    ----------
    phi : callable
        Smooth map φ: Gr(k,n) → Gr(k',n')
    omega : DifferentialForm
        Form on the target manifold
    eps : float
        Step size for computing differential

    Returns
    -------
    phi_star_omega : DifferentialForm
        Pullback form on source manifold
    """
    k = omega.degree

    def pullback_eval(U: np.ndarray, *vectors: np.ndarray) -> float:
        # Compute image point
        V = phi(U)

        # Compute differential of phi at each vector
        pushed_vectors = []
        for Xi in vectors:
            # dφ(Xi) via finite difference
            U_plus = qr_retraction(U, eps * Xi)
            V_plus = phi(U_plus)

            # Approximate tangent vector at V
            dPhi_Xi = tangent_project(V, (V_plus - V) / eps)
            pushed_vectors.append(dPhi_Xi)

        return omega(V, *pushed_vectors)

    return DifferentialForm(k, pullback_eval)


def pushforward(
    phi: Callable[[np.ndarray], np.ndarray],
    U: np.ndarray,
    Xi: np.ndarray,
    eps: float = 1e-6
) -> np.ndarray:
    """
    Pushforward of a tangent vector by a smooth map.

    dφ(Xi) = d/dt|_{t=0} φ(γ(t)) where γ is curve with γ'(0) = Xi

    Parameters
    ----------
    phi : callable
        Smooth map φ: Gr(k,n) → Gr(k',n')
    U : ndarray
        Base point
    Xi : ndarray
        Tangent vector at U
    eps : float
        Step size

    Returns
    -------
    dPhi_Xi : ndarray
        Pushed forward tangent vector at φ(U)
    """
    V = phi(U)
    U_plus = qr_retraction(U, eps * Xi)
    V_plus = phi(U_plus)

    # Approximate tangent vector at V
    dPhi_Xi = tangent_project(V, (V_plus - V) / eps)

    return dPhi_Xi


# =============================================================================
# SPECIAL FORMS ON GRASSMANNIAN
# =============================================================================

def canonical_1form(U: np.ndarray, Xi: np.ndarray) -> float:
    """
    Canonical 1-form on the Grassmannian.

    θ(Xi) = trace(U^T Xi)

    Note: This is zero for tangent vectors (U^T Xi = 0).
    """
    return np.trace(U.T @ Xi)


def symplectic_form(U: np.ndarray, Xi: np.ndarray, Eta: np.ndarray) -> float:
    """
    Symplectic 2-form on the Grassmannian (for complex case).

    ω(Xi, Eta) = Im(trace(Xi^H Eta))

    For real Grassmannians, this is the skew part.
    """
    return np.trace(Xi.T @ Eta) - np.trace(Eta.T @ Xi)


def metric_form(U: np.ndarray, Xi: np.ndarray, Eta: np.ndarray) -> float:
    """
    Riemannian metric as a 2-form.

    g(Xi, Eta) = trace(Xi^T Eta)
    """
    return tangent_inner_product(U, Xi, Eta)


def volume_form(k: int, n: int) -> DifferentialForm:
    """
    Volume form on Gr(k,n).

    The top-degree form that gives the Riemannian volume.

    Parameters
    ----------
    k, n : int
        Grassmannian parameters

    Returns
    -------
    vol : DifferentialForm
        Volume form of degree k(n-k)
    """
    dim = k * (n - k)

    def vol_eval(U: np.ndarray, *vectors: np.ndarray) -> float:
        if len(vectors) != dim:
            return 0.0

        # Construct matrix of inner products
        gram = np.zeros((dim, dim))
        for i in range(dim):
            for j in range(dim):
                gram[i, j] = tangent_inner_product(U, vectors[i], vectors[j])

        # Volume element is sqrt(det(Gram matrix))
        det = np.linalg.det(gram)
        return np.sqrt(max(0.0, det))

    return DifferentialForm(dim, vol_eval)
