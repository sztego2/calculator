"""Tkinter window for the calculator.

Run it, after installing the package, with::

    python -m calculator.app
"""

from __future__ import annotations

from collections.abc import Callable

import tkinter as tk
from tkinter import font as tkfont

from calculator.engine import OPERATIONS, Calculator

BG = "#c8c8c8"
FACE = "#f4f4f4"
FACE_PRESSED = "#dcdcdc"
INK = "#111111"
OUTLINE = "#111111"
DISPLAY_BG = "#ffffff"

BUTTON_W = 76
BUTTON_H = 70
GAP = 8
EQUALS_GAP = 28
MARGIN = 16
BELOW_DISPLAY = 16
SIGN = "+/\u2212"


class CalculatorApp:
    """Fixed-size calculator window. Buttons call :class:`Calculator`."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.engine = Calculator()
        self._font_family = _ui_font_family()
        self._build()

    def _build(self) -> None:
        root = self.root
        root.title("Calculator")
        root.configure(bg=BG)
        root.resizable(False, False)

        content = tk.Frame(root, bg=BG, highlightthickness=0, bd=0)
        content.pack(padx=MARGIN, pady=MARGIN)

        self.display_shell = tk.Frame(
            content,
            bg=OUTLINE,
            height=BUTTON_H,
            width=1,
            highlightthickness=0,
            bd=0,
        )
        self.display_shell.pack_propagate(False)
        self.display_shell.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=(0, GAP),
            pady=(0, BELOW_DISPLAY),
        )

        self.display = tk.Label(
            self.display_shell,
            text="0",
            anchor="e",
            justify="right",
            bg=DISPLAY_BG,
            fg=INK,
            font=(self._font_family, 22),
            padx=12,
            highlightthickness=0,
            bd=0,
        )
        self.display.pack(fill="both", expand=True, padx=2, pady=2)

        self.clear_button = self._button(
            content, "CE", self._clear, height=BUTTON_H
        )
        self.clear_button.grid(
            row=0,
            column=1,
            sticky="new",
            pady=(0, BELOW_DISPLAY),
        )

        self.numpad = tk.Frame(content, bg=BG, highlightthickness=0, bd=0)
        self.numpad.grid(row=1, column=0, sticky="nw", padx=(0, GAP))

        rows = (
            ("7", "8", "9"),
            ("4", "5", "6"),
            ("1", "2", "3"),
            (SIGN, "0", ","),
        )
        for row, labels in enumerate(rows):
            for col, label in enumerate(labels):
                button = self._pad_button(label)
                right = GAP if col < len(labels) - 1 else 0
                bottom = GAP if row < len(rows) - 1 else 0
                button.grid(row=row, column=col, padx=(0, right), pady=(0, bottom))

        self.ops = tk.Frame(content, bg=BG, highlightthickness=0, bd=0)
        self.ops.grid(row=1, column=1, sticky="nw")

        self.operator_buttons: list[tk.Frame] = []
        for index, symbol in enumerate(OPERATIONS):
            button = self._button(
                self.ops,
                symbol,
                lambda operator=symbol: self._operator(operator),
            )
            bottom = GAP if index < len(OPERATIONS) - 1 else 0
            button.grid(row=index, column=0, pady=(0, bottom), sticky="ew")
            self.operator_buttons.append(button)

        self.equals_button = self._button(self.ops, "=", self._equals)
        self.equals_button.grid(
            row=len(OPERATIONS),
            column=0,
            pady=(EQUALS_GAP, 0),
            sticky="ew",
        )

        root.update_idletasks()
        self.display_shell.configure(width=self.numpad.winfo_reqwidth())
        root.update_idletasks()
        self._refresh()

    def _pad_button(self, label: str) -> tk.Frame:
        if label == SIGN:
            return self._button(self.numpad, label, self._sign, font_size=15)
        if label == ",":
            return self._button(self.numpad, label, self._decimal)
        return self._button(
            self.numpad,
            label,
            lambda digit=label: self._digit(digit),
        )

    def _button(
        self,
        parent: tk.Misc,
        text: str,
        command: Callable[[], None],
        *,
        width: int = BUTTON_W,
        height: int = BUTTON_H,
        font_size: int = 18,
    ) -> tk.Frame:
        shell = tk.Frame(
            parent,
            width=width,
            height=height,
            bg=OUTLINE,
            highlightthickness=0,
            bd=0,
        )
        shell.pack_propagate(False)
        face = tk.Label(
            shell,
            text=text,
            bg=FACE,
            fg=INK,
            font=(self._font_family, font_size),
            highlightthickness=0,
            bd=0,
            cursor="hand2",
        )
        face.pack(fill="both", expand=True, padx=2, pady=2)

        def on_click(_event: object) -> None:
            face.configure(bg=FACE_PRESSED)

            def restore() -> None:
                try:
                    face.configure(bg=FACE)
                except tk.TclError:
                    return

            try:
                command()
            finally:
                face.after(80, restore)

        face.bind("<Button-1>", on_click)
        return shell

    def _refresh(self) -> None:
        text = self.engine.display
        size = 22 if len(text) <= 14 else 16
        self.display.configure(text=text, font=(self._font_family, size))

    def _digit(self, digit: str) -> None:
        self.engine.press_digit(digit)
        self._refresh()

    def _decimal(self) -> None:
        self.engine.press_decimal()
        self._refresh()

    def _sign(self) -> None:
        self.engine.press_sign()
        self._refresh()

    def _clear(self) -> None:
        self.engine.press_clear()
        self._refresh()

    def _operator(self, symbol: str) -> None:
        self.engine.press_operator(symbol)
        self._refresh()

    def _equals(self) -> None:
        self.engine.press_equals()
        self._refresh()


def _ui_font_family() -> str:
    if "Segoe UI" in tkfont.families():
        return "Segoe UI"
    return str(tkfont.nametofont("TkDefaultFont").actual("family"))


def main() -> None:
    root = tk.Tk()
    CalculatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
