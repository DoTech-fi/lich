# Release Workflow & Versioning

Lich Toolkit uses **Semantic Versioning** and **Automated Releases** powered by GitHub Actions and `python-semantic-release`.

## Release Strategy

We typically follow a **Git Flow**-like approach with two key branches:

1.  **`main`**: The development branch. All PRs, features, and fixes are merged here first.
2.  **`release`**: The production branch. Merging `main` into `release` triggers a release.

---

## How to Release

To publish a new version of Lich Toolkit (or your project):

1.  **Develop**: Push changes or merge Pull Requests into the `main` branch.
2.  **Verify**: Ensure CI/CD tests pass on `main`.
3.  **PR to Release**:
    *   Open a Pull Request from `main` to `release`.
    *   Review the changes.
    *   Merge the PR.
4.  **Auto-Release**:
    *   GitHub Actions detects the push to `release`.
    *   It analyzes your commits (Conventional Commits).
    *   It calculates the new version (e.g., `feature:` = minor bump, `fix:` = patch bump).
    *   It creates a **Git Tag**, a **GitHub Release**, and generates the **CHANGELOG**.

## Commit Message Convention

We use **Conventional Commits** to determine version bumps:

*   `fix: ...` -> **Patch Release** (v1.0.0 -> v1.0.1)
*   `feat: ...` -> **Minor Release** (v1.0.0 -> v1.1.0)
*   `feat!: ...` or `BREAKING CHANGE:` -> **Major Release** (v1.0.0 -> v2.0.0)
*   `chore:`, `docs:`, `style:` -> No version bump.

---
**Note:** Always keep `main` stable, as it is the source of truth for the next release.
