from __future__ import annotations
import ast
# We only allow these variable names in expressions
ALLOWED_NAMES = {"lambda0", "n1", "n2"}
# We only allow basic arithmetic (no imports, no function calls)
ALLOWED_NODES = (
    ast.Module,
    ast.Assign,
    ast.Name,
    ast.Store,
    ast.Load,
    ast.Constant,
    ast.Expr,
    ast.BinOp,
    ast.UnaryOp,
    ast.Add,
    ast.Sub,
    ast.Mult,
    ast.Div,
    ast.Pow,
    ast.USub,
    ast.UAdd,
)


def _validate_tree(tree: ast.AST) -> None:
    for node in ast.walk(tree):
        if isinstance(node, (ast.Call, ast.Attribute, ast.Import, ast.ImportFrom)):
            raise ValueError("Disallowed syntax: calls/imports/attributes not allowed.")
        if not isinstance(node, ALLOWED_NODES):
            raise ValueError(f"Disallowed syntax node: {type(node).__name__}")


def extract_d1_d2(code: str, *, lambda0: float, n1: float, n2: float) -> dict:
    """
    Parse LLM code safely and extract numeric d1, d2.

    Allowed output format example:
        d1 = lambda0/(4*n1)
        d2 = lambda0/(4*n2)

    Only arithmetic using lambda0, n1, n2 is allowed.
    """
    tree = ast.parse(code)
    _validate_tree(tree)

    env = {"lambda0": float(lambda0), "n1": float(n1), "n2": float(n2)}
    out: dict = {}

    for stmt in tree.body:
        if not isinstance(stmt, ast.Assign):
            continue

        if len(stmt.targets) != 1 or not isinstance(stmt.targets[0], ast.Name):
            raise ValueError("Only simple assignments allowed: d1 = ..., d2 = ...")

        var = stmt.targets[0].id
        if var not in {"d1", "d2"}:
            raise ValueError("Only d1 and d2 assignments are allowed")

        expr = ast.Expression(stmt.value)
        compiled = compile(expr, "<llm_expr>", "eval")
        val = eval(compiled, {"__builtins__": {}}, env)  # no builtins

        out[var] = float(val)

    if "d1" not in out or "d2" not in out:
        raise ValueError("LLM must define both d1 and d2")

    return out