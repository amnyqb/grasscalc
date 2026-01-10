# grasscalc API Reference

Complete API documentation for the Grassmannian Calculus package.

## Table of Contents

- [Core Module](#core-module)
  - [Linear Algebra](#linear-algebra)
  - [Representations](#representations)
  - [Distances](#distances)
  - [Tangent Space](#tangent-space)
  - [Calculus](#calculus)
  - [Random Sampling](#random-sampling)
- [Layer 1: Within-Manifold Calculus](#layer-1-within-manifold-calculus)
  - [Objective Functions](#objective-functions)
  - [Flows](#flows)
  - [Optimization](#optimization)
- [Layer 2: Between-Manifold Transitions](#layer-2-between-manifold-transitions)
  - [Correspondences](#correspondences)
  - [Sharp Bound Theorem](#sharp-bound-theorem)
  - [Transition Operators](#transition-operators)
  - [Hybrid Evolution](#hybrid-evolution)
  - [Macro Variables](#macro-variables)
- [GCT Module](#gct-module)
  - [Chain Definition](#chain-definition)
  - [Weinberg Angle](#weinberg-angle)
  - [Transitions](#transitions)
  - [Validation](#validation)
  - [Physics Constants](#physics-constants)

---

## Core Module

```python
from grasscalc import core
# or
from grasscalc.core import function_name
```

### Linear Algebra

#### `qr_retraction(Y)`

Retract a matrix to the Grassmannian via QR decomposition.

**Parameters:**
- `Y : ndarray, shape (n, k)` - Matrix to retract

**Returns:**
- `U : ndarray, shape (n, k)` - Orthonormal matrix with U^T U = I_k

**Example:**
```python
from grasscalc.core import qr_retraction
import numpy as np

Y = np.random.randn(7, 3)
U = qr_retraction(Y)
assert np.allclose(U.T @ U, np.eye(3))
```

---

#### `stable_qr(A)`

Numerically stable QR decomposition with column pivoting.

**Parameters:**
- `A : ndarray, shape (n, k)` - Input matrix

**Returns:**
- `Q : ndarray, shape (n, k)` - Orthonormal columns
- `R : ndarray, shape (k, k)` - Upper triangular

---

#### `svd_stable(A, full_matrices=False)`

Stable SVD with handling of near-singular matrices.

**Parameters:**
- `A : ndarray` - Input matrix
- `full_matrices : bool` - Whether to compute full U, V

**Returns:**
- `U, S, Vt` - SVD components

---

#### `gram_schmidt(V)`

Classical Gram-Schmidt orthonormalization.

**Parameters:**
- `V : ndarray, shape (n, k)` - Input vectors as columns

**Returns:**
- `Q : ndarray, shape (n, k)` - Orthonormal vectors

---

### Representations

#### `class GrassmannPoint`

Wrapper class for points on the Grassmannian.

**Attributes:**
- `basis : ndarray, shape (n, k)` - Orthonormal basis
- `k : int` - Subspace dimension
- `n : int` - Ambient dimension

**Methods:**
- `projector() -> ndarray` - Return n x n projector P = U U^T
- `distance_to(other) -> float` - Geodesic distance to another point

---

#### `to_projector(U)`

Convert basis representation to projector.

**Parameters:**
- `U : ndarray, shape (n, k)` - Orthonormal basis

**Returns:**
- `P : ndarray, shape (n, n)` - Projector matrix P = U U^T

---

#### `to_basis(P, k)`

Extract orthonormal basis from projector.

**Parameters:**
- `P : ndarray, shape (n, n)` - Projector matrix
- `k : int` - Rank (subspace dimension)

**Returns:**
- `U : ndarray, shape (n, k)` - Orthonormal basis

---

#### `stabilize(U, n, N)`

Embed subspace into larger ambient space.

**Parameters:**
- `U : ndarray, shape (n, k)` - Original basis
- `n : int` - Original ambient dimension
- `N : int` - Target ambient dimension (N >= n)

**Returns:**
- `U_stab : ndarray, shape (N, k)` - Stabilized basis (zero-padded)

---

### Distances

#### `geodesic_distance(U, V)`

Riemannian geodesic distance on the Grassmannian.

**Parameters:**
- `U : ndarray, shape (n, k)` - First point
- `V : ndarray, shape (n, k)` - Second point

**Returns:**
- `d : float` - Geodesic distance = sqrt(sum of squared principal angles)

**Example:**
```python
from grasscalc.core import geodesic_distance, sample_grassmann

U = sample_grassmann(3, 7)
V = sample_grassmann(3, 7)
d = geodesic_distance(U, V)
print(f"Distance: {d:.4f}")  # Typically 0.5 to 2.5
```

---

#### `chordal_distance_sq(U, V)`

Squared chordal (Frobenius) distance between subspaces.

**Parameters:**
- `U : ndarray, shape (n, k)` - First point
- `V : ndarray, shape (n, k')` - Second point (can have different k)

**Returns:**
- `d2 : float` - ||P_U - P_V||_F^2 / 2 = k - ||U^T V||_F^2

**Note:** For same k, d² ranges from 0 (identical) to k (orthogonal).

---

#### `principal_angles(U, V)`

Principal angles between two subspaces.

**Parameters:**
- `U : ndarray, shape (n, k)` - First subspace
- `V : ndarray, shape (n, k')` - Second subspace

**Returns:**
- `theta : ndarray, shape (min(k, k'),)` - Principal angles in [0, pi/2]

**Example:**
```python
from grasscalc.core import principal_angles
import numpy as np

U = sample_grassmann(3, 7)
V = sample_grassmann(3, 7)
theta = principal_angles(U, V)
print(f"Angles (degrees): {np.rad2deg(theta)}")
```

---

#### `frobenius_distance(U, V)`

Frobenius distance between projectors.

**Parameters:**
- `U, V : ndarray` - Subspace bases

**Returns:**
- `d : float` - ||P_U - P_V||_F

---

### Tangent Space

#### `tangent_project(U, Xi)`

Project a matrix to the tangent space at U.

**Parameters:**
- `U : ndarray, shape (n, k)` - Base point
- `Xi : ndarray, shape (n, k)` - Matrix to project

**Returns:**
- `Xi_tan : ndarray, shape (n, k)` - Tangent vector satisfying U^T Xi_tan = 0

**Example:**
```python
from grasscalc.core import tangent_project, sample_grassmann
import numpy as np

U = sample_grassmann(3, 7)
Xi = np.random.randn(7, 3)
Xi_tan = tangent_project(U, Xi)
assert np.allclose(U.T @ Xi_tan, 0)  # Tangent condition
```

---

#### `tangent_inner_product(U, Xi, Eta)`

Riemannian inner product of tangent vectors.

**Parameters:**
- `U : ndarray, shape (n, k)` - Base point
- `Xi, Eta : ndarray, shape (n, k)` - Tangent vectors at U

**Returns:**
- `ip : float` - tr(Xi^T Eta)

---

#### `tangent_norm(U, Xi)`

Riemannian norm of tangent vector.

**Parameters:**
- `U : ndarray, shape (n, k)` - Base point
- `Xi : ndarray, shape (n, k)` - Tangent vector

**Returns:**
- `norm : float` - ||Xi||_F

---

#### `exponential_map(U, Xi)`

Riemannian exponential map.

**Parameters:**
- `U : ndarray, shape (n, k)` - Base point
- `Xi : ndarray, shape (n, k)` - Tangent vector at U

**Returns:**
- `V : ndarray, shape (n, k)` - Endpoint of geodesic starting at U with velocity Xi

**Example:**
```python
from grasscalc.core.tangent import exponential_map, logarithm_map

# Roundtrip test
Xi = logarithm_map(U, V)
V_recovered = exponential_map(U, Xi)
error = np.linalg.norm(V @ V.T - V_recovered @ V_recovered.T)
# error is ~1e-15 (machine precision)
```

---

#### `logarithm_map(U, V)`

Riemannian logarithm map.

**Parameters:**
- `U : ndarray, shape (n, k)` - Base point
- `V : ndarray, shape (n, k)` - Target point (same k)

**Returns:**
- `Xi : ndarray, shape (n, k)` - Tangent vector at U such that exp_U(Xi) = V

---

#### `geodesic(U, V, t)`

Point on geodesic at parameter t.

**Parameters:**
- `U : ndarray, shape (n, k)` - Start point
- `V : ndarray, shape (n, k)` - End point
- `t : float` - Parameter in [0, 1]

**Returns:**
- `W : ndarray, shape (n, k)` - Point at geodesic(t)

**Example:**
```python
from grasscalc.core.tangent import geodesic
from grasscalc.core import geodesic_distance

midpoint = geodesic(U, V, 0.5)
d_UV = geodesic_distance(U, V)
d_mid = geodesic_distance(U, midpoint)
assert np.isclose(d_mid, d_UV / 2)  # Midpoint property
```

---

#### `parallel_transport(U, V, Xi)`

Parallel transport tangent vector along geodesic.

**Parameters:**
- `U : ndarray, shape (n, k)` - Start point
- `V : ndarray, shape (n, k)` - End point
- `Xi : ndarray, shape (n, k)` - Tangent vector at U

**Returns:**
- `Xi_V : ndarray, shape (n, k)` - Transported vector at V

**Note:** Parallel transport preserves inner products:
`<Xi, Eta>_U = <transport(Xi), transport(Eta)>_V`

---

#### `curvature_tensor(U, X, Y, Z)`

Riemann curvature tensor R(X,Y)Z.

**Parameters:**
- `U : ndarray, shape (n, k)` - Base point
- `X, Y, Z : ndarray, shape (n, k)` - Tangent vectors

**Returns:**
- `R_XYZ : ndarray, shape (n, k)` - Curvature tensor applied to Z

**Properties:**
- Antisymmetric: R(X,Y) = -R(Y,X)

---

#### `sectional_curvature(U, X, Y)`

Sectional curvature K(X, Y).

**Parameters:**
- `U : ndarray, shape (n, k)` - Base point
- `X, Y : ndarray, shape (n, k)` - Orthonormal tangent vectors

**Returns:**
- `K : float` - Sectional curvature in [0, 2] for Grassmannians

---

### Calculus

#### `riemannian_gradient(U, f, eps=1e-6)`

Compute Riemannian gradient of scalar function.

**Parameters:**
- `U : ndarray, shape (n, k)` - Point on Grassmannian
- `f : callable` - Scalar function f: Gr(k,n) -> R
- `eps : float` - Finite difference step size

**Returns:**
- `grad : ndarray, shape (n, k)` - Gradient (tangent vector at U)

**Example:**
```python
from grasscalc.core import riemannian_gradient, chordal_distance_sq

V_target = sample_grassmann(3, 7)
def objective(W):
    return chordal_distance_sq(W, V_target)

grad = riemannian_gradient(U, objective)
# grad points in direction of steepest descent
```

---

#### `riemannian_hessian(U, f, Xi, eps=1e-6)`

Hessian action on tangent vector.

**Parameters:**
- `U : ndarray, shape (n, k)` - Base point
- `f : callable` - Scalar function
- `Xi : ndarray, shape (n, k)` - Tangent vector

**Returns:**
- `Hess_Xi : ndarray, shape (n, k)` - Hessian[f](Xi)

---

#### `directional_derivative(U, f, Xi, eps=1e-6)`

Directional derivative of f along Xi.

**Parameters:**
- `U : ndarray` - Base point
- `f : callable` - Function to differentiate
- `Xi : ndarray` - Direction (tangent vector)

**Returns:**
- `Df_Xi : float` - d/dt f(exp_U(t*Xi))|_{t=0}

---

#### `covariant_derivative(U, vector_field, Xi, eps=1e-6)`

Covariant derivative of vector field along Xi.

**Parameters:**
- `U : ndarray` - Base point
- `vector_field : callable` - Maps Gr(k,n) -> tangent vectors
- `Xi : ndarray` - Direction

**Returns:**
- `nabla_Xi_Y : ndarray` - Covariant derivative (tangent at U)

---

#### `lie_derivative(U, f, vector_field, eps=1e-6)`

Lie derivative of scalar function along vector field.

**Parameters:**
- `U : ndarray` - Base point
- `f : callable` - Scalar function
- `vector_field : callable` - Vector field on Grassmannian

**Returns:**
- `L_Y_f : float` - Lie derivative

---

#### `line_integral(f, curve, t0=0, t1=1, n_points=100)`

Line integral along a curve.

**Parameters:**
- `f : callable` - Scalar function on Grassmannian
- `curve : callable` - Parameterized curve curve(t) -> Gr(k,n)
- `t0, t1 : float` - Parameter range
- `n_points : int` - Number of quadrature points

**Returns:**
- `integral : float` - Integral of f along curve weighted by arc length

**Example:**
```python
from grasscalc.core.calculus import line_integral
from grasscalc.core.tangent import geodesic

def my_curve(t):
    return geodesic(U, V, t)

# Length of geodesic
length = line_integral(lambda W: 1.0, my_curve, 0, 1, 100)
```

---

#### `surface_integral(f, surface, n_points=10)`

Surface integral over parameterized surface.

**Parameters:**
- `f : callable` - Scalar function
- `surface : callable` - surface(u, v) -> Gr(k,n) for u,v in [0,1]
- `n_points : int` - Points per dimension

**Returns:**
- `integral : float`

---

#### `volume_element(U)`

Riemannian volume element at U.

**Parameters:**
- `U : ndarray, shape (n, k)` - Point on Grassmannian

**Returns:**
- `dV : float` - Volume element (constant = 1 for Grassmannian metric)

---

#### `differential_form(degree, components)`

Create a differential form.

**Parameters:**
- `degree : int` - Form degree (0=scalar, 1=1-form, etc.)
- `components : callable` - Component function

**Returns:**
- `omega : DifferentialForm` - Form object

---

#### `exterior_derivative(omega)`

Exterior derivative of a form.

**Parameters:**
- `omega : DifferentialForm` - Input form

**Returns:**
- `d_omega : DifferentialForm` - Exterior derivative

---

#### `wedge_product(alpha, beta)`

Wedge product of forms.

**Parameters:**
- `alpha, beta : DifferentialForm` - Input forms

**Returns:**
- `alpha_wedge_beta : DifferentialForm` - Wedge product

---

### Random Sampling

#### `sample_grassmann(k, n, rng=None)`

Sample uniformly from Gr(k, n).

**Parameters:**
- `k : int` - Subspace dimension
- `n : int` - Ambient dimension
- `rng : numpy.random.Generator, optional` - Random number generator

**Returns:**
- `U : ndarray, shape (n, k)` - Random orthonormal matrix

**Example:**
```python
from grasscalc.core import sample_grassmann
import numpy as np

rng = np.random.default_rng(42)
U = sample_grassmann(3, 7, rng)
```

---

#### `sample_tangent(U, scale=1.0, rng=None)`

Sample random tangent vector at U.

**Parameters:**
- `U : ndarray, shape (n, k)` - Base point
- `scale : float` - Standard deviation
- `rng : Generator, optional` - RNG

**Returns:**
- `Xi : ndarray, shape (n, k)` - Random tangent vector

---

## Layer 1: Within-Manifold Calculus

```python
from grasscalc import layer1
```

### Objective Functions

#### `energy_overlap(U, A)`

Energy function based on matrix overlap.

**Parameters:**
- `U : ndarray, shape (n, k)` - Point
- `A : ndarray, shape (n, n)` - Symmetric matrix

**Returns:**
- `E : float` - tr(U^T A U)

---

#### `rayleigh_quotient(U, A)`

Rayleigh quotient for eigenvalue problems.

**Parameters:**
- `U : ndarray, shape (n, k)` - Subspace
- `A : ndarray, shape (n, n)` - Matrix

**Returns:**
- `R : float` - Rayleigh quotient

---

### Flows

#### `gradient_flow(U, f, dt)`

Single step of gradient flow.

**Parameters:**
- `U : ndarray` - Current point
- `f : callable` - Objective function
- `dt : float` - Step size

**Returns:**
- `U_new : ndarray` - Updated point

---

#### `run_gradient_flow(U, f, n_steps, dt)`

Run gradient flow for multiple steps.

**Parameters:**
- `U : ndarray` - Initial point
- `f : callable` - Objective
- `n_steps : int` - Number of steps
- `dt : float` - Step size

**Returns:**
- `trajectory : list` - List of points
- `values : list` - Function values

---

#### `geodesic_flow(U, Xi, t)`

Flow along geodesic.

**Parameters:**
- `U : ndarray` - Initial point
- `Xi : ndarray` - Initial velocity
- `t : float` - Time

**Returns:**
- `U_t : ndarray` - Point at time t

---

#### `hamiltonian_flow(U, Xi, H, dt)`

Hamiltonian flow step.

**Parameters:**
- `U : ndarray` - Position
- `Xi : ndarray` - Momentum (tangent vector)
- `H : callable` - Hamiltonian function
- `dt : float` - Time step

**Returns:**
- `U_new, Xi_new` - Updated position and momentum

---

### Optimization

#### `minimize_on_grassmann(f, U0, method='gradient', **kwargs)`

Minimize function on Grassmannian.

**Parameters:**
- `f : callable` - Objective function
- `U0 : ndarray` - Initial point
- `method : str` - 'gradient', 'trust_region', or 'cg'
- `**kwargs` - Additional options

**Returns:**
- `result : dict` - Optimization result with keys:
  - `'x'`: Optimal point
  - `'fun'`: Optimal value
  - `'niter'`: Number of iterations
  - `'success'`: Convergence flag

---

#### `trust_region_step(U, f, delta=0.1)`

Trust region optimization step.

**Parameters:**
- `U : ndarray` - Current point
- `f : callable` - Objective
- `delta : float` - Trust region radius

**Returns:**
- `U_new : ndarray` - Updated point
- `actual_reduction : float` - Decrease in objective

---

#### `conjugate_gradient_step(U, f, direction, beta)`

Conjugate gradient step.

**Parameters:**
- `U : ndarray` - Current point
- `f : callable` - Objective
- `direction : ndarray` - Search direction
- `beta : float` - CG parameter

**Returns:**
- `U_new : ndarray` - Updated point
- `new_direction : ndarray` - New search direction

---

## Layer 2: Between-Manifold Transitions

```python
from grasscalc import layer2
```

### Correspondences

#### `raise_k_successors(U, k_new)`

Find successors when increasing k.

**Parameters:**
- `U : ndarray, shape (n, k)` - Current subspace
- `k_new : int` - Target dimension (k_new > k)

**Returns:**
- `successors : list` - List of possible successors in Gr(k_new, n)

---

#### `raise_n_successors(U, n_new)`

Find successors when increasing ambient dimension.

**Parameters:**
- `U : ndarray, shape (n, k)` - Current subspace
- `n_new : int` - Target ambient dimension

**Returns:**
- `V : ndarray, shape (n_new, k)` - Stabilized subspace

---

#### `compose_correspondences(C1, C2)`

Compose two correspondences.

**Parameters:**
- `C1, C2 : callable` - Correspondence functions

**Returns:**
- `C : callable` - Composed correspondence

---

### Sharp Bound Theorem

#### `sharp_bound_check(U, V, N=None, tol=1e-10)`

Verify the Sharp Bound Theorem.

**Parameters:**
- `U : ndarray, shape (n, k)` - First subspace
- `V : ndarray, shape (n', k')` - Second subspace
- `N : int, optional` - Common ambient dimension
- `tol : float` - Tolerance for saturation

**Returns:**
- `result : dict` with keys:
  - `'d2'`: Squared chordal distance
  - `'delta_k'`: |k - k'|
  - `'gap'`: d² - |k - k'|
  - `'saturated'`: Whether gap < tol
  - `'theorem_satisfied'`: Whether gap >= 0

**Example:**
```python
from grasscalc.layer2 import sharp_bound_check
from grasscalc.core import sample_grassmann

U = sample_grassmann(3, 10)
V = sample_grassmann(5, 10)
result = sharp_bound_check(U, V)
print(f"Gap: {result['gap']:.4f}")  # Always >= 0
```

---

#### `sharp_bound_gap(U, V, N=None)`

Compute gap from sharp bound.

**Returns:**
- `gap : float` - d²(U,V) - |k - k'|

---

#### `is_saturated(U, V, N=None, tol=1e-10)`

Check if sharp bound is saturated.

**Returns:**
- `bool` - True if d² = |k - k'| (implies containment)

---

#### `is_containment(U, V, tol=1e-10)`

Check subspace containment.

**Returns:**
- `result : dict` with keys:
  - `'is_contained'`: True if one contains the other
  - `'direction'`: 'U_in_V', 'V_in_U', or 'none'
  - `'residual'`: Quality measure

---

#### `find_optimal_successor(U, k_next, n_next, constraint='containment')`

Find successor achieving sharp bound saturation.

**Parameters:**
- `U : ndarray, shape (n, k)` - Current subspace
- `k_next, n_next : int` - Target dimensions
- `constraint : str` - 'containment' or 'minimal'

**Returns:**
- `W : ndarray, shape (n_next, k_next)` - Optimal successor

---

### Transition Operators

#### `transition_action(U, V, tau=1.0, mu=1.0)`

Compute transition action between subspaces.

**Parameters:**
- `U, V : ndarray` - Source and target subspaces
- `tau : float` - Time parameter
- `mu : float` - Distance weight

**Returns:**
- `J : float` - Action value J = (s - tau)² + mu * d²(U, V)

---

#### `optimal_transition(U, k_new, n_new, tau=1.0, mu=1.0)`

Find optimal transition to new manifold.

**Parameters:**
- `U : ndarray` - Current subspace
- `k_new, n_new : int` - Target dimensions
- `tau, mu : float` - Action parameters

**Returns:**
- `V : ndarray` - Optimal successor
- `J : float` - Optimal action value

---

### Hybrid Evolution

#### `class HybridState`

State for hybrid (flow + transition) evolution.

**Attributes:**
- `U : ndarray` - Current subspace
- `k, n : int` - Current dimensions
- `s : float` - Current stage

---

#### `run_hybrid_chain(U0, stages, dt=0.01)`

Run hybrid evolution through stage sequence.

**Parameters:**
- `U0 : ndarray` - Initial subspace
- `stages : list` - List of (k, n) pairs
- `dt : float` - Flow time step

**Returns:**
- `trajectory : list` - List of HybridState objects

---

### Macro Variables

#### `macro_variables(U, V)`

Compute macro variables for transition.

**Parameters:**
- `U, V : ndarray` - Source and target

**Returns:**
- `result : dict` with keys:
  - `'distance'`: Geodesic distance
  - `'dimension_gap'`: |k' - k|
  - `'codimension'`: Changes in n - k

---

#### `grassmann_dimension(k, n)`

Dimension of Gr(k, n).

**Returns:**
- `D : int` - k(n - k)

---

#### `codimension(k, n)`

Codimension in ambient space.

**Returns:**
- `c : int` - n - k

---

## GCT Module

```python
from grasscalc import gct
```

### Chain Definition

#### `GCT_CHAIN`

The canonical seven-manifold chain.

```python
GCT_CHAIN = [
    (2, 5),   # Gr(2,5):  D=6   - Takens-minimal seed
    (3, 5),   # Gr(3,5):  D=6   - Complex structure
    (3, 7),   # Gr(3,7):  D=12  - Quaternionic
    (3, 16),  # Gr(3,16): D=39  - Electroweak (Weinberg)
    (7, 18),  # Gr(7,18): D=77  - Octonionic bridge
    (8, 24),  # Gr(8,24): D=128 - E8 half-spinor
    (10, 34), # Gr(10,34): D=240 - E8 roots
]
```

---

#### `gct_dimension(k, n)`

Grassmannian dimension.

**Returns:**
- `D : int` - k(n - k)

---

#### `gct_total_dimension(chain=None)`

Sum of dimensions in chain.

**Parameters:**
- `chain : list, optional` - Chain (default: GCT_CHAIN)

**Returns:**
- `total : int` - 508 for GCT_CHAIN

---

#### `gct_manifolds()`

Detailed information about each manifold.

**Returns:**
- `list of dict` - Each with keys: stage, k, n, D, codimension, name, grassmannian

---

### Weinberg Angle

#### `weinberg_angle(k=3, n=16)`

Compute Weinberg angle from Grassmannian.

**Parameters:**
- `k, n : int` - Grassmannian parameters (default: electroweak stage)

**Returns:**
- `sin2_theta : float` - sin²(theta_W) = k / (n - k)

**Example:**
```python
from grasscalc.gct import weinberg_angle

sin2_theta = weinberg_angle()  # 3/13 = 0.23077
print(f"sin²(theta_W) = {sin2_theta:.5f}")
```

---

#### `weinberg_angle_experimental()`

Experimental value of Weinberg angle.

**Returns:**
- `sin2_theta : float` - 0.23122 (PDG 2024)

---

#### `weinberg_error()`

Relative error of GCT prediction.

**Returns:**
- `error : float` - |predicted - experimental| / experimental

---

### Transitions

#### `T0, T1, T2, T3, T4, T5`

GCT transition operators between stages.

```python
from grasscalc.gct import T0, T1, T2

# T0: Gr(2,5) -> Gr(3,5)
# T1: Gr(3,5) -> Gr(3,7)
# etc.
```

---

#### `gct_transition_operators()`

Get all transition operators.

**Returns:**
- `list` - [T0, T1, T2, T3, T4, T5]

---

### Validation

#### `verify_gct_dimensions()`

Verify GCT dimension predictions.

**Returns:**
- `result : dict` with keys:
  - `'correct'`: All dimensions match
  - `'computed'`: List of computed dimensions
  - `'expected'`: List of expected dimensions
  - `'total'`: Total dimension
  - `'gauge'`: Gauge dimension (496)
  - `'gravity'`: Gravity dimension (12)

---

#### `verify_gct_chain()`

Complete validation of GCT chain.

**Returns:**
- `result : dict` - Comprehensive validation results

---

#### `run_gct_tests()`

Run all GCT validation tests.

**Returns:**
- `passed : bool` - All tests passed
- `results : dict` - Individual test results

---

### Physics Constants

#### `DIVISION_ALGEBRAS`

Hurwitz division algebras.

```python
DIVISION_ALGEBRAS = {
    'R': {'dim': 1, 'name': 'Real'},
    'C': {'dim': 2, 'name': 'Complex'},
    'H': {'dim': 4, 'name': 'Quaternion'},
    'O': {'dim': 8, 'name': 'Octonion'},
}
```

---

#### `division_algebra_map(k, n)`

Map Grassmannian to division algebra.

**Returns:**
- `algebra : str` - 'R', 'C', 'H', or 'O'

---

#### `hurwitz_dimensions()`

Hurwitz theorem dimensions.

**Returns:**
- `list` - [1, 2, 4, 8]

---

## Constants

### Key Dimensions

```python
TOTAL_DIMENSION = 508      # Total GCT chain dimension
GAUGE_DIMENSION = 496      # E8 x E8 dimension
GRAVITY_DIMENSION = 12     # Leftover for gravity
E8_ROOT_DIMENSION = 240    # E8 root system
E8_HALFSPINOR_DIMENSION = 128  # E8 half-spinor
```

### Physical Constants

```python
WEINBERG_ANGLE_GCT = 3/13  # = 0.230769...
WEINBERG_ANGLE_EXP = 0.23122  # PDG 2024
```
