# PYTHON UV RULE - MANDATORY Python Package Management

## 🚨 CRITICAL RULE: ALL Python Environments MUST Use UV

### Mandatory Requirements

**EVERY Python project in this monorepo MUST use UV for package management. NO EXCEPTIONS.**

### Implementation Rules

1. **Package Management**
   - ✅ ALWAYS use `uv` for ALL Python dependencies
   - ❌ NEVER use `pip`, `poetry`, `pipenv`, or other package managers
   - ❌ NEVER create virtual environments with `python -m venv`
   - ✅ ALWAYS use `uv venv` for virtual environment creation

2. **Dependency Installation**
   ```bash
   # CORRECT - Always use these commands:
   uv venv                    # Create virtual environment
   source .venv/bin/activate  # Activate virtual environment (Unix)
   .venv\Scripts\activate     # Activate virtual environment (Windows)
   uv pip install -e .        # Install editable package
   uv pip install package     # Install specific package
   uv pip sync               # Sync dependencies from uv.lock
   
   # INCORRECT - Never use these:
   python -m venv venv       ❌
   pip install package       ❌
   poetry install            ❌
   pipenv install            ❌
   ```

3. **Project Configuration**
   - ✅ MUST have `uv.lock` file in every Python project
   - ✅ MUST have `pyproject.toml` for project metadata
   - ❌ REMOVE `poetry.lock`, `Pipfile.lock`, `requirements.txt` if present
   - ✅ CONVERT existing projects to UV immediately

4. **UV Installation Check**
   ```bash
   # Ensure UV is installed globally:
   curl -LsSf https://astral.sh/uv/install.sh | sh
   # or
   brew install uv
   ```

### Conversion Process for Existing Projects

1. **From Poetry/Pipenv/pip:**
   ```bash
   # Remove old virtual environment
   rm -rf venv/ .venv/ env/
   
   # Create UV environment
   uv venv
   source .venv/bin/activate
   
   # Install dependencies
   uv pip install -e .
   
   # Generate lock file
   uv pip freeze > requirements.txt
   uv pip compile pyproject.toml -o uv.lock
   
   # Remove old lock files
   rm -f poetry.lock Pipfile.lock
   ```

2. **Verify Installation:**
   ```bash
   which python  # Should point to .venv/bin/python
   uv pip list   # Should show installed packages
   ```

### CI/CD Integration

All CI/CD pipelines MUST:
- Install UV as first step
- Use UV for all dependency management
- Cache UV lock files for faster builds

### Benefits of UV

1. **Speed**: 10-100x faster than pip
2. **Reproducibility**: Lock files ensure consistent environments
3. **Compatibility**: Works with existing pyproject.toml
4. **Simplicity**: Single tool for venv + package management
5. **Modern**: Built with Rust for performance

### Enforcement

- **Code Reviews**: Reject PRs using non-UV package managers
- **Pre-commit Hooks**: Check for UV usage
- **Automated Checks**: CI fails if UV not used
- **Documentation**: Update all Python setup docs to use UV

### Exception Process

**There are NO exceptions to this rule.** If you believe you need an exception, you don't - UV can handle your use case.

---

**Last Updated**: 2025-08-01
**Status**: MANDATORY - IMMEDIATE ENFORCEMENT