"""Static verification that no raw, string-interpolated SQL exists anywhere
in the application. This is a regression guard, not a one-time manual
check — a future contributor adding a raw `db.execute(f"...")` for a
"quick fix" will fail this test in CI before it ever reaches a review.

The one legitimate raw-SQL call site (a static, input-free health check
"SELECT 1") is explicitly allow-listed below.
"""

import re
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parent.parent / "app"

# (file, line-content-substring) pairs that are known-safe raw SQL — must
# be a static, parameter-free string. Anything else matching the
# dangerous patterns below fails the test.
ALLOWED_RAW_SQL = {
    ("db/session.py", 'text("SELECT 1")'),
}

# Matches string-interpolated SQL execution: f-strings, %-formatting, or
# string concatenation passed to .execute()/text().
DANGEROUS_PATTERNS = [
    re.compile(r'\.execute\(\s*f["\']'),
    re.compile(r'\.execute\(\s*["\'].*["\']\s*%'),
    re.compile(r'\.execute\(\s*["\'].*["\']\s*\+'),
    re.compile(r'text\(\s*f["\']'),
]


def test_no_raw_sql_string_interpolation() -> None:
    violations: list[str] = []

    for py_file in APP_ROOT.rglob("*.py"):
        relative_path = str(py_file.relative_to(APP_ROOT))
        content = py_file.read_text(encoding="utf-8")

        for line_num, line in enumerate(content.splitlines(), start=1):
            for pattern in DANGEROUS_PATTERNS:
                if pattern.search(line):
                    allowed = any(
                        relative_path.endswith(allowed_file) and allowed_snippet in line
                        for allowed_file, allowed_snippet in ALLOWED_RAW_SQL
                    )
                    if not allowed:
                        violations.append(f"{relative_path}:{line_num}: {line.strip()}")

    assert not violations, (
        "Found raw, string-interpolated SQL (SQL injection risk). "
        "Use SQLAlchemy's ORM query builder or parameterized text() bindings instead:\n"
        + "\n".join(violations)
    )
