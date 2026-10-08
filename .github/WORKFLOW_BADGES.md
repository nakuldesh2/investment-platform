# GitHub Actions Badges

Add these badges to your README.md to show CI/CD status.

## Status Badges

Add to the top of README.md for quick status visibility:

```markdown
[![CI - Lint, Type Check, and Test](https://github.com/nakuldesh2/investment-platform/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/nakuldesh2/investment-platform/actions/workflows/ci.yml)

[![Deploy to Railway](https://github.com/nakuldesh2/investment-platform/actions/workflows/deploy.yml/badge.svg?branch=main)](https://github.com/nakuldesh2/investment-platform/actions/workflows/deploy.yml)
```

## Rendered in README

The badges will show:
- 🟢 **passing** - All tests passed, code quality good
- 🔴 **failing** - Tests failed, needs fixing
- 🟡 **pending** - Workflow is running

Users can click badges to see detailed logs.

## Full Badge Setup

```markdown
# Investment Research Platform

[![CI - Lint, Type Check, and Test](https://github.com/nakuldesh2/investment-platform/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/nakuldesh2/investment-platform/actions/workflows/ci.yml)
[![Deploy to Railway](https://github.com/nakuldesh2/investment-platform/actions/workflows/deploy.yml/badge.svg?branch=main)](https://github.com/nakuldesh2/investment-platform/actions/workflows/deploy.yml)

... rest of README
```

## Additional Badges (Optional)

Consider adding:

```markdown
<!-- Python version -->
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

<!-- Node version -->
[![Node 18+](https://img.shields.io/badge/node-18+-green.svg)](https://nodejs.org/)

<!-- License -->
[![License](https://img.shields.io/badge/license-MIT-brightgreen.svg)](LICENSE)

<!-- Security -->
[![Security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)
```

## Example README Header

```markdown
# Investment Research Platform

[![CI - Lint, Type Check, and Test](https://github.com/nakuldesh2/investment-platform/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/nakuldesh2/investment-platform/actions/workflows/ci.yml)
[![Deploy to Railway](https://github.com/nakuldesh2/investment-platform/actions/workflows/deploy.yml/badge.svg?branch=main)](https://github.com/nakuldesh2/investment-platform/actions/workflows/deploy.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Node 18+](https://img.shields.io/badge/node-18+-green.svg)](https://nodejs.org/)

An enterprise-grade microservices platform for AI-assisted investment analysis...
```

## Test Coverage Badge

If you add coverage reporting:

```markdown
[![codecov](https://codecov.io/github/nakuldesh2/investment-platform/branch/main/graph/badge.svg)](https://codecov.io/github/nakuldesh2/investment-platform)
```

## Status Page

View all workflows at:
```
https://github.com/nakuldesh2/investment-platform/actions
```

## Badge Service

Badges come from:
- GitHub Actions (built-in)
- Shields.io (https://shields.io)
- Codecov (if coverage enabled)
