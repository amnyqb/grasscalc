# Contributing to grasscalc

Thank you for your interest in contributing to grasscalc! This document provides guidelines and best practices for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)
- [Style Guide](#style-guide)
- [Areas for Contribution](#areas-for-contribution)

---

## Code of Conduct

This project follows a simple code of conduct:

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Assume good intentions

---

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Git
- pip or conda for package management

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/physica.git
   cd physica/grasscalc
   ```
3. Add upstream remote:
   ```bash
   git remote add upstream https://github.com/alyaquob/physica.git
   ```

---

## Development Setup

### Create Virtual Environment

```bash
# Using venv
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Using conda
conda create -n grasscalc python=3.11
conda activate grasscalc
```

### Install in Development Mode

```bash
# Basic installation
pip install -e .

# With development dependencies
pip install -e ".[dev]"

# Full installation with all extras
pip install -e ".[full]"
```

### Verify Installation

```bash
# Run tests
pytest tests/ -v

# Check imports work
python -c "from grasscalc import core; print('Success!')"
```

---

## Making Changes

### Create a Branch

```bash
# Sync with upstream
git fetch upstream
git checkout main
git merge upstream/main

# Create feature branch
git checkout -b feature/your-feature-name
```

### Branch Naming Convention

- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation updates
- `refactor/description` - Code refactoring
- `test/description` - Test additions/improvements

### Commit Messages

Use clear, descriptive commit messages:

```
Short summary (50 chars or less)

More detailed explanation if needed. Wrap at 72 characters.
Explain what and why, not how.

- Bullet points are okay
- Use present tense ("Add feature" not "Added feature")
```

Examples:
- `Add parallel transport along arbitrary curves`
- `Fix exponential map for near-zero tangent vectors`
- `Update API documentation for calculus module`

---

## Testing

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_core.py -v

# Run specific test
pytest tests/test_core.py::TestTangent::test_tangent_projection -v

# Run with coverage
pytest tests/ --cov=grasscalc --cov-report=html
```

### Writing Tests

All new features should include tests. Follow these guidelines:

```python
# tests/test_module.py

import numpy as np
import pytest
from grasscalc.core import sample_grassmann

class TestFeatureName:
    """Test suite for new feature."""

    def test_basic_functionality(self):
        """Test that basic case works."""
        U = sample_grassmann(3, 7)
        result = new_function(U)
        assert result is not None

    def test_edge_case(self):
        """Test edge case handling."""
        # Test with zero, identity, etc.
        pass

    def test_mathematical_property(self):
        """Test that mathematical properties hold."""
        # E.g., symmetry, roundtrip, bounds
        pass

    @pytest.mark.parametrize("k,n", [(2, 5), (3, 7), (5, 10)])
    def test_various_dimensions(self, k, n):
        """Test across different dimensions."""
        U = sample_grassmann(k, n)
        # Test with this U
        pass
```

### Test Categories

1. **Unit tests**: Test individual functions
2. **Property tests**: Test mathematical properties (symmetry, bounds, etc.)
3. **Integration tests**: Test component interactions
4. **Regression tests**: Ensure bugs don't reappear

---

## Documentation

### Docstring Format

Use NumPy-style docstrings:

```python
def function_name(param1, param2, optional_param=None):
    """
    Short description of function.

    Longer description if needed, explaining the mathematical
    background or algorithm used.

    Parameters
    ----------
    param1 : ndarray, shape (n, k)
        Description of first parameter
    param2 : float
        Description of second parameter
    optional_param : str, optional
        Description of optional parameter (default: None)

    Returns
    -------
    result : ndarray, shape (n, k)
        Description of return value

    Raises
    ------
    ValueError
        If param1 has wrong shape

    Examples
    --------
    >>> U = sample_grassmann(3, 7)
    >>> result = function_name(U, 1.0)
    >>> result.shape
    (7, 3)

    Notes
    -----
    Mathematical formula or reference:

    .. math::

        f(x) = \\sum_{i=1}^n x_i^2

    References
    ----------
    .. [1] Author, "Paper Title", Journal, Year.

    See Also
    --------
    related_function : Brief description of relationship
    """
    pass
```

### Updating Documentation

1. Update docstrings for new/modified functions
2. Update `docs/API.md` for new public API
3. Add examples to `docs/EXAMPLES.md`
4. Update `README.md` if features change significantly

---

## Pull Request Process

### Before Submitting

1. **Sync with upstream**:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Run tests**:
   ```bash
   pytest tests/ -v
   ```

3. **Check style** (if using linters):
   ```bash
   black grasscalc/
   isort grasscalc/
   flake8 grasscalc/
   ```

4. **Update documentation** as needed

### Submitting

1. Push your branch:
   ```bash
   git push origin feature/your-feature-name
   ```

2. Create Pull Request on GitHub

3. Fill in the PR template:
   - Description of changes
   - Related issues
   - Testing performed
   - Documentation updates

### PR Review

- Address reviewer feedback
- Keep commits clean (squash if needed)
- Be patient - reviews take time

---

## Style Guide

### Python Style

- Follow PEP 8
- Maximum line length: 88 characters (Black default)
- Use type hints for public functions:
  ```python
  def function(param: np.ndarray, value: float = 1.0) -> np.ndarray:
      pass
  ```

### Naming Conventions

- **Functions**: `lowercase_with_underscores`
- **Classes**: `CamelCase`
- **Constants**: `UPPERCASE_WITH_UNDERSCORES`
- **Private**: `_leading_underscore`

### Code Organization

```python
# Standard library imports
import os
from typing import Optional, Tuple

# Third-party imports
import numpy as np
from numpy.linalg import norm, svd
from scipy.linalg import qr

# Local imports
from .distances import geodesic_distance
from .tangent import tangent_project
```

### Mathematical Notation

Use consistent notation in comments:
- `U, V, W` - Points on Grassmannian (n x k matrices)
- `Xi, Eta, Zeta` - Tangent vectors
- `k` - Subspace dimension
- `n` - Ambient dimension
- `d` - Distance
- `theta` - Principal angles

---

## Areas for Contribution

### High Priority

1. **Performance optimization**
   - Vectorized operations
   - Caching strategies
   - GPU support (optional)

2. **Additional geometry**
   - Stiefel manifold support
   - Flag manifolds
   - Symmetric spaces

3. **Integration methods**
   - Monte Carlo integration
   - Adaptive quadrature
   - Higher-order forms

### Medium Priority

4. **Visualization**
   - 2D/3D projections
   - Geodesic plots
   - Curvature visualization

5. **Interoperability**
   - Geomstats compatibility
   - PyManopt interface
   - PyTorch/JAX backends

6. **Applications**
   - PCA on manifolds
   - Subspace clustering
   - Computer vision examples

### Documentation

7. **Tutorials**
   - Beginner's guide
   - Mathematical background
   - Physics applications

8. **Examples**
   - Jupyter notebooks
   - Application examples
   - Benchmark comparisons

---

## Questions?

- Open an issue for bugs or feature requests
- Start a discussion for questions
- Email: amin@alyaquob.com

Thank you for contributing to grasscalc!
