# TOOLS

## chess_pass_cli.py

A lightweight helper that produces a CHESS_PASS skeleton from JSON input.

Example:

```bash
python TOOLS/chess_pass_cli.py EXAMPLES/sample_chess_input.json
```

Or:

```bash
echo '{"mission":"Clean up Partner Access page","protected_assets":["Sign in","Create account"]}' | python TOOLS/chess_pass_cli.py
```

The CLI is heuristic. It is not a blocker. It helps agents patch risky wording before execution.
