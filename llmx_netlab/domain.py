"""Domain-specific modules — the 'X' integrations (poster block 6).

code interpreter: a SAFE arithmetic evaluator (AST walk, no eval).
data analysis engine: bandwidth / transfer-time analysis.
math solver: expression results + networking unit conversions.
external API integrations: contracts by name only — nothing is called.
"""
import ast
import operator

_OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
        ast.Div: operator.truediv, ast.Pow: operator.pow, ast.Mod: operator.mod,
        ast.USub: operator.neg}


def code_interpreter(expr):
    """Evaluate a pure arithmetic expression. Anything else is refused."""
    tree = ast.parse(expr, mode="eval")

    def walk(node):
        if isinstance(node, ast.Expression):
            return walk(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
            return _OPS[type(node.op)](walk(node.left), walk(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
            return _OPS[type(node.op)](walk(node.operand))
        raise ValueError(f"not allowed in the code interpreter: {type(node).__name__}")

    return walk(tree)


def transfer_time(size_mb, bandwidth_mbps):
    """Data analysis: seconds to move size_mb over a link of bandwidth_mbps."""
    if bandwidth_mbps <= 0:
        raise ValueError("bandwidth must be positive")
    return (size_mb * 8) / bandwidth_mbps


def analyse_link(size_mb, links_mbps):
    return [{"bandwidth_mbps": b, "seconds": round(transfer_time(size_mb, b), 3)}
            for b in links_mbps]


_BITS = {"bps": 1, "kbps": 1e3, "mbps": 1e6, "gbps": 1e9}


def convert_bandwidth(value, from_unit, to_unit):
    """Math solver seat: unit conversion across bps/Kbps/Mbps/Gbps."""
    f, t = _BITS[from_unit.lower()], _BITS[to_unit.lower()]
    return value * f / t


EXTERNAL_APIS = [
    {"name": "placeholder-metrics-api", "purpose": "would export eval metrics", "status": "contract only — never called by this lab"},
    {"name": "placeholder-lookup-api", "purpose": "would enrich device data", "status": "contract only — never called by this lab"},
]
