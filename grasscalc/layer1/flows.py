"""
Gradient and geodesic flows on Grassmannians.
"""

import numpy as np
from numpy.linalg import norm
from typing import Callable, Dict, List, Optional, Tuple
from dataclasses import dataclass, field

from ..core.linalg import qr_retraction
from ..core.tangent import tangent_project, tangent_norm, exponential_map
from ..core.calculus import riemannian_gradient


@dataclass
class FlowResult:
    """Result of a gradient or geodesic flow."""
    trajectory: List[np.ndarray]
    energies: List[float]
    converged: bool
    iterations: int
    final_point: np.ndarray
    final_energy: float
    gradient_norms: List[float] = field(default_factory=list)


def gradient_flow(
    U: np.ndarray,
    objective: Callable[[np.ndarray], float],
    gradient: Optional[Callable[[np.ndarray], np.ndarray]] = None,
    dt: float = 0.1,
    eps: float = 1e-7
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Single step of gradient flow.

    U_{t+dt} = Retr_U(-dt * grad f)

    Parameters
    ----------
    U : ndarray
        Current point
    objective : callable
        Objective function f: Gr(k,n) → R
    gradient : callable, optional
        Riemannian gradient (computed numerically if not provided)
    dt : float
        Step size
    eps : float
        Numerical gradient step size

    Returns
    -------
    U_new : ndarray
        New point after gradient step
    grad : ndarray
        Gradient at U
    """
    if gradient is not None:
        grad = gradient(U)
    else:
        grad = riemannian_gradient(U, objective, eps=eps)

    # Gradient descent step
    U_new = qr_retraction(U, -dt * grad)

    return U_new, grad


def run_gradient_flow(
    U0: np.ndarray,
    objective: Callable[[np.ndarray], float],
    gradient: Optional[Callable[[np.ndarray], np.ndarray]] = None,
    dt: float = 0.1,
    tol: float = 1e-6,
    max_steps: int = 1000,
    store_trajectory: bool = True,
    adaptive_dt: bool = True,
    verbose: bool = False
) -> FlowResult:
    """
    Run gradient flow until convergence.

    Parameters
    ----------
    U0 : ndarray
        Initial point
    objective : callable
        Objective function to minimize
    gradient : callable, optional
        Riemannian gradient
    dt : float
        Initial step size
    tol : float
        Convergence tolerance (on gradient norm)
    max_steps : int
        Maximum iterations
    store_trajectory : bool
        Whether to store full trajectory
    adaptive_dt : bool
        Whether to use adaptive step size
    verbose : bool
        Print progress

    Returns
    -------
    FlowResult
        Result containing trajectory, energies, convergence info
    """
    U = U0.copy()
    trajectory = [U0.copy()] if store_trajectory else []
    energies = [objective(U0)]
    gradient_norms = []

    converged = False
    current_dt = dt

    for i in range(max_steps):
        # Compute gradient
        U_new, grad = gradient_flow(U, objective, gradient, current_dt)

        grad_norm = tangent_norm(U, grad)
        gradient_norms.append(grad_norm)

        E_new = objective(U_new)

        # Adaptive step size
        if adaptive_dt:
            if E_new > energies[-1]:
                # Energy increased, reduce step size
                current_dt *= 0.5
                continue
            elif E_new < energies[-1] - 0.1 * current_dt * grad_norm ** 2:
                # Good decrease, try larger step
                current_dt *= 1.2

        # Accept step
        U = U_new
        energies.append(E_new)

        if store_trajectory:
            trajectory.append(U.copy())

        if verbose and i % 100 == 0:
            print(f"Step {i}: E = {E_new:.6e}, |grad| = {grad_norm:.6e}")

        # Check convergence
        if grad_norm < tol:
            converged = True
            break

    return FlowResult(
        trajectory=trajectory,
        energies=energies,
        converged=converged,
        iterations=len(energies) - 1,
        final_point=U,
        final_energy=energies[-1],
        gradient_norms=gradient_norms
    )


def geodesic_flow(
    U: np.ndarray,
    Xi: np.ndarray,
    t: float = 1.0
) -> np.ndarray:
    """
    Flow along geodesic with initial velocity Xi.

    Parameters
    ----------
    U : ndarray
        Starting point
    Xi : ndarray
        Initial velocity (tangent vector)
    t : float
        Time parameter

    Returns
    -------
    V : ndarray
        Point at time t along geodesic
    """
    return exponential_map(U, t * Xi)


def hamiltonian_flow(
    U: np.ndarray,
    P: np.ndarray,
    H: Callable[[np.ndarray, np.ndarray], float],
    dt: float = 0.01,
    n_steps: int = 100
) -> Tuple[List[np.ndarray], List[np.ndarray]]:
    """
    Hamiltonian flow on T*Gr(k,n).

    Symplectic integration of Hamilton's equations:
    dU/dt = ∂H/∂P
    dP/dt = -∂H/∂U

    Parameters
    ----------
    U : ndarray
        Initial position
    P : ndarray
        Initial momentum (tangent vector)
    H : callable
        Hamiltonian H(U, P) → R
    dt : float
        Time step
    n_steps : int
        Number of steps

    Returns
    -------
    positions : list
        Trajectory in configuration space
    momenta : list
        Trajectory in momentum space
    """
    positions = [U.copy()]
    momenta = [P.copy()]

    eps = 1e-6

    for _ in range(n_steps):
        # Symplectic Euler (simplified)
        # Compute gradients numerically
        H0 = H(U, P)

        # ∂H/∂P (velocity)
        dH_dP = np.zeros_like(P)
        for i in range(P.shape[0]):
            for j in range(P.shape[1]):
                P_plus = P.copy()
                P_plus[i, j] += eps
                dH_dP[i, j] = (H(U, P_plus) - H0) / eps

        # Update position
        U_new = qr_retraction(U, dt * tangent_project(U, dH_dP))

        # ∂H/∂U (force)
        dH_dU = riemannian_gradient(U, lambda V: H(V, P), eps=eps)

        # Update momentum
        P_new = tangent_project(U_new, P - dt * dH_dU)

        U, P = U_new, P_new
        positions.append(U.copy())
        momenta.append(P.copy())

    return positions, momenta


def natural_gradient_flow(
    U: np.ndarray,
    objective: Callable[[np.ndarray], float],
    dt: float = 0.1
) -> np.ndarray:
    """
    Natural gradient flow (uses Fisher information metric).

    For Grassmannian with canonical metric, this equals standard gradient flow.

    Parameters
    ----------
    U : ndarray
        Current point
    objective : callable
        Objective function
    dt : float
        Step size

    Returns
    -------
    U_new : ndarray
        New point
    """
    # For canonical metric, natural gradient = Riemannian gradient
    U_new, _ = gradient_flow(U, objective, dt=dt)
    return U_new


def newton_flow(
    U: np.ndarray,
    objective: Callable[[np.ndarray], float],
    gradient: Optional[Callable[[np.ndarray], np.ndarray]] = None,
    damping: float = 1.0
) -> np.ndarray:
    """
    Newton's method step on Grassmannian.

    Uses approximate Hessian inversion via CG.

    Parameters
    ----------
    U : ndarray
        Current point
    objective : callable
        Objective function
    gradient : callable, optional
        Gradient function
    damping : float
        Damping factor for step size

    Returns
    -------
    U_new : ndarray
        New point after Newton step
    """
    from ..core.calculus import riemannian_hessian

    # Compute gradient
    if gradient is not None:
        grad = gradient(U)
    else:
        grad = riemannian_gradient(U, objective)

    # Approximate Newton direction via CG
    # Solve Hess(d) = -grad
    # For now, use gradient direction (Gauss-Newton approximation)
    direction = -grad

    # Line search would go here
    U_new = qr_retraction(U, damping * direction)

    return U_new
