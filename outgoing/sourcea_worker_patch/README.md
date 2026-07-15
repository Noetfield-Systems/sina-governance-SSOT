SourceA Worker patch: Signal Factory v1

This folder contains the Signal Factory v1 skill scaffold to be applied to the SourceA Worker repository.

Files included:
 - SKILL.md
 - receipt_schema.json
 - tests/test_signal_factory_v1.py

Apply instructions (in SourceA Worker repo):
1. Copy the files into the worker repo under `skills/signal-factory-v1/`.
2. Run `python3 -m json.tool skills/signal-factory-v1/receipt_schema.json` to validate JSON.
3. Run `python3 skills/signal-factory-v1/tests/test_signal_factory_v1.py` to run local checks.
4. Commit and open a PR in the SourceA Worker repository targeting its main branch.

Alternatively, from this machine, run `./apply_patch.sh /path/to/sourcea/repo` which will copy files into the target repo (no commits).