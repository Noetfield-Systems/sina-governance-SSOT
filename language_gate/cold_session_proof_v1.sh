#!/usr/bin/env bash
# Cold-session proof: dictionary from disk only (no chat memory).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

INDEX="language_gate/dictionary_index.json"
BATCH="SG-Canonical-Library/noetfield-library/P7-DOCTRINE/NOETFIELD_DICTIONARY_BATCH_A-Z_v1.md"
SAMPLE="language_gate/test_files/cold_session_doctrine_sample_v1.md"
OUT="receipts/language-layer-rc3-cold-session-proof-2026-07-07.json"

terms="$(python3 -c "import json; print(len(json.load(open('$INDEX'))['terms']))")"
batch_sha="$(shasum -a 256 "$BATCH" | awk '{print $1}')"
index_sha="$(shasum -a 256 "$INDEX" | awk '{print $1}')"

python3 - <<PY > /tmp/cold_gate.json
import json, sys
from pathlib import Path
sys.path.insert(0, "language_gate")
from language_gate_pipeline_v1 import run_pipeline
r = run_pipeline(Path("$SAMPLE"), write=False, strict_undefined=True)
print(json.dumps(r, indent=2))
PY
decision="$(python3 -c "import json; print(json.load(open('/tmp/cold_gate.json'))['decision'])")"
dict_src="$(python3 -c "import json; print(json.load(open('/tmp/cold_gate.json'))['receipt']['dictionary_source'])")"

mkdir -p receipts
python3 - <<PY
import json
from datetime import datetime, timezone
payload = {
    "schema": "language-layer-rc3-cold-session-proof-v1",
    "at": datetime.now(timezone.utc).astimezone().isoformat(),
    "checkpoint": "LANGUAGE_LAYER_RC3_CHECKPOINT",
    "commit": "8c0293b",
    "proof": {
        "session": "cold — no prior chat context",
        "dictionary_index_terms": int("$terms"),
        "dictionary_index_sha256": "$index_sha",
        "dictionary_batch_sha256": "$batch_sha",
        "sample_file": "$SAMPLE",
        "gate_decision": "$decision",
        "dictionary_source_from_receipt": "$dict_src",
        "machine_reads_disk": "$dict_src" == "$BATCH",
    },
    "verdict": "PASS" if "$decision" in {"PASS", "PASS_WITH_REWRITE"} else "FAIL",
}
open("$OUT", "w", encoding="utf-8").write(json.dumps(payload, indent=2) + "\n")
print(json.dumps(payload, indent=2))
PY

echo "COLD_SESSION_PROOF receipt=$OUT decision=$decision terms=$terms"
