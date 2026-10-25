"""Calculator state and arithmetic, with no user interface.

The display uses a decimal comma. Calculations use :class:`decimal.Decimal`,
so ``0,1 + 0,2`` is ``0,3``.

Add another operation by putting one callable in :data:`OPERATIONS`.
The window builds a button for every entry, in insertion order.
"""

from __future__ import annotations

from collections.abc import Callable
from decimal import (
    ROUND_HALF_UP,
    Decimal,
    DivisionByZero,
    InvalidOperation,
    Overflow,
    localcontext,
)

# Significant digits kept on a result. Longer values switch to scientific form.
_SIG_DIGITS = 12
_CALC_PRECISION = 28
_PLAIN_MIN = Decimal("1e-6")
_PLAIN_MAX = Decimal(10) ** _SIG_DIGITS

_Operation = Callable[[Decimal, Decimal], Decimal]


def _add(left: Decimal, right: Decimal) -> Decimal:
    return left + right


def _subtract(left: Decimal, right: Decimal) -> Decimal:
    return left - right


def _multiply(left: Decimal, right: Decimal) -> Decimal:
    return left * right


def _divide(left: Decimal, right: Decimal) -> Decimal:
    if right == 0:
        raise DivisionByZero("division by zero")
    return left / right


OPERATIONS: dict[str, _Operation] = {
    "÷": _divide,
    "×": _multiply,
    "−": _subtract,
    "+": _add,
}


class Calculator:
    """Four-function calculator. Keys call the ``press_*`` methods."""

    def __init__(self) -> None:
        self._entry = "0"
        self._accumulator: Decimal | None = None
        self._pending: str | None = None
        # True when the next digit starts a new number (after =, an operator,
        # or at startup). False while a number is being typed, including the
        # 0 left behind by CE.
        self._awaiting_input = True
        self._error = False

    @property
    def display(self) -> str:
        """Text currently shown, using a comma as the decimal mark."""
        if self._error:
            return "Error"
        return self._entry

    def press_digit(self, digit: str) -> None:
        if len(digit) != 1 or digit not in "0123456789":
            raise ValueError(f"expected a digit, got {digit!r}")
        if self._error:
            self._clear_all()
        if self._awaiting_input:
            self._entry = digit
            self._awaiting_input = False
            return
        if self._is_bare_zero():
            sign = "-" if self._entry.startswith("-") else ""
            updated = f"{sign}{digit}"
            self._entry = "0" if updated == "-0" else updated
            return
        if self._digit_count() >= _SIG_DIGITS:
            return
        self._entry += digit

    def press_decimal(self) -> None:
        if self._error:
            self._clear_all()
        if self._awaiting_input:
            self._entry = "0,"
            self._awaiting_input = False
            return
        if "," in self._entry:
            return
        self._entry += ","

    def press_sign(self) -> None:
        if self._error:
            return
        if self._parse(self._entry) == 0:
            return
        if self._entry.startswith("-"):
            self._entry = self._entry[1:]
        else:
            self._entry = f"-{self._entry}"

    def press_clear(self) -> None:
        """Clear the number being typed. A pending operation stays.

        An error is wiped completely and the display returns to ``0``.
        """
        if self._error:
            self._clear_all()
            return
        self._entry = "0"
        self._awaiting_input = False

    def press_operator(self, operator: str) -> None:
        if operator not in OPERATIONS:
            raise ValueError(f"unknown operator: {operator!r}")
        if self._error:
            return
        if self._pending is not None and not self._awaiting_input:
            self._evaluate()
            if self._error:
                return
        elif self._pending is None:
            self._accumulator = self._parse(self._entry)
        self._pending = operator
        self._awaiting_input = True

    def press_equals(self) -> None:
        if self._error:
            return
        if self._pending is None or self._accumulator is None:
            self._entry = _format_number(self._parse(self._entry))
            self._awaiting_input = True
            return
        self._evaluate()
        if not self._error:
            self._pending = None
            self._awaiting_input = True

    def _evaluate(self) -> None:
        if self._pending is None or self._accumulator is None:
            return
        try:
            result = _apply(self._pending, self._accumulator, self._parse(self._entry))
        except (DivisionByZero, InvalidOperation, Overflow, ZeroDivisionError):
            self._fail()
            return
        if not result.is_finite():
            self._fail()
            return
        self._accumulator = result
        self._entry = _format_number(result)

    def _fail(self) -> None:
        self._error = True
        self._entry = "0"
        self._accumulator = None
        self._pending = None
        self._awaiting_input = True

    def _clear_all(self) -> None:
        self._entry = "0"
        self._accumulator = None
        self._pending = None
        self._awaiting_input = True
        self._error = False

    def _is_bare_zero(self) -> bool:
        return "," not in self._entry and self._entry.lstrip("-") == "0"

    def _digit_count(self) -> int:
        return sum(character.isdigit() for character in self._entry)

    @staticmethod
    def _parse(entry: str) -> Decimal:
        return Decimal(entry.replace(",", "."))


def _apply(operator: str, left: Decimal, right: Decimal) -> Decimal:
    with localcontext() as ctx:
        ctx.prec = _CALC_PRECISION
        ctx.rounding = ROUND_HALF_UP
        ctx.traps[DivisionByZero] = True
        ctx.traps[InvalidOperation] = True
        ctx.traps[Overflow] = True
        return OPERATIONS[operator](left, right)


def _format_number(value: Decimal) -> str:
    """Render a result with a comma, without trailing zeros."""
    if not value.is_finite() or value == 0:
        return "0"
    with localcontext() as ctx:
        ctx.prec = _SIG_DIGITS
        ctx.rounding = ROUND_HALF_UP
        rounded = +value
    if rounded == 0:
        return "0"
    magnitude = abs(rounded)
    if magnitude >= _PLAIN_MAX or magnitude < _PLAIN_MIN:
        return _format_scientific(rounded)
    text = format(rounded, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    if text in {"", "-0", "-"}:
        return "0"
    return text.replace(".", ",")


def _format_scientific(value: Decimal) -> str:
    mantissa, exponent = format(value, f".{_SIG_DIGITS - 1}E").split("E")
    mantissa = mantissa.rstrip("0").rstrip(".")
    if mantissa in {"", "-0", "-"}:
        return "0"
    return f"{mantissa.replace('.', ',')}e{int(exponent):+d}"
