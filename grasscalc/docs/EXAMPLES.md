# grasscalc Examples

Practical examples demonstrating the grasscalc package capabilities.

## Table of Contents

1. [Basic Operations](#basic-operations)
2. [Geodesics and Distances](#geodesics-and-distances)
3. [Calculus Operations](#calculus-operations)
4. [Optimization](#optimization)
5. [Sharp Bound Theorem](#sharp-bound-theorem)
6. [GCT Applications](#gct-applications)
7. [Integration](#integration)
8. [Advanced Topics](#advanced-topics)

---

## Basic Operations

### Creating Points on the Grassmannian

```python
import numpy as np
from grasscalc.core import sample_grassmann, qr_retraction

# Method 1: Random sampling (uniform distribution)
U = sample_grassmann(k=3, n=7)
print(f"Shape: {U.shape}")  # (7, 3)
print(f"Orthonormal: {np.allclose(U.T @ U, np.eye(3))}")  # True

# Method 2: From any matrix via QR retraction
A = np.random.randn(7, 3)
V = qr_retraction(A)

# Method 3: Deterministic construction (e.g., first k standard basis vectors)
I = np.eye(7)
W = I[:, :3]  # First 3 columns
```

### Representations and Conversions

```python
from grasscalc.core import to_projector, to_basis, stabilize

# Basis to projector
U = sample_grassmann(3, 7)
P = to_projector(U)
print(f"P shape: {P.shape}")  # (7, 7)
print(f"P² = P: {np.allclose(P @ P, P)}")  # True

# Projector to basis
U_recovered = to_basis(P, k=3)
print(f"Same subspace: {np.allclose(U @ U.T, U_recovered @ U_recovered.T)}")

# Stabilize to larger ambient space
U_stab = stabilize(U, n=7, N=10)
print(f"Stabilized shape: {U_stab.shape}")  # (10, 3)
```

---

## Geodesics and Distances

### Computing Distances

```python
from grasscalc.core import geodesic_distance, chordal_distance_sq, principal_angles

U = sample_grassmann(3, 7)
V = sample_grassmann(3, 7)

# Geodesic (Riemannian) distance
d_geo = geodesic_distance(U, V)
print(f"Geodesic distance: {d_geo:.4f}")

# Chordal distance (squared)
d2_chord = chordal_distance_sq(U, V)
print(f"Chordal distance²: {d2_chord:.4f}")

# Principal angles
theta = principal_angles(U, V)
print(f"Principal angles (deg): {np.rad2deg(theta)}")

# Relationship: geodesic = sqrt(sum of squared angles)
print(f"Verification: {np.isclose(d_geo, np.linalg.norm(theta))}")
```

### Geodesic Interpolation

```python
from grasscalc.core.tangent import geodesic, logarithm_map, exponential_map
import matplotlib.pyplot as plt

U = sample_grassmann(3, 7)
V = sample_grassmann(3, 7)

# Points along geodesic
t_values = np.linspace(0, 1, 11)
distances = []

for t in t_values:
    W = geodesic(U, V, t)
    d = geodesic_distance(U, W)
    distances.append(d)

# Plot: distance increases linearly
plt.plot(t_values, distances, 'o-')
plt.xlabel('t')
plt.ylabel('d(U, γ(t))')
plt.title('Geodesic Parameterization')
plt.show()
```

### Exponential and Logarithm Maps

```python
from grasscalc.core.tangent import exponential_map, logarithm_map
from grasscalc.core import tangent_project

U = sample_grassmann(3, 7)
V = sample_grassmann(3, 7)

# Log: find tangent vector connecting U to V
Xi = logarithm_map(U, V)
print(f"Xi is tangent: {np.allclose(U.T @ Xi, 0)}")

# Exp: move from U along Xi
V_recovered = exponential_map(U, Xi)

# Roundtrip test
error = np.linalg.norm(V @ V.T - V_recovered @ V_recovered.T, 'fro')
print(f"Roundtrip error: {error:.2e}")  # ~1e-15

# Create your own tangent vector
Xi_custom = np.random.randn(7, 3)
Xi_custom = tangent_project(U, Xi_custom)
Xi_custom = Xi_custom / np.linalg.norm(Xi_custom) * 0.5  # Normalize

W = exponential_map(U, Xi_custom)
print(f"Moved to new point at distance: {geodesic_distance(U, W):.4f}")
```

---

## Calculus Operations

### Riemannian Gradient

```python
from grasscalc.core import riemannian_gradient, chordal_distance_sq
from grasscalc.core.tangent import exponential_map, is_tangent

# Define target
V_target = sample_grassmann(3, 7)

# Objective: distance to target
def objective(W):
    return chordal_distance_sq(W, V_target)

# Compute gradient
U = sample_grassmann(3, 7)
grad = riemannian_gradient(U, objective)

# Verify it's a tangent vector
print(f"Gradient is tangent: {is_tangent(U, grad)}")

# Gradient descent step
step_size = 0.1
U_new = exponential_map(U, -step_size * grad)

print(f"Before: {objective(U):.4f}")
print(f"After:  {objective(U_new):.4f}")
print(f"Decreased: {objective(U_new) < objective(U)}")
```

### Covariant Derivative

```python
from grasscalc.core.calculus import covariant_derivative
from grasscalc.core import tangent_project

U = sample_grassmann(3, 7)

# Define a vector field
def vector_field(W):
    # Example: constant direction projected to tangent space
    direction = np.ones((7, 3))
    return tangent_project(W, direction)

# Compute covariant derivative along Xi
Xi = tangent_project(U, np.random.randn(7, 3))
nabla_Xi_Y = covariant_derivative(U, vector_field, Xi)

print(f"Covariant derivative is tangent: {is_tangent(U, nabla_Xi_Y)}")
```

### Curvature

```python
from grasscalc.core.tangent import curvature_tensor, sectional_curvature

U = sample_grassmann(3, 7)

# Create orthonormal tangent vectors
Xi = tangent_project(U, np.random.randn(7, 3))
Xi = Xi / np.linalg.norm(Xi, 'fro')

Eta = tangent_project(U, np.random.randn(7, 3))
Eta = Eta - Xi * np.trace(Xi.T @ Eta)  # Orthogonalize
Eta = Eta / np.linalg.norm(Eta, 'fro')

Zeta = tangent_project(U, np.random.randn(7, 3))

# Curvature tensor
R_XY_Z = curvature_tensor(U, Xi, Eta, Zeta)
print(f"R(X,Y)Z norm: {np.linalg.norm(R_XY_Z, 'fro'):.4f}")

# Verify antisymmetry
R_YX_Z = curvature_tensor(U, Eta, Xi, Zeta)
print(f"R(X,Y) = -R(Y,X): {np.allclose(R_XY_Z, -R_YX_Z)}")

# Sectional curvature (always in [0, 2] for Grassmannians)
K = sectional_curvature(U, Xi, Eta)
print(f"Sectional curvature K = {K:.4f}")
print(f"K in [0, 2]: {0 <= K <= 2}")
```

### Parallel Transport

```python
from grasscalc.core.tangent import parallel_transport, tangent_inner_product

U = sample_grassmann(3, 7)
V = sample_grassmann(3, 7)

# Create two tangent vectors at U
Xi = tangent_project(U, np.random.randn(7, 3))
Eta = tangent_project(U, np.random.randn(7, 3))

# Inner product at U
ip_U = tangent_inner_product(U, Xi, Eta)

# Transport to V
Xi_V = parallel_transport(U, V, Xi)
Eta_V = parallel_transport(U, V, Eta)

# Inner product at V (should be preserved)
ip_V = tangent_inner_product(V, Xi_V, Eta_V)

print(f"Inner product at U: {ip_U:.4f}")
print(f"Inner product at V: {ip_V:.4f}")
print(f"Preserved: {np.isclose(ip_U, ip_V)}")
```

---

## Optimization

### Gradient Descent

```python
from grasscalc.layer1 import run_gradient_flow

# Objective: minimize distance to target
target = sample_grassmann(3, 7)
def f(U):
    return chordal_distance_sq(U, target)

# Initial point
U0 = sample_grassmann(3, 7)

# Run gradient flow
trajectory, values = run_gradient_flow(U0, f, n_steps=100, dt=0.1)

print(f"Initial value: {values[0]:.4f}")
print(f"Final value:   {values[-1]:.4f}")

# Plot convergence
import matplotlib.pyplot as plt
plt.semilogy(values)
plt.xlabel('Iteration')
plt.ylabel('Objective')
plt.title('Gradient Flow Convergence')
plt.show()
```

### Rayleigh Quotient Optimization

```python
from grasscalc.layer1 import minimize_on_grassmann, rayleigh_quotient

# Find dominant eigenspace of a matrix
n, k = 10, 3
A = np.random.randn(n, n)
A = A + A.T  # Symmetric

# Minimize negative Rayleigh quotient (= maximize eigenvalues)
def objective(U):
    return -rayleigh_quotient(U, A)

U0 = sample_grassmann(k, n)
result = minimize_on_grassmann(objective, U0, method='gradient', n_steps=200, dt=0.05)

print(f"Converged: {result['success']}")
print(f"Final Rayleigh quotient: {-result['fun']:.4f}")

# Compare to true eigenvalues
eigvals = np.linalg.eigvalsh(A)
print(f"Top {k} eigenvalues: {eigvals[-k:][::-1]}")
```

---

## Sharp Bound Theorem

### Basic Verification

```python
from grasscalc.layer2 import sharp_bound_check, sharp_bound_gap

# Create subspaces of different dimensions
U = sample_grassmann(3, 10)  # k=3
V = sample_grassmann(5, 10)  # k=5

result = sharp_bound_check(U, V)

print("Sharp Bound Theorem Check:")
print(f"  d²(U, V) = {result['d2']:.4f}")
print(f"  |k - k'| = {result['delta_k']}")
print(f"  Gap      = {result['gap']:.4f}")
print(f"  Theorem satisfied: {result['theorem_satisfied']}")
```

### Testing Saturation (Containment)

```python
from grasscalc.layer2 import is_saturated, is_containment, find_optimal_successor

# Start with a 3-plane
U = sample_grassmann(3, 10)

# Find optimal successor achieving saturation
V = find_optimal_successor(U, k_next=5, n_next=10)

# Check saturation
saturated = is_saturated(U, V)
containment = is_containment(U, V)

print(f"Saturated: {saturated}")  # True
print(f"Containment: {containment['direction']}")  # 'U_in_V'
print(f"Gap: {sharp_bound_gap(U, V):.2e}")  # ~0
```

### Statistical Verification

```python
# Verify theorem over many random pairs
n_trials = 100
gaps = []

for _ in range(n_trials):
    k1 = np.random.randint(2, 6)
    k2 = np.random.randint(2, 6)
    n = 10

    U = sample_grassmann(k1, n)
    V = sample_grassmann(k2, n)

    gap = sharp_bound_gap(U, V, N=n)
    gaps.append(gap)

print(f"Minimum gap: {min(gaps):.6f}")
print(f"All non-negative: {all(g >= -1e-10 for g in gaps)}")
print(f"Mean gap: {np.mean(gaps):.4f}")
```

---

## GCT Applications

### Weinberg Angle Derivation

```python
from grasscalc.gct import (
    weinberg_angle, weinberg_angle_experimental, weinberg_error,
    GCT_CHAIN, gct_manifolds
)

# GCT prediction for Weinberg angle
sin2_theta = weinberg_angle()  # From Gr(3, 16)
sin2_exp = weinberg_angle_experimental()
error = weinberg_error()

print("Weinberg Angle from GCT:")
print(f"  sin²θ_W (theory) = 3/13 = {sin2_theta:.6f}")
print(f"  sin²θ_W (exp.)   = {sin2_exp:.6f}")
print(f"  Relative error   = {error*100:.2f}%")
```

### Seven-Manifold Chain

```python
from grasscalc.gct import gct_total_dimension, gct_manifolds

# Display the chain
manifolds = gct_manifolds()

print("GCT Seven-Manifold Chain:")
print("-" * 55)
print(f"{'Stage':<6} {'Gr(k,n)':<12} {'D':<8} {'Role':<25}")
print("-" * 55)

for m in manifolds:
    print(f"{m['stage']:<6} {m['grassmannian']:<12} {m['D']:<8} {m['name']:<25}")

print("-" * 55)
total = gct_total_dimension()
print(f"{'Total':<6} {'':<12} {total:<8} 496 (gauge) + 12 (gravity)")
```

### Validate GCT Predictions

```python
from grasscalc.gct import verify_gct_chain, run_gct_tests

# Run validation
result = verify_gct_chain()

print("GCT Validation Results:")
print(f"  Dimensions correct: {result['dimensions_correct']}")
print(f"  Total dimension: {result['total']} (expected 508)")
print(f"  Gauge component: {result['gauge']} (expected 496)")
print(f"  Gravity component: {result['gravity']} (expected 12)")

# Run full test suite
passed, details = run_gct_tests()
print(f"\nAll tests passed: {passed}")
```

---

## Integration

### Line Integrals

```python
from grasscalc.core.calculus import line_integral
from grasscalc.core.tangent import geodesic
from grasscalc.core import geodesic_distance

U = sample_grassmann(3, 7)
V = sample_grassmann(3, 7)

# Define curve: geodesic from U to V
def curve(t):
    return geodesic(U, V, t)

# Integrate constant 1 -> arc length
arc_length = line_integral(lambda W: 1.0, curve, t0=0, t1=1, n_points=100)
true_distance = geodesic_distance(U, V)

print(f"Arc length:        {arc_length:.6f}")
print(f"Geodesic distance: {true_distance:.6f}")
print(f"Match: {np.isclose(arc_length, true_distance)}")

# Integrate a non-trivial function
target = sample_grassmann(3, 7)
def distance_to_target(W):
    return geodesic_distance(W, target)

integral = line_integral(distance_to_target, curve, t0=0, t1=1, n_points=100)
print(f"Integral of distance: {integral:.4f}")
```

### Integration Along Geodesic

```python
from grasscalc.core.calculus import integrate_over_geodesic

# Alternative method using integrate_over_geodesic
result = integrate_over_geodesic(
    U, V,
    integrand=lambda W: 1.0,
    n_points=100
)
print(f"Geodesic length: {result:.6f}")
```

---

## Advanced Topics

### Working with Different Metrics

```python
# The standard metric is the Frobenius inner product
# Custom metrics can be implemented by modifying gradient computations

from grasscalc.core import tangent_project

def weighted_inner_product(U, Xi, Eta, weights):
    """Weighted inner product with diagonal weights."""
    W_Xi = Xi * weights.reshape(-1, 1)  # Weight rows
    return np.trace(W_Xi.T @ Eta)

# Example: emphasize certain dimensions
weights = np.ones(7)
weights[:3] = 2.0  # Double weight on first 3 dimensions

U = sample_grassmann(3, 7)
Xi = tangent_project(U, np.random.randn(7, 3))
Eta = tangent_project(U, np.random.randn(7, 3))

standard_ip = tangent_inner_product(U, Xi, Eta)
weighted_ip = weighted_inner_product(U, Xi, Eta, weights)

print(f"Standard inner product: {standard_ip:.4f}")
print(f"Weighted inner product: {weighted_ip:.4f}")
```

### Batch Operations

```python
# Process multiple points efficiently
n_points = 100

# Sample many points
points = [sample_grassmann(3, 7) for _ in range(n_points)]

# Compute pairwise distances (upper triangle)
distances = np.zeros((n_points, n_points))
for i in range(n_points):
    for j in range(i+1, n_points):
        d = geodesic_distance(points[i], points[j])
        distances[i, j] = d
        distances[j, i] = d

print(f"Mean distance: {np.mean(distances[distances > 0]):.4f}")
print(f"Max distance:  {np.max(distances):.4f}")
```

### Custom Objective Functions

```python
from grasscalc.core import riemannian_gradient
from grasscalc.core.tangent import exponential_map

# Example: sum of distances to multiple targets
targets = [sample_grassmann(3, 7) for _ in range(5)]

def multi_target_objective(U):
    return sum(chordal_distance_sq(U, t) for t in targets)

# Find point minimizing sum of distances (geometric median approximation)
U = sample_grassmann(3, 7)
for i in range(50):
    grad = riemannian_gradient(U, multi_target_objective)
    U = exponential_map(U, -0.1 * grad)

print(f"Final objective: {multi_target_objective(U):.4f}")

# Distances to each target
for i, t in enumerate(targets):
    print(f"  Distance to target {i}: {geodesic_distance(U, t):.4f}")
```

### Visualization

```python
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# For Gr(1, 3) = RP^2, we can visualize in 3D
# (projective plane embedded in S^2)

n_samples = 500
points_3d = []

for _ in range(n_samples):
    U = sample_grassmann(1, 3)
    # Normalize to unit sphere (for visualization)
    v = U.flatten()
    points_3d.append(v)

points_3d = np.array(points_3d)

fig = plt.figure(figsize=(8, 8))
ax = fig.add_subplot(111, projection='3d')
ax.scatter(points_3d[:, 0], points_3d[:, 1], points_3d[:, 2],
           alpha=0.3, s=10)
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title('Random points on Gr(1,3) ≅ RP²')
plt.show()
```

---

## Performance Tips

### Efficient Distance Computations

```python
# For repeated distance computations, cache projectors
U_proj = U @ U.T  # Compute once

def fast_chordal_sq(V):
    """Fast chordal distance using cached projector."""
    V_proj = V @ V.T
    return np.linalg.norm(U_proj - V_proj, 'fro')**2 / 2
```

### Vectorized Operations

```python
# Use NumPy broadcasting for tangent space operations
def batch_tangent_project(U, matrices):
    """Project multiple matrices to tangent space at U."""
    # matrices: shape (m, n, k)
    UtU = U.T @ U  # k x k
    return matrices - U @ (U.T @ matrices)  # Broadcasting
```

### Memory-Efficient Sampling

```python
# Generator for memory-efficient random point iteration
def grassmann_generator(k, n, rng=None):
    """Yield random Grassmannian points one at a time."""
    if rng is None:
        rng = np.random.default_rng()
    while True:
        A = rng.standard_normal((n, k))
        Q, _ = np.linalg.qr(A)
        yield Q

# Use with iteration
gen = grassmann_generator(3, 7)
for i, U in enumerate(gen):
    if i >= 10:
        break
    print(f"Point {i}: shape {U.shape}")
```
