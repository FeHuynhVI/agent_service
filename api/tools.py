"""Executable tools for agents: SymPy math and Python runner.

These functions are registered (best-effort) to specific agents so they can
invoke them via the underlying AutoGen function-calling interface. The
registration gracefully no-ops if the current AutoGen version doesn't expose
the expected registration APIs.
"""

from __future__ import annotations

import os
import re
import sys
import tempfile
import subprocess
from typing import Any, Dict, Optional

from .agent_base import logger


# ----------------------
# Python code runner
# ----------------------
_DISALLOWED_PATTERNS = [
    r"\bimport\s+os\b",
    r"\bimport\s+sys\b",
    r"\bimport\s+subprocess\b",
    r"\bimport\s+socket\b",
    r"\bimport\s+http\b",
    r"\bimport\s+requests\b",
    r"\bopen\s*\(",
    r"__import__\s*\(",
]

# ----------------------
# SymPy math operations
# ----------------------
def sympy_compute(
    expr: str,
    *,
    task: str = "simplify",
    var: str = "x",
    order: int = 1,
    lower: Optional[str] = None,
    upper: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Compute symbolic results using SymPy.

    Parameters:
    - expr: math expression or equation (e.g., "x^2 - 1", or "x^2-1=0").
    - task: one of ["simplify","solve","diff","integrate","factor","expand","limit"].
    - var: main variable (default: "x").
    - order: derivative order for "diff".
    - lower/upper: bounds for definite integrals when task == "integrate".

    Returns a JSON-serializable dict: {"task": ..., "input": ..., "result": str, "latex": str|None}
    """
    try:
        import sympy as sp
    except Exception as e:  # pragma: no cover - optional dependency
        return {
            "task": task,
            "input": expr,
            "error": f"SymPy not available: {e}",
        }

    # Map caret to ** for exponent if user uses x^2
    cleaned = expr.replace("^", "**") if isinstance(expr, str) else str(expr)

    # Build symbol table for safe sympify
    # Collect identifiers and create symbols lazily
    ident_re = re.compile(r"[A-Za-z_]\w*")
    idents = sorted(set(ident_re.findall(cleaned)))
    # Exclude Python keywords/known dangerous names
    blacklist = {"import", "os", "sys", "subprocess", "eval", "exec", "open", "__import__"}
    idents = [s for s in idents if s not in blacklist]
    symbols: Dict[str, Any] = {}
    for name in idents:
        try:
            symbols[name] = sp.symbols(name)
        except Exception:
            pass

    try:
        # Equation support: a=b → sp.Eq(a,b)
        if task == "solve" and "=" in cleaned:
            lhs, rhs = cleaned.split("=", 1)
            lhs_s = sp.sympify(lhs, locals=symbols)
            rhs_s = sp.sympify(rhs, locals=symbols)
            equation = sp.Eq(lhs_s, rhs_s)
            sym_var = symbols.get(var, sp.symbols(var))
            sol = sp.solve(equation, sym_var)
            result = str(sol)
            latex = sp.latex(sol)
        else:
            sym_expr = sp.sympify(cleaned, locals=symbols)
            sym_var = symbols.get(var, sp.symbols(var))
            if task == "simplify":
                res = sp.simplify(sym_expr)
            elif task == "solve":
                res = sp.solve(sym_expr, sym_var)
            elif task == "diff":
                res = sp.diff(sym_expr, sym_var, order)
            elif task == "integrate":
                if lower is not None and upper is not None:
                    a = sp.sympify(str(lower), locals=symbols)
                    b = sp.sympify(str(upper), locals=symbols)
                    res = sp.integrate(sym_expr, (sym_var, a, b))
                else:
                    res = sp.integrate(sym_expr, sym_var)
            elif task == "factor":
                res = sp.factor(sym_expr)
            elif task == "expand":
                res = sp.expand(sym_expr)
            elif task == "limit":
                # Expect expr like f(x); use var and upper as the approach value (e.g. 0 or oo)
                point = sp.sympify(str(upper) if upper is not None else 0, locals=symbols)
                res = sp.limit(sym_expr, sym_var, point)
            else:
                return {"task": task, "input": expr, "error": f"Unsupported task: {task}"}

            result = str(res)
            try:
                latex = sp.latex(res)
            except Exception:
                latex = None

        return {
            "task": task,
            "input": expr,
            "result": result,
            "latex": latex,
        }
    except Exception as e:  # pragma: no cover - robustness
        return {
            "task": task,
            "input": expr,
            "error": f"SymPy error: {e}",
        }

def run_python(
    code: str,
    *,
    stdin: Optional[str] = None,
    timeout_sec: int = 3,
) -> Dict[str, Any]:
    """
    Execute short Python code safely in a subprocess with a timeout.

    - Blocks common dangerous imports and file/network access via simple pattern checks.
    - Captures stdout/stderr and returns exit information.
    - Not a security sandbox; use only for trusted/short snippets.
    """
    if not isinstance(code, str) or len(code.strip()) == 0:
        return {"error": "Empty code"}

    for pat in _DISALLOWED_PATTERNS:
        if re.search(pat, code):
            return {"error": f"Disallowed pattern: {pat}"}

    # Normalize newlines
    snippet = code.replace("\r\n", "\n")

    with tempfile.TemporaryDirectory(prefix="agent_py_") as tmp:
        main_py = os.path.join(tmp, "main.py")
        with open(main_py, "w", encoding="utf-8") as f:
            f.write(snippet)

        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        try:
            proc = subprocess.run(
                [sys.executable, main_py],
                input=stdin if isinstance(stdin, str) else None,
                capture_output=True,
                text=True,
                timeout=max(1, int(timeout_sec)),
                env=env,
            )
            return {
                "stdout": proc.stdout,
                "stderr": proc.stderr,
                "exit_code": proc.returncode,
                "timed_out": False,
            }
        except subprocess.TimeoutExpired as e:
            return {
                "stdout": e.stdout or "",
                "stderr": e.stderr or "",
                "exit_code": None,
                "timed_out": True,
            }
        except Exception as e:  # pragma: no cover - robustness
            return {"error": f"Run error: {e}"}


# ----------------------
# Registration helpers
# ----------------------
def _try_register(agent: Any, func: Any) -> bool:
    """Attempt to register a Python function as a tool for an agent.

    Tries several known AutoGen registration APIs and returns True if any
    succeeds, otherwise False. Never raises.
    """
    tried = []
    # register_for_execution is commonly a decorator-producing method.
    if hasattr(agent, "register_for_execution"):
        try:
            dec = agent.register_for_execution()  # type: ignore[attr-defined]
            dec(func)
            logger.info("Registered tool via register_for_execution: %s", getattr(func, "__name__", func))
            return True
        except Exception as e:
            tried.append(f"register_for_execution: {e}")

    for name in ("register_tool", "register_function", "register_for_llm"):
        if hasattr(agent, name):
            try:
                getattr(agent, name)(func)
                logger.info("Registered tool via %s: %s", name, getattr(func, "__name__", func))
                return True
            except Exception as e:
                tried.append(f"{name}: {e}")

    if tried:
        logger.warning("Tool registration failed on %s with: %s", getattr(agent, "name", agent), "; ".join(tried))
    else:
        logger.warning("No known registration API on agent: %s", getattr(agent, "name", agent))
    return False


def attach_math_tools(agent: Any) -> None:
    """Attach SymPy tools to the Math expert agent (best-effort)."""
    _try_register(agent, sympy_compute)


def attach_cs_tools(agent: Any) -> None:
    """Attach Python runner tools to the CS expert agent (best-effort)."""
    _try_register(agent, run_python)


__all__ = [
    "sympy_compute",
    "run_python",
    "attach_math_tools",
    "attach_cs_tools",
]

