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

const ALLOWED_ACTIONS = new Set(["draft_pr", "dispatch_job", "issue", "noop"]);
const ALLOWED_JOB_IDS = new Set([
  "commissioning_tick",
  "motor_job",
  "repair_run",
  "live_model_smoke",
]);

/**
 * Coerce common model failures into a usable action shape before hard validation.
 */
export function normalizeAction(raw, planner = {}) {
  if (!raw || typeof raw !== "object") {
    if (planner?.action === "dispatch_job" && ALLOWED_JOB_IDS.has(planner.job_id)) {
      return { action: "dispatch_job", job_id: planner.job_id, title: planner.title, rationale: planner.why };
    }
    return { action: "noop", rationale: "empty_implementer_payload" };
  }
  const action = { ...raw };
  if (!action.action && Array.isArray(action.changes) && action.changes.length) {
    action.action = "draft_pr";
  }
  if (!action.action && ALLOWED_JOB_IDS.has(action.job_id)) {
    action.action = "dispatch_job";
  }
  if (!action.action && ["draft_pr", "dispatch_job", "issue", "noop"].includes(planner?.action)) {
    action.action = planner.action;
    if (planner.job_id && !action.job_id) action.job_id = planner.job_id;
    if (planner.title && !action.title) action.title = planner.title;
    if (planner.why && !action.rationale) action.rationale = planner.why;
  }
  if (action.action === "issue" && Array.isArray(action.changes) && action.changes.length >= 1) {
    action.action = "draft_pr";
  }
  return action;
}

export function validateAction(action) {
  if (!action || !ALLOWED_ACTIONS.has(action.action)) {
    return { ok: false, reason: "invalid_action" };
  }
  if (action.action === "dispatch_job") {
    if (!ALLOWED_JOB_IDS.has(String(action.job_id || "").trim())) {
      return { ok: false, reason: "unknown_or_missing_job_id" };
    }
    return { ok: true, action };
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
