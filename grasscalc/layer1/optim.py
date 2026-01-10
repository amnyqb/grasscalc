"""
Optimization algorithms on Grassmannians.
"""

import numpy as np
from numpy.linalg import norm
from typing import Callable, Dict, Optional, Tuple
from dataclasses import dataclass

from ..core.linalg import qr_retraction
from ..core.tangent import tangent_project, tangent_norm, tangent_inner_product
from ..core.calculus import riemannian_gradient
from .flows import FlowResult


def minimize_on_grassmann(
    U0: np.ndarray,
    objective: Callable[[np.ndarray], float],
    gradient: Optional[Callable[[np.ndarray], np.ndarray]] = None,
    method: str = 'gradient_descent',
    tol: float = 1e-6,
    max_iter: int = 1000,
    **kwargs
) -> FlowResult:
    """
    Minimize a function on the Grassmannian.

    Parameters
    ----------
    U0 : ndarray
        Initial point
    objective : callable
        Function to minimize
    gradient : callable, optional
        Riemannian gradient
    method : str
        Optimization method: 'gradient_descent', 'conjugate_gradient', 'trust_region'
    tol : float
        Convergence tolerance
    max_iter : int
        Maximum iterations
    **kwargs
        Additional method-specific parameters

    Returns
    -------
    FlowResult
        Optimization result
    """
    if method == 'gradient_descent':
        from .flows import run_gradient_flow
        return run_gradient_flow(
            U0, objective, gradient,
            tol=tol, max_steps=max_iter,
            **kwargs
        )

    elif method == 'conjugate_gradient':
        return _conjugate_gradient_minimize(
            U0, objective, gradient, tol, max_iter, **kwargs
        )

    elif method == 'trust_region':
        return _trust_region_minimize(
            U0, objective, gradient, tol, max_iter, **kwargs
        )

    else:
        raise ValueError(f"Unknown method: {method}")


def _conjugate_gradient_minimize(
    U0: np.ndarray,
    objective: Callable[[np.ndarray], float],
    gradient: Optional[Callable[[np.ndarray], np.ndarray]],
    tol: float,
    max_iter: int,
    **kwargs
) -> FlowResult:
    """Conjugate gradient optimization on Grassmannian."""
    U = U0.copy()
    energies = [objective(U0)]
    trajectory = [U0.copy()]
    gradient_norms = []

    # Initial gradient and direction
    if gradient is not None:
        grad = gradient(U)
    else:
        grad = riemannian_gradient(U, objective)

    direction = -grad
    grad_norm_sq = tangent_inner_product(U, grad, grad)

    for i in range(max_iter):
        grad_norm = np.sqrt(grad_norm_sq)
        gradient_norms.append(grad_norm)

        if grad_norm < tol:
            return FlowResult(
                trajectory=trajectory,
                energies=energies,
                converged=True,
                iterations=i,
                final_point=U,
                final_energy=energies[-1],
                gradient_norms=gradient_norms
            )

        # Line search
        alpha = _line_search(U, objective, direction)

        # Update
        U_new = qr_retraction(U, alpha * direction)

        # New gradient
        if gradient is not None:
            grad_new = gradient(U_new)
        else:
            grad_new = riemannian_gradient(U_new, objective)

        # Transport direction (simplified)
        direction_transported = tangent_project(U_new, direction)

        # Polak-Ribiere beta
        grad_new_norm_sq = tangent_inner_product(U_new, grad_new, grad_new)
        grad_diff = grad_new - tangent_project(U_new, grad)
        beta = max(0, tangent_inner_product(U_new, grad_new, grad_diff) / grad_norm_sq)

        # New direction
        direction = -grad_new + beta * direction_transported

        U = U_new
        grad = grad_new
        grad_norm_sq = grad_new_norm_sq

        energies.append(objective(U))
        trajectory.append(U.copy())

    return FlowResult(
        trajectory=trajectory,
        energies=energies,
        converged=False,
        iterations=max_iter,
        final_point=U,
        final_energy=energies[-1],
        gradient_norms=gradient_norms
    )


def _trust_region_minimize(
    U0: np.ndarray,
    objective: Callable[[np.ndarray], float],
    gradient: Optional[Callable[[np.ndarray], np.ndarray]],
    tol: float,
    max_iter: int,
    delta: float = 1.0,
    **kwargs
) -> FlowResult:
    """Trust region optimization on Grassmannian."""
    U = U0.copy()
    energies = [objective(U0)]
    trajectory = [U0.copy()]
    gradient_norms = []

    for i in range(max_iter):
        # Gradient
        if gradient is not None:
            grad = gradient(U)
        else:
            grad = riemannian_gradient(U, objective)

        grad_norm = tangent_norm(U, grad)
        gradient_norms.append(grad_norm)

        if grad_norm < tol:
            return FlowResult(
                trajectory=trajectory,
                energies=energies,
                converged=True,
                iterations=i,
                final_point=U,
                final_energy=energies[-1],
                gradient_norms=gradient_norms
            )

        # Trust region step
        step = trust_region_step(U, grad, delta)

        # Trial point
        U_trial = qr_retraction(U, step)
        f_trial = objective(U_trial)

        # Predicted vs actual reduction
        predicted = -tangent_inner_product(U, grad, step)
        actual = energies[-1] - f_trial

        # Adjust trust region
        if actual > 0:
            rho = actual / max(predicted, 1e-14)

            if rho > 0.75:
                delta = min(2 * delta, 10.0)
            elif rho < 0.25:
                delta *= 0.25

            if rho > 0.1:
                U = U_trial
                energies.append(f_trial)
                trajectory.append(U.copy())
            else:
                energies.append(energies[-1])
        else:
            delta *= 0.25
            energies.append(energies[-1])

    return FlowResult(
        trajectory=trajectory,
        energies=energies,
        converged=False,
        iterations=max_iter,
        final_point=U,
        final_energy=energies[-1],
        gradient_norms=gradient_norms
    )


def trust_region_step(
    U: np.ndarray,
    grad: np.ndarray,
    delta: float
) -> np.ndarray:
    """
    Compute trust region step (Cauchy point).

    Parameters
    ----------
    U : ndarray
        Current point
    grad : ndarray
        Riemannian gradient
    delta : float
        Trust region radius

    Returns
    -------
    step : ndarray
        Trust region step
    """
    grad_norm = tangent_norm(U, grad)

    if grad_norm < 1e-14:
        return np.zeros_like(grad)

    # Cauchy point: step in negative gradient direction
    # Clamp to trust region
    step_size = min(delta, grad_norm)
    step = -(step_size / grad_norm) * grad

    return step


def conjugate_gradient_step(
    U: np.ndarray,
    grad: np.ndarray,
    prev_grad: np.ndarray,
    prev_direction: np.ndarray,
    beta_type: str = 'polak_ribiere'
) -> np.ndarray:
    """
    Compute conjugate gradient direction.

    Parameters
    ----------
    U : ndarray
        Current point
    grad : ndarray
        Current gradient
    prev_grad : ndarray
        Previous gradient (transported to U)
    prev_direction : ndarray
        Previous direction (transported to U)
    beta_type : str
        'fletcher_reeves', 'polak_ribiere', 'hestenes_stiefel'

    Returns
    -------
    direction : ndarray
        New search direction
    """
    grad_norm_sq = tangent_inner_product(U, grad, grad)
    prev_grad_norm_sq = tangent_inner_product(U, prev_grad, prev_grad)

    if prev_grad_norm_sq < 1e-14:
        return -grad

    if beta_type == 'fletcher_reeves':
        beta = grad_norm_sq / prev_grad_norm_sq

    elif beta_type == 'polak_ribiere':
        grad_diff = grad - prev_grad
        beta = tangent_inner_product(U, grad, grad_diff) / prev_grad_norm_sq
        beta = max(0, beta)  # Restart if negative

    elif beta_type == 'hestenes_stiefel':
        grad_diff = grad - prev_grad
        denom = tangent_inner_product(U, grad_diff, prev_direction)
        if abs(denom) < 1e-14:
            beta = 0
        else:
            beta = tangent_inner_product(U, grad, grad_diff) / denom

    else:
        raise ValueError(f"Unknown beta type: {beta_type}")

    direction = -grad + beta * prev_direction
    return direction


def _line_search(
    U: np.ndarray,
    objective: Callable[[np.ndarray], float],
    direction: np.ndarray,
    alpha_init: float = 1.0,
    c1: float = 1e-4,
    rho: float = 0.5,
    max_iter: int = 20
) -> float:
    """
    Backtracking line search with Armijo condition.

    Parameters
    ----------
    U : ndarray
        Current point
    objective : callable
        Objective function
    direction : ndarray
        Search direction
    alpha_init : float
        Initial step size
    c1 : float
        Armijo constant
    rho : float
        Backtracking factor
    max_iter : int
        Maximum iterations

    Returns
    -------
    alpha : float
        Accepted step size
    """
    f0 = objective(U)
    grad = riemannian_gradient(U, objective)
    slope = tangent_inner_product(U, grad, direction)

    if slope >= 0:
        # Not a descent direction, use small step
        return 0.01

    alpha = alpha_init

    for _ in range(max_iter):
        U_trial = qr_retraction(U, alpha * direction)
        f_trial = objective(U_trial)

        # Armijo condition
        if f_trial <= f0 + c1 * alpha * slope:
            return alpha

        alpha *= rho

    return alpha
