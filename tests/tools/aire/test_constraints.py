"""Structural enforcement of architecture-spec constraints 1 and 6 (no daemon,
no network). Asserts no aire module imports a networking or server library.
This makes the constraint mechanical, not a matter of reviewer vigilance.
"""

import ast
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[3] / "tools" / "aire"

FORBIDDEN = {
    "socket", "ssl", "http", "urllib", "ftplib", "smtplib", "telnetlib",
    "asyncio", "socketserver", "selectors", "xmlrpc",
    "requests", "aiohttp", "httpx", "flask", "fastapi", "tornado", "uvicorn",
}


class TestNoNetworkImports(unittest.TestCase):
    def test_no_forbidden_imports(self):
        offenders = []
        for py in sorted(TOOLS.glob("*.py")):
            tree = ast.parse(py.read_text())
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name.split(".")[0] in FORBIDDEN:
                            offenders.append((py.name, alias.name))
                elif isinstance(node, ast.ImportFrom):
                    root = (node.module or "").split(".")[0]
                    if root in FORBIDDEN:
                        offenders.append((py.name, node.module))
        self.assertEqual(offenders, [], f"forbidden imports found: {offenders}")


if __name__ == "__main__":
    unittest.main()
