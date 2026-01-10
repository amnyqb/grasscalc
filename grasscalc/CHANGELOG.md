# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Placeholder for future changes

## [0.1.0] - 2026-01-10

### Added

#### Core Module
- Linear algebra utilities: `qr_retraction`, `svd_stable`, `gram_schmidt`, `stable_qr`
- Point representations: `GrassmannPoint`, `to_projector`, `to_basis`, `stabilize`
- Distance metrics: `geodesic_distance`, `chordal_distance_sq`, `principal_angles`, `frobenius_distance`
- Tangent space operations: `tangent_project`, `tangent_inner_product`, `tangent_norm`
- Exponential and logarithm maps with machine-precision roundtrip
- Parallel transport preserving inner products
- Geodesic interpolation
- Curvature tensor and sectional curvature
- Random sampling: `sample_grassmann`, `sample_tangent`

#### Calculus Operations
- Riemannian gradient and Hessian
- Directional and partial derivatives
- Covariant derivative
- Lie derivative
- Line integrals along curves
- Surface integrals
- Volume elements
- Differential forms (exterior derivative, wedge product, pullback, pushforward)

#### Layer 1: Within-Manifold Calculus
- Objective functions: `energy_overlap`, `stage_function`, `rayleigh_quotient`
- Gradient flows: `gradient_flow`, `run_gradient_flow`, `geodesic_flow`, `hamiltonian_flow`
- Optimization: `minimize_on_grassmann`, `trust_region_step`, `conjugate_gradient_step`

#### Layer 2: Between-Manifold Transitions
- Correspondences: `raise_k_successors`, `raise_n_successors`, `compose_correspondences`
- Sharp Bound Theorem: `sharp_bound_check`, `sharp_bound_gap`, `is_saturated`, `is_containment`
- Transition operators: `transition_action`, `optimal_transition`
- Min-plus operators: `minplus_operator`, `argmin_transition`
- Hybrid evolution: `run_hybrid_chain`, `HybridState`
- Macro variables: `macro_variables`, `codimension`, `grassmann_dimension`

#### GCT Module
- Seven-manifold chain definition: `GCT_CHAIN`, `gct_dimension`, `gct_total_dimension`
- Weinberg angle: `weinberg_angle`, `weinberg_angle_experimental`, `weinberg_error`
- Transition operators: `T0` through `T5`
- Validation: `verify_gct_dimensions`, `verify_gct_chain`, `run_gct_tests`
- Physics: `division_algebra_map`, `hurwitz_dimensions`, `DIVISION_ALGEBRAS`

#### Documentation
- Comprehensive README with examples
- API reference documentation
- Usage examples documentation
- Contributing guidelines
- MIT License

#### Testing
- 21 tests covering core geometry and GCT module
- All tests passing

### Fixed
- Exponential/logarithm map roundtrip now achieves machine precision (~1e-15)
- Parallel transport correctly preserves inner products

## [0.0.1] - 2026-01-09

### Added
- Initial package structure
- Basic Grassmannian geometry operations

---

[Unreleased]: https://github.com/alyaquob/physica/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/alyaquob/physica/releases/tag/v0.1.0
[0.0.1]: https://github.com/alyaquob/physica/releases/tag/v0.0.1
