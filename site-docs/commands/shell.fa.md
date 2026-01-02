# lich shell

Shell تعاملی پایتون با context پروژه.

## استفاده

```bash
lich shell
```

## مثال

```bash
$ lich shell

🧙 Shell تعاملی لیچ

>>> from internal.entities.user import User
>>> from internal.services.user_service import UserService
>>> 
>>> users = await user_service.list_all()
>>> len(users)
42
```

## پشتیبانی از IPython

اگر IPython نصب باشد:

- Syntax highlighting
- Tab completion
- Magic commands

نصب IPython:

```bash
pip install ipython
```
