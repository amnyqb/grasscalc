# grasscalc

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://img.shields.io/badge/pypi-v0.1.0-blue)](https://pypi.org/project/grasscalc/)

**Grassmannian Calculus** - A Python package for differential calculus on Grassmannian manifolds with applications to theoretical physics.

## Overview

`grasscalc` provides a complete framework for performing calculus operations on Grassmannian manifolds Gr(k,n) - the space of k-dimensional linear subspaces of R^n. The package implements:

- **Layer 1**: Within-manifold calculus (differentiation, integration, geodesic flows)
- **Layer 2**: Between-manifold transition calculus (correspondences, Sharp Bound Theorem)
- **GCT Module**: Grassmannian Cosmological Theory - deriving Standard Model parameters from geometry

## Key Features

### Riemannian Geometry
- Geodesic distance, chordal distance, principal angles
- Exponential and logarithm maps (with machine-precision roundtrip)
- Parallel transport preserving inner products
- Curvature tensor and sectional curvature

### Calculus Operations
- Riemannian gradient and Hessian
- Covariant derivatives
- Directional and partial derivatives
- Lie derivatives

### Integration
- Line integrals along geodesics
- Surface integrals
- Volume elements
- Differential forms (exterior derivative, wedge product)

### Optimization
- Gradient descent on Grassmannians
- Trust region methods
- Conjugate gradient
- Hamiltonian and geodesic flows

### Sharp Bound Theorem
A novel mathematical result (Al Yaquob, 2026):

> For V in Gr(k,n) and W in Gr(k',n'):  **d²(V, W) >= |k - k'|**
>
> with equality if and only if one subspace contains the other.

### GCT: Physics from Geometry
The package implements the seven-manifold chain that derives fundamental physics:

```
Gr(2,5) -> Gr(3,5) -> Gr(3,7) -> Gr(3,16) -> Gr(7,18) -> Gr(8,24) -> Gr(10,34)
```

**Key predictions:**
- **Weinberg angle**: sin²(theta_W) = 3/13 = 0.23077 (from Gr(3,16), 0.33% error)
- **Total dimension**: 508 = 496 (gauge) + 12 (gravity)
- **E8 x E8**: Emerges from dimensions 240 + 128 + 128

## Installation

### From PyPI (recommended)
```bash
pip install grasscalc
```

### From source
```bash
git clone https://github.com/alyaquob/physica.git
cd physica/grasscalc
pip install -e .
```

### With optional dependencies
```bash
# Visualization support
pip install grasscalc[viz]

# Development tools
pip install grasscalc[dev]

# Full installation (including geomstats, pymanopt, torch)
pip install grasscalc[full]
```

## Quick Start

### Basic Grassmannian Operations

```python
import numpy as np
from grasscalc.core import sample_grassmann, geodesic_distance, tangent_project

# Sample random points on Gr(3, 7)
U = sample_grassmann(k=3, n=7)
V = sample_grassmann(k=3, n=7)

# Compute geodesic distance
d = geodesic_distance(U, V)
print(f"Geodesic distance: {d:.4f}")

# Project to tangent space
Xi = np.random.randn(7, 3)
Xi_tangent = tangent_project(U, Xi)
print(f"Is tangent: {np.allclose(U.T @ Xi_tangent, 0)}")  # True
```

### Exponential and Logarithm Maps

```python
from grasscalc.core.tangent import exponential_map, logarithm_map, geodesic

# Logarithm: find tangent vector from U to V
Xi = logarithm_map(U, V)

# Exponential: move from U along tangent vector
V_recovered = exponential_map(U, Xi)

# Verify roundtrip (machine precision)
error = np.linalg.norm(V @ V.T - V_recovered @ V_recovered.T, 'fro')
print(f"Roundtrip error: {error:.2e}")  # ~1e-15

# Geodesic interpolation
midpoint = geodesic(U, V, t=0.5)
```

### Calculus Operations

```python
from grasscalc.core import riemannian_gradient, chordal_distance_sq
from grasscalc.core.tangent import exponential_map

# Define objective: squared distance to target
V_target = sample_grassmann(k=3, n=7)
def objective(W):
    return chordal_distance_sq(W, V_target)

# Compute Riemannian gradient
grad = riemannian_gradient(U, objective)

# Gradient descent step
step_size = 0.1
U_new = exponential_map(U, -step_size * grad)

print(f"Objective decreased: {objective(U_new) < objective(U)}")  # True
```

### Sharp Bound Theorem

```python
from grasscalc.layer2 import sharp_bound_check, is_saturated

# Check sharp bound for subspaces of different dimensions
U = sample_grassmann(k=3, n=10)
V = sample_grassmann(k=5, n=10)

result = sharp_bound_check(U, V)
print(f"d² = {result['d2']:.4f}")
print(f"|k - k'| = {result['delta_k']}")
print(f"Gap = {result['gap']:.4f}")
print(f"Theorem satisfied: {result['theorem_satisfied']}")  # Always True
```

### GCT: Deriving the Weinberg Angle

```python
from grasscalc.gct import weinberg_angle, GCT_CHAIN, gct_total_dimension

# The Weinberg angle emerges from Gr(3, 16)
sin2_theta = weinberg_angle()
print(f"sin²(theta_W) = {sin2_theta:.5f}")  # 0.23077
print(f"Exact value: 3/13 = {3/13:.5f}")

# Total dimension of the GCT chain
print(f"Total dimension: {gct_total_dimension()}")  # 508
print("= 496 (gauge) + 12 (gravity)")

# The seven-manifold chain
for k, n in GCT_CHAIN:
    D = k * (n - k)
    print(f"Gr({k},{n}): D = {D}")
```

### Parallel Transport

```python
from grasscalc.core.tangent import parallel_transport, tangent_inner_product

# Transport tangent vectors from U to V
Xi = tangent_project(U, np.random.randn(7, 3))
Eta = tangent_project(U, np.random.randn(7, 3))

# Inner product at U
ip_before = tangent_inner_product(U, Xi, Eta)

# Transport to V
Xi_V = parallel_transport(U, V, Xi)
Eta_V = parallel_transport(U, V, Eta)

# Inner product preserved (machine precision)
ip_after = tangent_inner_product(V, Xi_V, Eta_V)
print(f"Inner product preserved: {np.isclose(ip_before, ip_after)}")  # True
```

### Line Integrals

```python
from grasscalc.core.calculus import line_integral
from grasscalc.core.tangent import geodesic

# Integrate constant function 1 along geodesic
def curve(t):
    return geodesic(U, V, t)

length = line_integral(lambda W: 1.0, curve, t0=0, t1=1, n_points=100)
d = geodesic_distance(U, V)
print(f"Length equals geodesic distance: {np.isclose(length, d)}")  # True
```

## Package Structure

```
grasscalc/
├── __init__.py          # Package entry point
├── core/                # Core geometry operations
│   ├── linalg.py        # QR, SVD, Gram-Schmidt
│   ├── representations.py # Point representations
│   ├── distances.py     # Distance metrics
│   ├── tangent.py       # Tangent space, exp/log maps
│   ├── calculus.py      # Derivatives, integrals, forms
│   └── random.py        # Random sampling
├── layer1/              # Within-manifold calculus
│   ├── objectives.py    # Objective functions
│   ├── flows.py         # Gradient/geodesic flows
│   └── optim.py         # Optimization algorithms
├── layer2/              # Between-manifold transitions
│   ├── correspondences.py # Raise-k, raise-n
│   ├── sharp_bound.py   # Sharp Bound Theorem
│   ├── transition_action.py # Transition operators
│   ├── operators.py     # Min-plus operators
│   ├── hybrid.py        # Hybrid evolution
│   └── macro.py         # Macro variables
├── gct/                 # Grassmannian Cosmological Theory
│   ├── chain.py         # Seven-manifold chain
│   ├── weinberg.py      # Weinberg angle
│   ├── transitions.py   # GCT transition operators
│   ├── validation.py    # Theory validation
│   └── physics.py       # Division algebras
└── tests/               # Test suite
    ├── test_core.py
    └── test_gct.py
```

## GCT Chain

| Stage | Manifold | Dimension | Role |
|-------|----------|-----------|------|
| 0 | Gr(2,5) | 6 | Takens-minimal seed |
| 1 | Gr(3,5) | 6 | Complex structure |
| 2 | Gr(3,7) | 12 | Quaternionic |
| 3 | Gr(3,16) | 39 | Electroweak (Weinberg angle) |
| 4 | Gr(7,18) | 77 | Octonionic bridge |
| 5 | Gr(8,24) | 128 | E8 half-spinor |
| 6 | Gr(10,34) | 240 | E8 roots |
| **Total** | | **508** | **496 (gauge) + 12 (gravity)** |

## API Reference

### Core Module (`grasscalc.core`)

#### Distances
| Function | Description |
|----------|-------------|
| `geodesic_distance(U, V)` | Riemannian geodesic distance |
| `chordal_distance_sq(U, V)` | Squared chordal (Frobenius) distance |
| `principal_angles(U, V)` | Principal angles between subspaces |
| `frobenius_distance(U, V)` | Frobenius distance between projectors |

#### Tangent Space
| Function | Description |
|----------|-------------|
| `tangent_project(U, Xi)` | Project to tangent space at U |
| `exponential_map(U, Xi)` | Riemannian exponential map |
| `logarithm_map(U, V)` | Riemannian logarithm map |
| `geodesic(U, V, t)` | Point on geodesic at parameter t |
| `parallel_transport(U, V, Xi)` | Transport tangent vector |
| `curvature_tensor(U, X, Y, Z)` | Riemann curvature R(X,Y)Z |
| `sectional_curvature(U, X, Y)` | Sectional curvature K(X,Y) |

#### Calculus
| Function | Description |
|----------|-------------|
| `riemannian_gradient(U, f)` | Gradient of scalar function |
| `riemannian_hessian(U, f, Xi)` | Hessian action on tangent |
| `covariant_derivative(U, Y, Xi)` | Covariant derivative |
| `directional_derivative(U, f, Xi)` | Directional derivative |
| `line_integral(f, curve, t0, t1)` | Integral along curve |
| `exterior_derivative(omega)` | Exterior derivative |
| `wedge_product(alpha, beta)` | Wedge product |

#### Random Sampling
| Function | Description |
|----------|-------------|
| `sample_grassmann(k, n)` | Uniform random point on Gr(k,n) |
| `sample_tangent(U, scale)` | Random tangent vector at U |

### Layer 1 (`grasscalc.layer1`)

| Function | Description |
|----------|-------------|
| `gradient_flow(U, f, dt)` | Single gradient flow step |
| `run_gradient_flow(U, f, steps)` | Run gradient flow |
| `minimize_on_grassmann(f, U0)` | Minimize function on manifold |
| `trust_region_step(U, f)` | Trust region optimization step |
| `conjugate_gradient_step(U, f, ...)` | CG optimization step |

### Layer 2 (`grasscalc.layer2`)

| Function | Description |
|----------|-------------|
| `sharp_bound_check(U, V)` | Verify Sharp Bound Theorem |
| `sharp_bound_gap(U, V)` | Gap from sharp bound |
| `is_saturated(U, V)` | Check bound saturation |
| `is_containment(U, V)` | Check subspace containment |
| `raise_k_successors(U, k')` | Correspondences for k->k' |
| `transition_action(U, V)` | Compute transition action |

### GCT Module (`grasscalc.gct`)

| Object | Description |
|--------|-------------|
| `GCT_CHAIN` | The seven-manifold chain [(2,5), ..., (10,34)] |
| `gct_dimension(k, n)` | Dimension k(n-k) |
| `gct_total_dimension()` | Total = 508 |
| `weinberg_angle()` | sin²(theta_W) = 3/13 |
| `weinberg_error()` | Error vs experimental value |
| `T0, T1, ..., T5` | Transition operators |
| `verify_gct_chain()` | Validate GCT predictions |

## Mathematical Background

### Grassmannian Manifold

The Grassmannian Gr(k,n) is the set of all k-dimensional linear subspaces of R^n. It is a smooth manifold of dimension:

```
dim Gr(k,n) = k(n-k)
```

Points can be represented as:
- **Orthonormal basis**: n x k matrix U with U^T U = I_k
- **Projector**: n x n matrix P = U U^T with P² = P

### Tangent Space

The tangent space at U consists of matrices Xi in R^(n x k) satisfying:

```
U^T Xi = 0
```

The Riemannian metric is the Frobenius inner product:

```
<Xi, Eta>_U = tr(Xi^T Eta)
```

### Geodesics

Given tangent vector Xi at U with SVD Xi = W S V^T, the geodesic is:

```
gamma(t) = U V cos(S t) V^T + W sin(S t) V^T
```

The exponential map is gamma(1) and the geodesic distance is ||S||_F.

### Sharp Bound Theorem

For subspaces V in Gr(k,n) and W in Gr(k',n') in common ambient space:

```
d²(V, W) >= |k - k'|
```

Equality holds if and only if one subspace contains the other. This provides a geometric foundation for transitions between Grassmannians.

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=grasscalc --cov-report=html
```

Current test coverage: 21 tests, all passing.

## Requirements

- Python 3.9+
- NumPy >= 1.20.0
- SciPy >= 1.7.0

### Optional Dependencies
- matplotlib >= 3.5.0 (visualization)
- pytest >= 7.0.0 (testing)
- geomstats, pymanopt (comparison/interop)

## Citation

If you use this package in your research, please cite:

```bibtex
@software{grasscalc2026,
  author = {Al Yaquob, A. Y.},
  title = {grasscalc: Grassmannian Calculus for Python},
  year = {2026},
  url = {https://github.com/alyaquob/physica/tree/main/grasscalc}
}

@article{alyaquob2026gct,
  author = {Al Yaquob, A. Y.},
  title = {Grassmannian Cosmological Theory:
           Deriving the Standard Model from Geometric Transitions},
  year = {2026},
  journal = {arXiv preprint}
}
```

## References

- Al Yaquob, A. (2026). *Grassmannian Calculus and Transition Operators: A Comprehensive Introduction*
- Al Yaquob, A. (2026). *Grassmannian Dynamics: Unconditional Uniqueness from Four Theorems*
- Edelman, A., Arias, T. A., & Smith, S. T. (1998). The geometry of algorithms with orthogonality constraints. *SIAM Journal on Matrix Analysis and Applications*
- Absil, P.-A., Mahony, R., & Sepulchre, R. (2008). *Optimization Algorithms on Matrix Manifolds*. Princeton University Press.

## License

MIT License - see [LICENSE](LICENSE) file.

## Author

**A. Y. Al Yaquob**
Email: amin@alyaquob.com
Independent Researcher

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
