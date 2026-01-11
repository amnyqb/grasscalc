# Grasscalc Paper

This directory contains the academic paper describing the `grasscalc` package.

## Files

| File | Description |
|------|-------------|
| `grasscalc_paper.tex` | Main paper (LaTeX) |
| `supplementary.tex` | Extended proofs and derivations |
| `Makefile` | Build automation |
| `experiments/` | Numerical experiment scripts |

## Building the Paper

### Prerequisites

- LaTeX distribution (TeX Live, MiKTeX, or MacTeX)
- Python 3.9+ with grasscalc installed
- Make (optional, for automation)

### Quick Build

```bash
# Build PDF only
make pdf

# Run experiments and build PDF
make all

# Quick experiments (fewer trials)
make quick-experiments
```

### Manual Build

```bash
# Compile LaTeX
pdflatex grasscalc_paper
pdflatex grasscalc_paper  # Run twice for TOC

# Compile supplementary
pdflatex supplementary
```

## Running Experiments

The `experiments/` directory contains scripts to reproduce all numerical results:

```bash
cd experiments

# Full experiments (may take several minutes)
python run_experiments.py --output ../results

# Quick version for testing
python run_experiments.py --quick --output ../results
```

### Experiment Outputs

Results are saved to `results/`:
- `all_results.json` - Complete numerical results
- `table_*.tex` - LaTeX table fragments for inclusion

## Paper Structure

### Main Paper

1. **Introduction** - Motivation, contributions, organization
2. **Mathematical Foundations** - Grassmannian geometry review
3. **Sharp Bound Theorem** - Novel result with proof
4. **Software Architecture** - Package design
5. **GCT Module** - Physics applications
6. **Numerical Experiments** - Validation results
7. **Comparison** - vs pymanopt, geomstats, geoopt
8. **Conclusions** - Summary and future work

### Supplementary Materials

- Extended Sharp Bound proof
- Weinberg angle derivation
- E₈ structure analysis
- Curvature computations
- Implementation details

## Key Results

| Result | Value | Reference |
|--------|-------|-----------|
| Sharp Bound | d²(V,W) ≥ \|k-k'\| | Theorem 3.1 |
| Weinberg angle | sin²θ = 3/13 = 0.23077 | Section 5.3 |
| GCT total dimension | 508 = 496 + 12 | Table 5 |
| Prediction error | 0.19% | Section 5.3 |

## Citation

```bibtex
@article{alyaquob2026grasscalc,
  title={Grassmannian Calculus: A Computational Framework for
         Differential Geometry on Subspace Manifolds with
         Applications to Theoretical Physics},
  author={Al Yaquob, A. Y.},
  journal={arXiv preprint},
  year={2026}
}
```

## License

MIT License - see repository root for details.
