const PROTECTED_PREFIXES = [
  ".github/",
  ".cursor/",
  "receipts/",
  "SG-Canonical-Library/",
  "P0-",
  "P8-",
  "workers/sg-authority",
  "workers/nf-hourly-ai-circles-v1/",
];

const PROTECTED_EXACT = new Set([
  "AGENTS.md",
  "data/runtime_reality_v1.json",
  "data/sg_authority_key_pointer_v1.json",
  "data/github_automation_registry_v1.json",
  "data/automation_surface_inventory_v1.json",
]);

export function safePath(path) {
  if (!path || path.startsWith("/") || path.includes("..") || PROTECTED_EXACT.has(path)) return false;
  if (PROTECTED_PREFIXES.some((prefix) => path.startsWith(prefix))) return false;
  if (/(\.pem|\.key|\.env|secret|credential)/i.test(path)) return false;
  return /^(scripts|tests|docs|workers|language_gate|decision_language_machine_v1)\//.test(path);
}

export function validateAction(action) {
  if (!action || !["draft_pr", "issue", "noop"].includes(action.action)) {
    return { ok: false, reason: "invalid_action" };
  }
  if (action.action !== "draft_pr") return { ok: true, action };
  if (!Array.isArray(action.changes) || action.changes.length < 1 || action.changes.length > 3) {
    return { ok: false, reason: "changes_count_out_of_bounds" };
  }
  let total = 0;
  for (const change of action.changes) {
    if (!safePath(change.path)) return { ok: false, reason: `protected_path:${change.path}` };
    if (typeof change.content !== "string" || change.content.length > 24000) {
      return { ok: false, reason: `content_out_of_bounds:${change.path}` };
    }
    total += change.content.length;
  }
  if (total > 48000) return { ok: false, reason: "total_content_out_of_bounds" };
  return { ok: true, action };
}

export function deterministicReview(pr, files, checks) {
  const findings = [];
  if (!pr.draft) findings.push("candidate_is_not_draft");
  if (!String(pr.head?.ref || "").startsWith("ai-circle/")) findings.push("unexpected_head_namespace");
  if (files.length > 3) findings.push("file_count_exceeds_3");
  const delta = files.reduce(
    (sum, file) => sum + Number(file.additions || 0) + Number(file.deletions || 0),
    0,
  );
  if (delta > 800) findings.push("diff_delta_exceeds_800_lines");
  for (const file of files) {
    if (
      PROTECTED_EXACT.has(file.filename) ||
      PROTECTED_PREFIXES.some((prefix) => file.filename.startsWith(prefix)) ||
      /(\.pem|\.key|\.env|secret|credential)/i.test(file.filename)
    ) {
      findings.push(`protected_path:${file.filename}`);
    }
    if (!file.patch && file.status !== "removed") findings.push(`unreviewable_patch:${file.filename}`);
  }
  const codeChanged = files.some((file) =>
    /^(scripts|workers|language_gate|decision_language_machine_v1)\//.test(file.filename),
  );
  const testChanged = files.some((file) => /(^|\/)(test|tests)\//.test(file.filename));
  if (codeChanged && !testChanged) findings.push("code_change_without_test_change");
  const checkRuns = checks?.check_runs || [];
  const completedFailures = checkRuns.filter(
    (check) => check.status === "completed" && !["success", "neutral", "skipped"].includes(check.conclusion),
  );
  if (completedFailures.length) findings.push("failing_check_run");
  return {
    pass: findings.length === 0,
    findings,
    delta,
    checks_seen: checkRuns.map((check) => ({
      name: check.name,
      status: check.status,
      conclusion: check.conclusion,
    })),
  };
}
