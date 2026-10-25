# Calculator

Desktop calculator for add, subtract, multiply, and divide. The display uses a decimal comma. The math uses `decimal.Decimal`, so `0,1 + 0,2` stays exact.

## Setup

From this directory (`calculator/`):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

## Run the app

```powershell
python -m calculator.app
```

## Tests

No tests are written yet. `tests/` is only a placeholder.

```powershell
pytest
```
