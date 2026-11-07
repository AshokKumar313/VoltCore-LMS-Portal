"""
========================================================================================
VoltCore Apex Academia - Safe Mathematical & Boolean Expression Parser
Anna University / MIT Campus Standards (Department of Electronics Engineering)
----------------------------------------------------------------------------------------
Module: backend/safe_expression_parser.py
Security Standard: CWE-95 / CWE-94 Neutralization (Zero eval/exec)
Architecture: Whitelist-enforced Abstract Syntax Tree (AST) evaluation
========================================================================================
"""

import ast
import math
import operator
import re
from typing import Dict, Any, Union, Optional, Set, Callable


class SecurityException(ValueError):
    """Raised when an expression attempts to execute forbidden constructs."""
    pass


# Whitelist of safe binary operations
SAFE_BINARY_OPERATORS: Dict[type, Callable[[Any, Any], Any]] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.BitAnd: operator.and_,
    ast.BitOr: operator.or_,
    ast.BitXor: operator.xor,
    ast.LShift: operator.lshift,
    ast.RShift: operator.rshift,
}

# Whitelist of safe unary operations
SAFE_UNARY_OPERATORS: Dict[type, Callable[[Any], Any]] = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
    ast.Not: operator.not_,
    ast.Invert: operator.invert,
}

# Whitelist of safe comparison operations
SAFE_COMPARISON_OPERATORS: Dict[type, Callable[[Any, Any], bool]] = {
    ast.Eq: operator.eq,
    ast.NotEq: operator.ne,
    ast.Lt: operator.lt,
    ast.LtE: operator.le,
    ast.Gt: operator.gt,
    ast.GtE: operator.ge,
}

# Whitelist of safe mathematical functions
SAFE_MATH_FUNCTIONS: Dict[str, Callable[..., Any]] = {
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "asin": math.asin,
    "acos": math.acos,
    "atan": math.atan,
    "atan2": math.atan2,
    "sinh": math.sinh,
    "cosh": math.cosh,
    "tanh": math.tanh,
    "sqrt": math.sqrt,
    "exp": math.exp,
    "log": math.log,
    "log10": math.log10,
    "log2": math.log2,
    "abs": abs,
    "min": min,
    "max": max,
    "round": round,
    "pow": pow,
    "pi": math.pi,
    "e": math.e,
}


class SafeExpressionParser:
    """
    Evaluates mathematical and boolean expressions using Python's AST module.
    Enforces a strict whitelist of node types and neutralizes any attempt at code injection,
    object traversal, method invocation, or built-in access.
    """

    MAX_EXPRESSION_LENGTH = 1000
    MAX_EXPONENT = 100  # Mitigate catastrophic CPU consumption via huge powers (e.g., 999**9999)

    @classmethod
    def evaluate(
        cls,
        expression: str,
        variables: Optional[Dict[str, Any]] = None,
        allow_math_funcs: bool = True
    ) -> Any:
        """
        Safely evaluates an expression string using the AST whitelist parser.

        :param expression: Mathematical or boolean expression string
        :param variables: Dictionary of identifier -> value mappings
        :param allow_math_funcs: Whether whitelisted math functions (sin, cos, sqrt) are enabled
        :return: Evaluated numerical or boolean result
        :raises SecurityException: If forbidden AST constructs are detected
        :raises ValueError: For syntax or numerical errors
        """
        if not isinstance(expression, str):
            raise TypeError("Expression must be a string.")

        clean_expr = expression.strip()
        if not clean_expr:
            raise ValueError("Expression cannot be empty.")

        if len(clean_expr) > cls.MAX_EXPRESSION_LENGTH:
            raise SecurityException(f"Expression exceeds maximum permitted length of {cls.MAX_EXPRESSION_LENGTH} characters.")

        # Prohibit known dangerous tokens before parsing
        forbidden_patterns = [
            r"__",           # Dunder methods
            r"\bimport\b",
            r"\bopen\b",
            r"\bexec\b",
            r"\beval\b",
            r"\bgetattr\b",
            r"\bsetattr\b",
            r"\bdelattr\b",
            r"\bsubclasses\b",
            r"\bglobals\b",
            r"\blocals\b",
            r"\bcompile\b",
            r"\bbuiltins\b",
        ]
        for pattern in forbidden_patterns:
            if re.search(pattern, clean_expr, re.IGNORECASE):
                raise SecurityException(f"Expression contains forbidden pattern: '{pattern}'.")

        try:
            tree = ast.parse(clean_expr, mode="eval")
        except SyntaxError as e:
            raise ValueError(f"Syntax error in expression: {e}")

        var_env = dict(variables or {})
        return cls._eval_node(tree.body, var_env, allow_math_funcs)

    @classmethod
    def _eval_node(
        cls,
        node: ast.AST,
        var_env: Dict[str, Any],
        allow_math_funcs: bool
    ) -> Any:
        """Recursively evaluates an AST node strictly according to the whitelist."""

        # 1. Literals (Numbers, Booleans, None, Strings)
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float, bool)) or node.value is None:
                return node.value
            raise SecurityException(f"Disallowed constant type: {type(node.value).__name__}")

        # Older Python compatibility for ast.Num
        if hasattr(ast, "Num") and isinstance(node, ast.Num):
            return node.n

        # 2. Identifiers / Variables
        if isinstance(node, ast.Name):
            name = node.id
            if name == "True":
                return True
            if name == "False":
                return False
            if name == "None":
                return None
            if name in var_env:
                return var_env[name]
            if allow_math_funcs and name in SAFE_MATH_FUNCTIONS:
                val = SAFE_MATH_FUNCTIONS[name]
                if isinstance(val, (int, float)):
                    return val
            raise ValueError(f"Undefined variable or identifier: '{name}'")

        # 3. Binary Operations (+, -, *, /, **, &, |, ^, %, <<, >>)
        if isinstance(node, ast.BinOp):
            op_type = type(node.op)
            if op_type not in SAFE_BINARY_OPERATORS:
                raise SecurityException(f"Disallowed binary operator: {op_type.__name__}")

            left = cls._eval_node(node.left, var_env, allow_math_funcs)
            right = cls._eval_node(node.right, var_env, allow_math_funcs)

            # Prevent DOS via massive exponents
            if op_type == ast.Pow:
                if isinstance(right, (int, float)) and right > cls.MAX_EXPONENT:
                    raise SecurityException(f"Exponent {right} exceeds safe threshold ({cls.MAX_EXPONENT}).")

            handler = SAFE_BINARY_OPERATORS[op_type]
            try:
                return handler(left, right)
            except ZeroDivisionError:
                raise ZeroDivisionError("Division by zero in expression.")

        # 4. Unary Operations (+x, -x, not x, ~x)
        if isinstance(node, ast.UnaryOp):
            op_type = type(node.op)
            if op_type not in SAFE_UNARY_OPERATORS:
                raise SecurityException(f"Disallowed unary operator: {op_type.__name__}")

            operand = cls._eval_node(node.operand, var_env, allow_math_funcs)
            return SAFE_UNARY_OPERATORS[op_type](operand)

        # 5. Boolean Operations (and, or)
        if isinstance(node, ast.BoolOp):
            if isinstance(node.op, ast.And):
                for val_node in node.values:
                    res = cls._eval_node(val_node, var_env, allow_math_funcs)
                    if not res:
                        return res
                return res
            elif isinstance(node.op, ast.Or):
                for val_node in node.values:
                    res = cls._eval_node(val_node, var_env, allow_math_funcs)
                    if res:
                        return res
                return res
            else:
                raise SecurityException(f"Disallowed boolean operator: {type(node.op).__name__}")

        # 6. Comparison Operations (==, !=, <, <=, >, >=)
        if isinstance(node, ast.Compare):
            left = cls._eval_node(node.left, var_env, allow_math_funcs)
            for op, comparator in zip(node.ops, node.comparators):
                op_type = type(op)
                if op_type not in SAFE_COMPARISON_OPERATORS:
                    raise SecurityException(f"Disallowed comparison operator: {op_type.__name__}")
                right = cls._eval_node(comparator, var_env, allow_math_funcs)
                if not SAFE_COMPARISON_OPERATORS[op_type](left, right):
                    return False
                left = right
            return True

        # 7. Function Calls strictly within SAFE_MATH_FUNCTIONS whitelist
        if isinstance(node, ast.Call):
            if not allow_math_funcs:
                raise SecurityException("Function calls are disabled for this expression.")

            if not isinstance(node.func, ast.Name):
                raise SecurityException("Only directly named mathematical functions are allowed.")

            func_name = node.func.id
            if func_name not in SAFE_MATH_FUNCTIONS or not callable(SAFE_MATH_FUNCTIONS[func_name]):
                raise SecurityException(f"Forbidden function call: '{func_name}'.")

            # Keyword arguments are prohibited for security predictability
            if node.keywords:
                raise SecurityException("Keyword arguments are disallowed in mathematical function calls.")

            evaluated_args = [cls._eval_node(arg, var_env, allow_math_funcs) for arg in node.args]
            return SAFE_MATH_FUNCTIONS[func_name](*evaluated_args)

        # Explicitly forbid dangerous AST nodes
        # Attribute traversal: obj.attr (blocks class hierarchy traversal)
        if isinstance(node, ast.Attribute):
            raise SecurityException("Attribute access (dot notation) is strictly forbidden.")

        # Subscripts: obj[idx] (blocks dictionary/list indexing escapes)
        if isinstance(node, ast.Subscript):
            raise SecurityException("Subscript/indexing access is strictly forbidden.")

        # Any other unlisted node type
        raise SecurityException(f"Forbidden syntax node: {type(node).__name__}")


def safe_eval_boolean(expression: str, var_values: Optional[Dict[str, Any]] = None) -> int:
    """
    Specialized helper for digital electronics and SVA condition evaluation.
    Normalizes engineering syntax (A', ~, +, *, &, |, XOR, AND, OR, NOT) into standard expressions,
    then evaluates safely via SafeExpressionParser without eval/exec.

    Returns 1 if True, 0 if False.
    """
    expr = (expression or "").strip()
    if not expr:
        return 0

    values = dict(var_values or {})

    # 1. Handle trailing quote notation for negation e.g. A' -> (not A)
    for var in sorted(values.keys(), key=len, reverse=True):
        expr = re.sub(rf"\b{re.escape(var)}'", f" (not {var}) ", expr)

    # 2. Normalize keywords and operators
    expr = re.sub(r"\bAND\b", " and ", expr)
    expr = re.sub(r"\bOR\b", " or ", expr)
    expr = re.sub(r"\bNOT\b", " not ", expr)
    expr = re.sub(r"\bXOR\b", " ^ ", expr)

    # Symbol normalization
    expr = expr.replace("&&", " and ")
    expr = expr.replace("||", " or ")
    expr = expr.replace("!", " not ")
    expr = expr.replace("~", " not ")
    expr = expr.replace("+", " or ")
    expr = expr.replace("*", " and ")
    expr = expr.replace("&", " and ")
    expr = expr.replace("|", " or ")

    # Map variable values to boolean integers (0 or 1)
    normalized_vars = {}
    for k, v in values.items():
        if isinstance(v, bool):
            normalized_vars[k] = 1 if v else 0
        elif isinstance(v, (int, float)):
            normalized_vars[k] = 1 if v != 0 else 0
        else:
            normalized_vars[k] = 1 if bool(v) else 0

    try:
        res = SafeExpressionParser.evaluate(expr, normalized_vars, allow_math_funcs=False)
        return 1 if res else 0
    except Exception:
        return 0
