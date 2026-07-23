#!/usr/bin/env python3
"""verify_wiring_commissioning_v1.py — deterministic enforcement for the
Wiring & Commissioning Contract v1.

Read-only over the org tree (its only write is an append-only status receipt;
disable with --no-write). Job statuses are COMPUTED from artifacts on disk;
there is no way to hand-mark a job done.

FAIL-CLOSED LOCK (hardened after adversarial review wf_722ce91b-2a6):
  * Before evaluating anything, the plan/contract/script sha256 are checked
    against receipts/WIRING_COMMISSIONING_PLAN_LOCK_v1.json.
  * A MISSING lock receipt is an ENFORCEMENT_VIOLATION (exit 3), not benign —
    so deleting the lock cannot re-open a fail-open hole. Create the lock with
    --init-lock (an explicit, git-logged act).
  * Any sha mismatch is ENFORCEMENT_VIOLATION (exit 3); no statuses reported.

FOUNDER GATES ARE NON-BYPASSABLE:
  A job whose founder_gate.required is true and whose founder receipt_glob is
  absent can NEVER compute DONE — even if its exit receipt is fabricated. It
  reports AWAITING_FOUNDER. DONE requires exit_gate AND founder receipt AND
  all deps DONE (fixpoint).

Usage:
  python3 scripts/verify_wiring_commissioning_v1.py [--root DIR] [--json]
      [--no-write] [--init-lock]
Exit: 0 ok · 2 malformed contract · 3 enforcement violation (lock).
"""
import argparse, datetime, glob as globmod, hashlib, json, os, re, subprocess, sys

DEF_ROOT = "/Users/sinakazemnezhad/Desktop/Noetfield-Systems"
HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.dirname(HERE)  # lock worktree root
SELF = os.path.abspath(__file__)
DEF_CONTRACT = os.path.join(WT, "product", "WIRING_COMMISSIONING_CONTRACT_v1.json")
PLAN = os.path.join(WT, "product", "WIRING_COMMISSIONING_PLAN_v1.md")
DEF_LOCK = os.path.join(WT, "receipts", "WIRING_COMMISSIONING_PLAN_LOCK_v1.json")
LOCKED_REL = {  # files whose integrity the lock protects (relative to WT)
    "product/WIRING_COMMISSIONING_PLAN_v1.md": PLAN,
    "product/WIRING_COMMISSIONING_CONTRACT_v1.json": DEF_CONTRACT,
    "scripts/verify_wiring_commissioning_v1.py": SELF,
}
ISO_RE = re.compile(r"^\d{4}-\d{2}-\d{2}([T ]\d{2}:\d{2}(:\d{2})?)?")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def git(repo, *args):
    try:
        r = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True, timeout=30)
        return r.returncode, r.stdout.strip()
    except Exception as e:  # noqa: BLE001 — any git failure is fail-closed NOT_PASS
        return 1, str(e)


def jget(obj, dotted):
    cur = obj
    for part in dotted.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            return None, False
    return cur, True


def _as_date(v):
    if isinstance(v, str) and ISO_RE.match(v):
        try:
            dt = datetime.datetime.fromisoformat(v.replace("Z", "+00:00").replace(" ", "T"))
            return dt.replace(tzinfo=None)  # normalize: compare wall-clock, avoid naive/aware mix
        except ValueError:
            return None
    return None


def check_pred(doc, pred):
    val, found = jget(doc, pred["path"])
    op = pred["op"]
    if op == "exists":
        return found
    if not found:
        return False
    ref = pred.get("value")
    if op == "eq":
        return val == ref
    if op == "ne":
        return val != ref
    if op in ("gte", "lte"):
        dv, dr = _as_date(val), _as_date(ref)
        if dv is not None and dr is not None:
            return dv >= dr if op == "gte" else dv <= dr
        try:
            return (val >= ref) if op == "gte" else (val <= ref)
        except TypeError:
            return False
    if op == "contains":
        try:
            return ref in val
        except TypeError:
            return False
    if op == "in":
        return val in ref
    if op == "matches":  # externally-checkable-ID predicate: regex over a string field
        return isinstance(val, str) and re.search(ref, val) is not None
    raise ValueError(f"unknown op {op}")


def eval_gate(gate, root, notes):
    t = gate["type"]
    if t == "all_of_gates":
        return all(eval_gate(g, root, notes) for g in gate["gates"])
    if t == "any_of_gates":
        return any(eval_gate(g, root, notes) for g in gate["gates"])
    if t == "file_exists":
        return all(os.path.exists(os.path.join(root, p)) for p in gate["paths"])
    if t == "file_absent":
        return not any(os.path.exists(os.path.join(root, p)) for p in gate["paths"])
    if t == "file_exists_glob":
        return bool(globmod.glob(os.path.join(root, gate["glob"]), recursive=True))
    if t == "file_contains":
        p = os.path.join(root, gate["path"])
        if not os.path.isfile(p):
            return False
        try:
            with open(p, encoding="utf-8", errors="replace") as f:
                blob = f.read()
        except OSError:
            return False
        return all(m in blob for m in gate["markers"])
    if t == "sha_match":
        paths = [os.path.join(root, p) for p in gate["paths"]]
        if not all(os.path.isfile(p) for p in paths):
            return False
        return len({sha256(p) for p in paths}) == 1
    if t == "git_synced":
        repo = os.path.join(root, gate["repo"])
        branch = gate["branch"]
        rc, cur = git(repo, "rev-parse", "--abbrev-ref", "HEAD")
        if rc != 0 or cur != branch:
            notes.append(f"{gate['repo']}: on '{cur}', want '{branch}'")
            return False
        rc1, head = git(repo, "rev-parse", "HEAD")
        rc2, remote = git(repo, "rev-parse", f"origin/{branch}")
        if rc1 or rc2 or head != remote:
            notes.append(f"{gate['repo']}: HEAD {head[:9]} != origin/{branch} {remote[:9]}")
            return False
        rc3, porc = git(repo, "status", "--porcelain")
        dirty = [l for l in porc.splitlines() if l and not l.startswith("??")]
        if rc3 or dirty:
            notes.append(f"{gate['repo']}: {len(dirty)} modified tracked file(s)")
            return False
        return True
    if t == "git_merged":
        # PASS if the branch head is an ancestor of origin/into (plain merge),
        # OR a land receipt records a merge_commit_sha that is an ancestor
        # (covers squash/rebase merges, GitHub's defaults).
        repo = os.path.join(root, gate["repo"])
        for ref in (f"origin/{gate['ref']}", gate["ref"]):
            rc, _ = git(repo, "merge-base", "--is-ancestor", ref, f"origin/{gate['into']}")
            if rc == 0:
                return True
        mrg = gate.get("merge_receipt_glob")
        if mrg:
            for m in sorted(globmod.glob(os.path.join(root, mrg), recursive=True)):
                try:
                    with open(m) as f:
                        sha = json.load(f).get("merge_commit_sha", "")
                except (OSError, json.JSONDecodeError):
                    continue
                if re.fullmatch(r"[0-9a-f]{40}", str(sha)):
                    rc, _ = git(repo, "merge-base", "--is-ancestor", sha, f"origin/{gate['into']}")
                    if rc == 0:
                        return True
        notes.append(f"{gate['repo']}: {gate['ref']} not merged into origin/{gate['into']}")
        return False
    if t == "receipt_json":
        matches = sorted(globmod.glob(os.path.join(root, gate["glob"]), recursive=True))
        if not matches:
            return False
        mode = gate.get("mode", "newest")
        if mode == "newest":
            matches = [max(matches, key=lambda p: (os.path.getmtime(p), p))]
        results = []
        for m in matches:
            try:
                with open(m) as f:
                    doc = json.load(f)
                results.append(all(check_pred(doc, p) for p in gate.get("all_of", [])))
            except (json.JSONDecodeError, OSError) as e:
                notes.append(f"unreadable receipt {m}: {e}")
                results.append(False)
        return all(results) if mode == "all" else any(results)
    raise ValueError(f"unknown gate type {t}")


def lock_check(lock_path, init):
    """Return (ok, state, violation_msg). Fail-closed on absence."""
    cur = {rel: (sha256(p) if os.path.isfile(p) else "ABSENT") for rel, p in LOCKED_REL.items()}
    if not os.path.isfile(lock_path):
        if init:
            payload = {
                "schema": "wiring_commissioning_plan_lock_v1",
                "locked_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "note": "sha256 of the three locked artifacts. Absence or mismatch = ENFORCEMENT_VIOLATION.",
                "files": cur,
            }
            with open(lock_path, "w") as f:
                json.dump(payload, f, indent=1)
            return True, "INITIALIZED", None
        return False, "MISSING", ("lock receipt absent — fail-closed. Create it with --init-lock "
                                  "(an explicit, git-logged act). A missing lock does not bypass enforcement.")
    with open(lock_path) as f:
        locked = json.load(f).get("files", {})
    for rel, want in locked.items():
        if cur.get(rel) != want:
            return False, "TAMPERED", f"{rel}\n  locked  {want}\n  on-disk {cur.get(rel)}"
    return True, "VERIFIED", None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=DEF_ROOT)
    ap.add_argument("--contract", default=DEF_CONTRACT)
    ap.add_argument("--lock", default=DEF_LOCK)
    ap.add_argument("--no-write", action="store_true")
    ap.add_argument("--init-lock", action="store_true", help="create the lock receipt from current hashes, then continue")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    ok, lstate, msg = lock_check(a.lock, a.init_lock)
    if not ok:
        print(f"ENFORCEMENT_VIOLATION [{lstate}]: {msg}", file=sys.stderr)
        return 3

    try:
        with open(a.contract) as f:
            contract = json.load(f)
        jobs = {j["job_id"]: j for j in contract["jobs"]}
    except (OSError, json.JSONDecodeError, KeyError) as e:
        print(f"MALFORMED CONTRACT: {e}", file=sys.stderr)
        return 2

    # exit gate + founder receipt presence
    exit_pass, founder_ok, gate_notes = {}, {}, {}
    for jid, job in jobs.items():
        notes = []
        try:
            exit_pass[jid] = eval_gate(job["exit_gate"], a.root, notes)
        except ValueError as e:
            print(f"MALFORMED CONTRACT ({jid}): {e}", file=sys.stderr)
            return 2
        gate_notes[jid] = notes
        fg = job.get("founder_gate", {})
        if fg.get("required") and fg.get("receipt_glob"):
            founder_ok[jid] = bool(globmod.glob(os.path.join(a.root, fg["receipt_glob"]), recursive=True))
        else:
            founder_ok[jid] = True
        for d in job.get("depends_on", []):
            if d not in jobs:
                print(f"MALFORMED CONTRACT ({jid}): unknown dep {d}", file=sys.stderr)
                return 2

    # DONE fixpoint: exit_pass AND founder_ok AND all deps DONE
    done = {jid: False for jid in jobs}
    for _ in range(len(jobs) + 1):
        changed = False
        for jid, job in jobs.items():
            v = exit_pass[jid] and founder_ok[jid] and all(done[d] for d in job.get("depends_on", []))
            if v != done[jid]:
                done[jid], changed = v, True
        if not changed:
            break

    status = {}
    for jid, job in jobs.items():
        if done[jid]:
            status[jid] = "DONE"
        elif any(not done[d] for d in job.get("depends_on", [])):
            status[jid] = "BLOCKED_DEPS"
        elif not founder_ok[jid]:
            status[jid] = "AWAITING_FOUNDER"
        else:
            status[jid] = "READY"  # deps done, founder ok, exit gate not yet satisfied

    now = datetime.datetime.now(datetime.timezone.utc)
    counts = {s: sum(1 for v in status.values() if v == s)
              for s in ("DONE", "READY", "AWAITING_FOUNDER", "BLOCKED_DEPS")}
    out = {
        "schema": "wiring_commissioning_status_v1",
        "checked_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "contract_sha256": sha256(a.contract),
        "lock_check": lstate,
        "summary": counts,
        "jobs": [{"job_id": jid, "phase": jobs[jid]["phase"], "status": status[jid],
                  "title": jobs[jid]["title"][:100],
                  **({"notes": gate_notes[jid]} if gate_notes[jid] else {})} for jid in jobs],
    }

    if a.json:
        print(json.dumps(out, indent=1))
    else:
        print(f"Wiring & Commissioning status @ {out['checked_at']}  (lock: {lstate})")
        print(f"  DONE {counts['DONE']}  READY {counts['READY']}  "
              f"AWAITING_FOUNDER {counts['AWAITING_FOUNDER']}  BLOCKED_DEPS {counts['BLOCKED_DEPS']}")
        cur = None
        for jid in jobs:
            if jobs[jid]["phase"] != cur:
                cur = jobs[jid]["phase"]
                print(f"\n== {cur} ==")
            mark = {"DONE": "✅", "READY": "▶️ ", "AWAITING_FOUNDER": "🔒", "BLOCKED_DEPS": "⛔"}[status[jid]]
            print(f"  {mark} {jid} [{status[jid]}] {jobs[jid]['title'][:92]}")
            for n in gate_notes[jid][:2]:
                print(f"        · {n}")

    if not a.no_write:
        dest = os.path.join(WT, "receipts", f"WIRING_COMMISSIONING_STATUS_{now.strftime('%Y%m%dT%H%M%SZ')}.json")
        with open(dest, "w") as f:
            json.dump(out, f, indent=1)
        print(f"\nstatus receipt: {dest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
