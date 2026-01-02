# lich test

Run tests with pytest.

## Usage

```bash
lich test [OPTIONS] [PATH]
```

## Options

| Option | Description |
|--------|-------------|
| `--unit`, `-u` | Run only unit tests |
| `--integration`, `-i` | Run only integration tests |
| `--coverage`, `-c` | Show coverage report |
| `--verbose`, `-v` | Verbose output |
| `--watch`, `-w` | Re-run on file changes |

## Examples

```bash
# Run all tests
lich test

# Run with coverage
lich test --coverage

# Run unit tests only
lich test --unit

# Run specific file
lich test backend/tests/test_users.py

# Watch mode
lich test --watch
```

## Example Output

```bash
$ lich test --coverage

🧪 Running Tests

============================= test session starts =============================
collected 24 items

tests/test_users.py ....                                               [ 16%]
tests/test_products.py ......                                          [ 41%]
tests/test_orders.py ..........                                        [ 83%]
tests/test_auth.py ....                                                [100%]

---------- coverage: platform darwin, python 3.12 -----------
Name                                Stmts   Miss  Cover
-------------------------------------------------------
internal/services/user_service.py      45      2    96%
internal/services/order_service.py     67      5    93%
-------------------------------------------------------
TOTAL                                 245     15    94%

========================= 24 passed in 0.83s ==========================
```

## See Also

- [`make factory`](make/factory.md) - Create test data
- [Testing Guide](../best-practices/testing.md)
