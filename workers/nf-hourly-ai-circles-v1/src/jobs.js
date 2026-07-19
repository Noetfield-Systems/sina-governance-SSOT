const DEMO_MARKERS = [
  /\bdemo\b/i,
  /\btoy\b/i,
  /\bplaceholder\b/i,
  /\bfake\b/i,
  /\bmock[-_ ]?job\b/i,
  /assert add\(2,\s*2\)\s*==\s*5/i,
  /\bred fixture\b/i,
  /\bsample[-_ ]?job\b/i,
];

export function containsDemoMarker(value) {
  const text = typeof value === "string" ? value : JSON.stringify(value || {});
  return DEMO_MARKERS.some((pattern) => pattern.test(text));
}

export function buildProductionJobContract({
  receiptId,
  repo,
  base,
  baseSha,
  action,
}) {
  return {
    schema: "nf.production-repository-job.v1",
    job_id: receiptId,
    created_at: new Date().toISOString(),
    target: {
      repo,
      base,
      exact_base_sha: baseSha,
    },
    objective: action.title,
    rationale: action.rationale,
    changes: action.changes.map((change) => change.path),
    acceptance_checks: action.tests,
    execution: {
      kind: "github_draft_pr",
      sandbox: "GitHubActionsSandbox",
      mutation_boundary: "draft_branch_only",
    },
    authority: {
      mode: "PRODUCTION_REPOSITORY_JOBS_HOLD",
      autonomous_production_mutations: "HOLD",
      permitted: ["branch", "commit", "draft_pr", "ci", "independent_check"],
      forbidden: ["merge", "deploy", "authority_change", "secret_change"],
    },
  };
}

export function productionJobBody(contract) {
  return [
    "## Production repository job",
    "",
    `**Job:** \`${contract.job_id}\``,
    `**Exact base:** \`${contract.target.exact_base_sha}\``,
    `**Repository:** \`${contract.target.repo}\``,
    "",
    contract.rationale,
    "",
    "## Changed paths",
    ...contract.changes.map((path) => `- \`${path}\``),
    "",
    "## Acceptance checks",
    ...contract.acceptance_checks.map((check) => `- ${check}`),
    "",
    "## Production boundary",
    "- Real repository branch, commit, draft PR, CI, and independent check",
    "- No synthetic fixture or fallback artifact",
    "- HOLD preserved: no autonomous merge, deploy, authority, or secret mutation",
  ].join("\n");
}
