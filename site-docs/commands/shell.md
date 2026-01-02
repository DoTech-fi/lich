# lich shell

Interactive Python shell with project context.

## Usage

```bash
lich shell
```

## What It Does

Opens a Python REPL with:

- Project modules pre-imported
- Database session ready
- Services available

## Example

```bash
$ lich shell

🧙 Lich Interactive Shell

>>> from internal.entities.user import User
>>> from internal.services.user_service import UserService
>>> 
>>> # Create a user
>>> user = User(name="Test", email="test@example.com")
>>> 
>>> # Query the database
>>> users = await user_service.list_all()
>>> len(users)
42
```

## IPython Support

If IPython is installed, you get enhanced features:

- Syntax highlighting
- Tab completion
- Magic commands

Install IPython:

```bash
pip install ipython
```
