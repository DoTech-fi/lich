# Git Workflow & Release Strategy

Lich Toolkit follows a **Collaboration-First** git workflow.

## The Golden Rule: Semantic Commits

All commits MUST follow the [Conventional Commits](https://www.conventionalcommits.org/) specification. This allows us to automate:
1.  **Changelogs** (Automatically generated)
2.  **Versioning** (Semantic Versioning)
3.  **Release Notes** (Beautiful & structured)

---

## 1. When working with AI (Antigravity) 🤖
**This is the preferred method.**
When you ask the AI to make changes, it will automatically:
1.  Write code.
2.  Run tests.
3.  **Generate a perfect Semantic Commit** message for you.

You just say: *"Implement Google Auth"*
AI does: `feat(auth): add google oauth integration with auto-redirect`

---

## 2. When working manually (Solo) 🧑‍💻
When you are coding alone in the terminal, use the **Lich Git Tools** to ensure you stay compliant.

### `lich commit`
Opens an interactive wizard to build a perfect commit message.
```bash
$ lich commit
# Wizard asks:
# 1. Type (feat, fix, docs...)
# 2. Scope (optional)
# 3. Description
# -> Generates: feat(ui): upate button styles
```

### `lich tag`
Creates a version tag safely.
```bash
$ lich tag v1.0.0
# Checks format, creates tag locally.
# Optional: --push to push immediately.
```

### `lich push`
Pushes your code to origin securely.
```bash
$ lich push
# Pushes current branch to origin/main
```

---

## 3. Release Process
To release a new version:

1.  **Ensure CI Passes**: Run `lich ci` or check GitHub.
2.  **Tag & Push**:
    ```bash
    lich tag v1.1.0 --push
    ```
3.  **Done**: GitHub Actions will detect the tag, build the package, and publish the release.
