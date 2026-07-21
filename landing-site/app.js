(() => {
  const statusDot = document.getElementById("statusDot");
  const statusText = document.getElementById("statusText");
  const runButton = document.getElementById("runwayRun");
  const resetButton = document.getElementById("runwayReset");
  const streamRoot = document.getElementById("jobStream");
  const runIdBadge = document.getElementById("runIdBadge");
  const snapshotLine = document.getElementById("snapshotLine");
  const receiptBody = document.getElementById("receiptBody");
  const scenarioButtons = document.querySelectorAll(".scenario-btn");
  const revealTargets = document.querySelectorAll("[data-reveal]");
  const scenarioSummary = document.getElementById("scenarioSummary");
  const scenarioPain = document.getElementById("scenarioPain");
  const scenarioSolution = document.getElementById("scenarioSolution");
  const scenarioTarget = document.getElementById("scenarioTarget");
  const scenarioCost = document.getElementById("scenarioCost");
  const scenarioRetries = document.getElementById("scenarioRetries");
  const scenarioTokens = document.getElementById("scenarioTokens");
  const scenarioCalls = document.getElementById("scenarioCalls");
  const scenarioRisk = document.getElementById("scenarioRisk");
  const scenarioFallback = document.getElementById("scenarioFallback");
  const trustLine = document.getElementById("trustLine");
  const runState = document.getElementById("runState");
  const runNodes = document.getElementById("runNodes");
  const runChecksPassed = document.getElementById("runChecksPassed");
  const runRetriesUsed = document.getElementById("runRetriesUsed");
  const runConfidence = document.getElementById("runConfidence");
  const runLatency = document.getElementById("runLatency");
  const copyReceipt = document.getElementById("copyReceipt");
  const copyReceiptHint = document.getElementById("copyReceiptHint");

  const scenarioFeed = {
    decision: {
      id: "decision-brief",
      name: "Decision brief",
      runType: "Decision brief",
      summary:
        "A constrained decision brief from multiple notes is synthesized into ranked recommendations with schema checks.",
      pain:
        "Unstructured notes and date drift produce inconsistent outputs with low auditability.",
      solution:
        "Lock goal contracts and enforce schema checks across planner and verifier stages.",
      reliability_target: 99.0,
      cost_cap_usd: 0.42,
      expected_retries: 0,
      expected_tokens: 780,
      expected_model_calls: 2,
      risk_envelope: "Low — single source normalization and structured policy checks.",
      fallback_policy: "Retry failed segments once; escalate if schema mismatch exceeds threshold.",
      provider_failover: false,
      failure_modes: ["Unstructured context", "Ambiguous date formats", "Weak acceptance criteria"],
      best_solution:
        "Contract-first intake with strict schema checks before each planner/verifier stage.",
      steps: [
        {
          status: "ok",
          step: "goal_contract",
          phase: "Define",
          text: "Goal contract validated. Scope, deadlines, and proof criteria are locked.",
          elapsedMs: 450
        },
        {
          status: "ok",
          step: "receipt_gate",
          phase: "Plan",
          text: "Cost preflight passed. Spend cap loaded and escalation boundaries set.",
          elapsedMs: 520
        },
        {
          status: "ok",
          step: "planner",
          phase: "Plan",
          text: "Deterministic execution graph generated with 5 immutable nodes.",
          elapsedMs: 660
        },
        {
          status: "warn",
          phase: "Execute",
          step: "normalizer",
          text: "Context normalization raised one warning: ambiguous date format adjusted.",
          elapsedMs: 940
        },
        {
          status: "ok",
          step: "verifier",
          phase: "Verify",
          text: "Schema and lineage checks passed for all candidate outputs.",
          elapsedMs: 520
        },
        {
          status: "ok",
          step: "receipt",
          phase: "Receipt",
          text: "Receipt generated with ranked recommendations and proof bundle IDs.",
          elapsedMs: 490
        }
      ]
    },
    rfp: {
      id: "rfp-response-pack",
      name: "RFP response pack",
      runType: "RFP response pack",
      summary:
        "Compliance-heavy RFP responses are assembled into a structured, evidence-backed draft with policy checks.",
      pain:
        "Teams lose hours fixing format, policy and source-limits errors after generation.",
      solution:
        "Preflight policy gates plus evidence retrieval and retry logic on unstable sources.",
      reliability_target: 98.4,
      cost_cap_usd: 0.31,
      expected_retries: 1,
      expected_tokens: 1250,
      expected_model_calls: 3,
      risk_envelope: "Medium — appendix drift and deadline-bound sources.",
      fallback_policy: "Retry failed source calls, then switch to mirror source and resume remaining steps.",
      provider_failover: true,
      failure_modes: ["Source timeout", "Appendix link drift", "Policy edge case"],
      best_solution:
        "Policy-aware preflight with timeout-aware retries and evidence fallback preserves reproducibility.",
      steps: [
        {
          status: "ok",
          phase: "Define",
          step: "goal_contract",
          text: "RFP intake accepted. Required sections and proof checkpoints are locked.",
          elapsedMs: 420
        },
        {
          status: "ok",
          phase: "Plan",
          step: "receipt_gate",
          text: "Budget preflight passed: 0.31 USD estimated cap.",
          elapsedMs: 600
        },
        {
          status: "ok",
          phase: "Plan",
          step: "planner",
          text: "Compliance outline generated with references and risk tags.",
          elapsedMs: 700
        },
        {
          status: "fail",
          phase: "Execute",
          step: "source_fetch",
          text: "Primary appendix source returned malformed payload and failed to parse.",
          elapsedMs: 760,
          recovered: true
        },
        {
          status: "warn",
          phase: "Execute",
          step: "source_retry",
          text: "Failover to mirror endpoint completed and payload was normalized successfully.",
          elapsedMs: 820
        },
        {
          status: "ok",
          phase: "Verify",
          step: "verifier",
          text: "Replay check passed after retry. All required fields are present.",
          elapsedMs: 690
        },
        {
          status: "ok",
          phase: "Receipt",
          step: "receipt",
          text: "Receipt contains warning context, fallback source index, and acceptance hash.",
          elapsedMs: 520
        }
      ]
    },
    spreadsheet: {
      id: "spreadsheet-policy-cleanup",
      name: "Spreadsheet + policy cleanup",
      runType: "Spreadsheet cleanup",
      summary:
        "Operational spreadsheets are normalized with deterministic rules and policy checks to remove silent drift.",
      pain:
        "Manual cleanup causes inconsistent row ordering, duplicate keys, and non-reproducible diffs.",
      solution:
        "Deterministic transforms plus policy checks and checksum-based verification.",
      reliability_target: 99.7,
      cost_cap_usd: 0.11,
      expected_retries: 0,
      expected_tokens: 410,
      expected_model_calls: 2,
      risk_envelope: "Very low — deterministic transforms with immutable diff output.",
      fallback_policy: "If checksum mismatch occurs, halt and return diff preview for manual review.",
      provider_failover: false,
      failure_modes: ["Inconsistent row format", "Duplicate keys", "Float precision drift"],
      best_solution:
        "Row-level deterministic rules with checksum replay and immutable patch identifiers.",
      steps: [
        {
          status: "ok",
          phase: "Define",
          step: "goal_contract",
          text: "Input schema and required fields resolved, including policy columns.",
          elapsedMs: 390
        },
        {
          status: "ok",
          phase: "Plan",
          step: "receipt_gate",
          text: "Cost and timeout limits confirmed. Non-destructive mode is enabled.",
          elapsedMs: 470
        },
        {
          status: "ok",
          phase: "Plan",
          step: "planner",
          text: "Execution plan generated: dedupe, normalize, validate, package.",
          elapsedMs: 640
        },
        {
          status: "warn",
          phase: "Execute",
          step: "policy_check",
          text: "One policy exception was detected and annotated for operator review.",
          elapsedMs: 740
        },
        {
          status: "ok",
          phase: "Verify",
          step: "verifier",
          text: "Checksum and row-level diff checks passed, policy rule tags preserved.",
          elapsedMs: 590
        },
        {
          status: "ok",
          phase: "Receipt",
          step: "receipt",
          text: "Receipt stored with reproducible patch IDs and deterministic diff payload.",
          elapsedMs: 520
        }
      ]
    },
    complex_api: {
      id: "enterprise-api-workflow",
      name: "Complex API workflow",
      runType: "Complex API workflow",
      summary:
        "A single request composes a decision pack from CRM, pricing feeds, and policy sources.",
      pain:
        "Partial outages and schema drift cause mixed failures and untraceable reruns.",
      solution:
        "Use fan-in stages, scoped retries, provider fallback, and schema replay before final output.",
      reliability_target: 99.2,
      cost_cap_usd: 1.18,
      expected_retries: 2,
      expected_tokens: 1830,
      expected_model_calls: 4,
      risk_envelope: "High — multi-source outages and payload variance.",
      fallback_policy: "Retry failed partitions only; failover provider only for regional outages.",
      provider_failover: true,
      failure_modes: ["Provider timeout", "Schema drift", "Regional outage", "Duplicate records"],
      best_solution:
        "Staged fan-in with targeted retries and full replay checks for every partition.",
      steps: [
        {
          status: "ok",
          phase: "Define",
          step: "goal_contract",
          text: "Contract locked: 17 sources, required evidence fields, and zero-loss policy.",
          elapsedMs: 390
        },
        {
          status: "ok",
          phase: "Plan",
          step: "receipt_gate",
          text: "Preflight passed. Spend cap set and time budgets allocated by provider.",
          elapsedMs: 520
        },
        {
          status: "ok",
          phase: "Plan",
          step: "planner",
          text: "Execution graph built: parallel fetch, weighted merge, normalize, verify, package.",
          elapsedMs: 680
        },
        {
          status: "ok",
          phase: "Execute",
          step: "source_fetch",
          text: "Primary CRM and pricing sources responded within budgets; one region returned schema variant.",
          elapsedMs: 760
        },
        {
          status: "fail",
          phase: "Execute",
          step: "record_validate",
          text: "Schema variant produced duplicate record identifiers. Partition is isolated and retried.",
          elapsedMs: 900,
          recovered: true
        },
        {
          status: "warn",
          phase: "Execute",
          step: "retry",
          text: "Recovery path started: invalid partition replayed with deterministic sanitizer.",
          elapsedMs: 810
        },
        {
          status: "warn",
          phase: "Execute",
          step: "fallback",
          text: "Provider failover completed. Alternative endpoint returned complete dataset.",
          elapsedMs: 940
        },
        {
          status: "ok",
          phase: "Verify",
          step: "verifier",
          text: "Replay checks passed. Coverage reached 100% and hashes are stable.",
          elapsedMs: 690
        },
        {
          status: "ok",
          phase: "Receipt",
          step: "receipt",
          text: "Final receipt includes evidence index, retry log, and failover summary.",
          elapsedMs: 560
        }
      ]
    },
    webpage: {
      id: "webpage-build-deploy",
      name: "Webpage build + deploy",
      runType: "webpage-build-deploy",
      summary:
        "Compile a bounded webpage graph, execute deterministic-first jobs, verify HTML/CSS artifacts, and emit a canonical receipt.",
      pain: "Landing pages ship without execution proof or cost envelopes.",
      solution: "HDIR webpage-build-deploy lane with Runway projection and receipts.",
      reliability_target: 97.0,
      cost_cap_usd: 1.5,
      expected_retries: 1,
      expected_tokens: 1200,
      expected_model_calls: 8,
      risk_envelope: "Moderate — bounded publish with remote verification gates.",
      fallback_policy: "Escalate one controlled tier failure; deny unbounded escalation.",
      provider_failover: true,
      failure_modes: ["missing_viewport", "broken_internal_links", "provider_timeout"],
      best_solution: "Keep T0 majority and project only authoritative HDIR sequences.",
      steps: [
        {
          status: "ok",
          phase: "Requirements",
          step: "normalize_text",
          text: "Goal normalized into webpage requirements contract.",
          elapsedMs: 420
        },
        {
          status: "ok",
          phase: "Build",
          step: "build_html_document",
          text: "index.html artifact generated with hero/proof/cta sections.",
          elapsedMs: 640
        },
        {
          status: "ok",
          phase: "Verification",
          step: "verify_html_structure",
          text: "Viewport, sections, and internal links verified.",
          elapsedMs: 520
        },
        {
          status: "ok",
          phase: "Receipt",
          step: "receipt",
          text: "Canonical HDIR receipt projected into the Runway cockpit.",
          elapsedMs: 480
        }
      ]
    }
  };

  const runwayConfig = window.__RUNWAY__ || { mode: "demo", apiBaseUrl: "", contractVersion: "runway.v1" };
  const runwayModeBadge = document.getElementById("runwayModeBadge");
  const demoProvider =
    typeof window.DemoRunwayProvider === "function" ? new window.DemoRunwayProvider(scenarioFeed) : null;
  let liveProvider =
    typeof window.LiveRunwayProvider === "function"
      ? new window.LiveRunwayProvider({
          apiBaseUrl: runwayConfig.apiBaseUrl,
          contractVersion: runwayConfig.contractVersion || "runway.v1",
          tenantId: runwayConfig.tenantId || "tenant-runway-staging"
        })
      : null;

  function normalizeMode(value) {
    const candidate = String(value || "").toLowerCase();
    if (candidate === "live") return "live";
    if (candidate === "offline") return "offline";
    return "demo";
  }

  function resolveModeRequested() {
    const urlMode = new URLSearchParams(window.location.search).get("runwayMode") ||
      new URLSearchParams(window.location.search).get("runway_mode") ||
      new URLSearchParams(window.location.search).get("mode");

    return normalizeMode(urlMode || runwayConfig.mode || "demo");
  }

  function hasLiveBackendConnection(stateValue) {
    const state = String(stateValue || "").toLowerCase();
    return (
      state === "connected" ||
      state === "ok" ||
      state === "healthy" ||
      state === "live" ||
      state === "true" ||
      state === "1"
    );
  }

  function deriveContractVersions(payload) {
    const fallback = {
      frontend: runwayConfig.contractVersion || "runway.v1",
      kernel: "runway.v1"
    };

    if (!payload || typeof payload !== "object") {
      return fallback;
    }

    if (typeof payload.contract_version === "string" && payload.contract_version.trim()) {
      fallback.frontend = payload.contract_version;
    }
    if (typeof payload.contractVersion === "string" && payload.contractVersion.trim()) {
      fallback.frontend = payload.contractVersion;
    }
    if (typeof payload.contracts === "object" && payload.contracts && typeof payload.contracts.frontend === "string") {
      fallback.frontend = payload.contracts.frontend;
    }

    if (Array.isArray(payload.runway_contract_versions) && payload.runway_contract_versions.length) {
      fallback.kernel = String(payload.runway_contract_versions[0] || "runway.v1");
      return fallback;
    }
    if (Array.isArray(payload.runwayContractVersions) && payload.runwayContractVersions.length) {
      fallback.kernel = String(payload.runwayContractVersions[0] || "runway.v1");
      return fallback;
    }
    if (Array.isArray(payload.contractVersions) && payload.contractVersions.length) {
      fallback.kernel = String(payload.contractVersions[0] || "runway.v1");
      return fallback;
    }

    if (typeof payload.kernel === "string" && payload.kernel.trim()) {
      fallback.kernel = payload.kernel;
    }
    if (typeof payload.runway_contract_version === "string" && payload.runway_contract_version.trim()) {
      fallback.kernel = payload.runway_contract_version;
    }

    return fallback;
  }

  function deriveContractVersion(payload) {
    if (!payload || typeof payload !== "object") {
      return runwayConfig.contractVersion || "runway.v1";
    }

    if (typeof payload.contract_version === "string" && payload.contract_version.trim()) {
      return payload.contract_version;
    }
    if (typeof payload.contractVersion === "string" && payload.contractVersion.trim()) {
      return payload.contractVersion;
    }
    if (typeof payload.contract === "string" && payload.contract.trim()) {
      return payload.contract;
    }

    const versions = deriveContractVersions(payload);
    return versions.frontend || runwayConfig.contractVersion || "runway.v1";
  }

  function makeLiveProvider(apiBaseUrl, contractVersion, tenantId) {
    if (!apiBaseUrl || typeof window.LiveRunwayProvider !== "function") {
      return null;
    }

    if (
      liveProvider &&
      !liveProvider.offline &&
      liveProvider.apiBaseUrl === apiBaseUrl &&
      (liveProvider.contractVersion || "runway.v1") === (contractVersion || "runway.v1") &&
      liveProvider.tenantId === (tenantId || "tenant-runway-staging")
    ) {
      return liveProvider;
    }

    liveProvider = new window.LiveRunwayProvider({
      apiBaseUrl,
      contractVersion: contractVersion || "runway.v1",
      tenantId: tenantId || "tenant-runway-staging"
    });

    return liveProvider;
  }

  function applyModeBadge(mode) {
    if (!runwayModeBadge) {
      return;
    }

    const normalized = normalizeMode(mode);
    const modeText = normalized === "live" ? "LIVE" : normalized === "offline" ? "OFFLINE" : "DEMO";
    runwayModeBadge.textContent = modeText;

    runwayModeBadge.classList.remove("mode-live", "mode-demo", "mode-offline");
    runwayModeBadge.classList.add(
      modeText === "LIVE" ? "mode-live" : modeText === "OFFLINE" ? "mode-offline" : "mode-demo"
    );
  }

  function getExecutionContext() {
    const requestedMode = resolveModeRequested();
    const liveRuntimeProvider = requestedMode === "live"
      ? makeLiveProvider(
          runwayConfig.apiBaseUrl,
          runwayConfig.contractVersion || "runway.v1",
          runwayConfig.tenantId || "tenant-runway-staging"
        )
      : null;

    if (requestedMode === "live" && liveRuntimeProvider && !liveRuntimeProvider.offline) {
      applyModeBadge("live");
      return { mode: "live", provider: liveRuntimeProvider, source: "hdir-gateway", sourceInfo: liveRuntimeProvider.getModeLabel() };
    }

    if (requestedMode === "live") {
      applyModeBadge("offline");
      return { mode: "offline", provider: null, source: "local-simulator", sourceInfo: "OFFLINE" };
    }

    applyModeBadge("demo");
    return { mode: "demo", provider: demoProvider, source: "local-simulator", sourceInfo: "local-simulator" };
  }

  let activeScenario = "decision";
  let running = false;
  let latestReceiptText = "";

  const currencyFormatter = new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 2
  });

  function normalizeStatus(value) {
    if (value === "warn" || value === "warning" || value === "recoverable_issue") {
      return "warn";
    }

    if (value === "fail" || value === "failed" || value === "error" || value === "timeout") {
      return "fail";
    }

    return "ok";
  }

  function modeLabel(value) {
    const normalized = normalizeMode(value);
    if (normalized === "live") {
      return "LIVE";
    }
    if (normalized === "offline") {
      return "OFFLINE";
    }
    return "DEMO";
  }

  function toVerificationFlag(value) {
    if (!value || typeof value !== "object") {
      return null;
    }

    return {
      ...(value.passed !== undefined ? { passed: value.passed } : {}),
      ...(value.verifiedAt ? { verifiedAt: value.verifiedAt } : {}),
      ...(value.runId ? { runId: value.runId } : {}),
      status: value.status || value.verdict || (value.passed ? "PASS" : "UNKNOWN"),
      source: value.source || "runway.v1"
    };
  }

  function eventStatusFromStep(stepStatus, isRecoveredFailure) {
    if (stepStatus === "fail" && isRecoveredFailure) {
      return "warn";
    }

    if (stepStatus === "warn") {
      return "warn";
    }

    if (stepStatus === "fail") {
      return "fail";
    }

    return "ok";
  }

  function formatCurrency(value) {
    const numeric = Number.isFinite(Number(value)) ? Number(value) : 0;
    return currencyFormatter.format(numeric);
  }

  function simpleHash(input) {
    const source = String(input || "");
    let hash = 2166136261;
    for (let i = 0; i < source.length; i += 1) {
      hash ^= source.charCodeAt(i);
      hash = Math.imul(hash, 16777619) >>> 0;
    }
    return hash.toString(16).padStart(8, "0");
  }

  function sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  function formatMs(value) {
    if (!Number.isFinite(value) || value < 0) {
      return "--ms";
    }
    return `${Math.max(0, Math.round(value))}ms`;
  }

  function setStatus(message, tone = "ok") {
    statusText.textContent = message;
    if (runState) {
      runState.textContent = message;
    }

    const toneColor =
      tone === "ok"
        ? "var(--ok)"
        : tone === "warn"
          ? "var(--warning)"
          : "var(--bad)";

    statusDot.style.background = toneColor;
    statusDot.style.boxShadow = `0 0 12px ${toneColor}`;
  }

  function emitRunEvent(detail) {
    window.dispatchEvent(new CustomEvent("runwayRun", { detail }));
  }

  function renderTimestamp(baseMs) {
    return `+${String(Math.max(0, Date.now() - baseMs)).padStart(4, "0")}ms`;
  }

  function computeReliability(profile, counts, elapsedSeconds) {
    const warnPenalty = counts.warn * 1.4;
    const failPenalty = counts.fail * 14;
    const latencyPenalty = Math.max(0, elapsedSeconds - 6.5) * 1.4;
    const base = profile.reliability_target || 98;
    const achieved = Math.max(0, Math.min(100, base - warnPenalty - failPenalty - latencyPenalty));

    return {
      target: Number(base.toFixed(2)),
      achieved: Number(achieved.toFixed(2)),
      target_gap: Number((base - achieved).toFixed(2)),
      passRate: profile.steps
        ? Number((((counts.ok || counts.passed || 0) / Math.max(profile.steps.length, 1)) * 100).toFixed(1))
        : 0
    };
  }

  function createEntry(entry, index, total, startMs) {
    if (streamRoot.classList.contains("loading")) {
      const skeleton = streamRoot.querySelector(".stream-skeleton");
      if (skeleton) {
        skeleton.remove();
      }
      streamRoot.classList.remove("loading");
    }

    const row = document.createElement("article");
    row.className = `stream-entry ${entry.status}`;

    const phase = document.createElement("span");
    phase.className = "stream-phase";
    phase.textContent = entry.phase || entry.step;

    const text = document.createElement("p");
    text.className = "stream-text";
    text.textContent = entry.text;

    const timing = document.createElement("span");
    timing.className = "stream-timing";
    timing.textContent = `${index + 1}/${total} · ${entry.step} · ${renderTimestamp(startMs)}`;

    row.appendChild(phase);
    row.appendChild(text);
    row.appendChild(timing);
    streamRoot.appendChild(row);
    row.scrollIntoView({ behavior: "smooth", block: "end" });
  }

  function countTimelineStatus(timeline) {
    const counts = { ok: 0, warn: 0, fail: 0, total: timeline.length };
    timeline.forEach((entry) => {
      if (entry && entry.status === "warn") {
        counts.warn += 1;
      } else if (entry && entry.status === "fail") {
        if (entry.recovered) {
          counts.warn += 1;
        } else {
          counts.fail += 1;
        }
      } else {
        counts.ok += 1;
      }
    });
    return counts;
  }

  function resolveReceiptCostFromKernel(receiptPayload, snapshot, feed, profile) {
    const fallback = Number(profile && profile.cost_cap_usd ? profile.cost_cap_usd : snapshot.estimated_cost_usd || 0);
    const payload =
      receiptPayload && typeof receiptPayload === "object"
        ? (receiptPayload.payload || receiptPayload)
        : {};

    const candidate =
      Number(payload.costActual) ||
      Number(payload.cost_actual_usd) ||
      Number(payload.cost?.actual_usd) ||
      Number(payload.cost?.spent_usd) ||
      Number(payload.cost?.amount) ||
      Number(payload.spent_usd) ||
      Number(payload.amount) ||
      fallback;

    return Number(Number.isFinite(candidate) ? candidate : fallback);
  }

  function deriveLiveOutcome(snapshot, counts) {
    if (!snapshot || !snapshot.status) {
      return counts.fail > 0 ? "FAIL" : counts.warn > 0 ? "PASS_WITH_WARN" : "PASS";
    }

    if (snapshot.status === "COMPLETED") {
      return counts.fail > 0 ? "PASS_WITH_WARN" : "PASS";
    }

    if (snapshot.status === "FAILED" || snapshot.status === "BLOCKED") {
      return "FAIL";
    }

    if (snapshot.status === "REVIEW_REQUIRED") {
      return "PASS_WITH_WARN";
    }

    return "PASS_WITH_WARN";
  }

  function buildLiveKernelReceipt(runId, snapshot, timeline, profile, runResult) {
    const baseProfile = profile || scenarioFeed.webpage;
    const safeTimeline = Array.isArray(timeline) ? timeline : [];
    const counts = countTimelineStatus(safeTimeline);
    const verifiedAt = snapshot.updated_at ? new Date(snapshot.updated_at).toISOString() : new Date().toISOString();
    const expectedCost = Number(snapshot.estimated_cost_usd || baseProfile.cost_cap_usd || 0);
    const costActual = resolveReceiptCostFromKernel(runResult, snapshot, safeTimeline, baseProfile);
    const receiptPayload =
      runResult && typeof runResult === "object" && typeof runResult.payload === "object" ? runResult.payload : runResult;
    const artifactUrl = snapshot.artifact_url || (Array.isArray(snapshot.artifact_urls) ? snapshot.artifact_urls[0] : null);
    const artifactHash = snapshot.artifact_hash || snapshot.artifacts_hash || null;
    const artifactNames = Array.isArray(snapshot.artifact_names) ? snapshot.artifact_names : [];
    const checksIdentified = Array.isArray(receiptPayload?.checks_identified)
      ? receiptPayload.checks_identified
      : Array.isArray(receiptPayload?.checks)
        ? receiptPayload.checks
        : baseProfile.failure_modes || [];
    const outcome = deriveLiveOutcome(snapshot, counts);
    const rawReliability = Number.isFinite(Number(snapshot.reliability)) ? Number(snapshot.reliability) : null;
    const profileReliability = Number.isFinite(Number(baseProfile.reliability_target))
      ? Number(baseProfile.reliability_target)
      : null;
    const snapshotReliability01 =
      rawReliability === null || !Number.isFinite(rawReliability)
        ? null
        : rawReliability > 1
          ? rawReliability / 100
          : rawReliability;
    const reliabilityTarget01 =
      profileReliability === null || !Number.isFinite(profileReliability)
        ? null
        : profileReliability > 1
          ? profileReliability / 100
          : profileReliability;
    const effectiveReliability01 = snapshotReliability01 === null ? reliabilityTarget01 || 0 : snapshotReliability01;

    return {
      run_id: runId,
      runId,
      scenario_id: baseProfile.id,
      result: outcome,
      outputs: {
        label: baseProfile.runType || baseProfile.summary,
        summary: snapshot.goal || baseProfile.summary,
        checks_identified: checksIdentified,
        timeline_count: safeTimeline.length,
        artifact: artifactUrl || null,
        artifact_url: artifactUrl || null,
        artifact_hash: artifactHash || null,
        artifacts: artifactNames,
        artifact_count: artifactNames.length
      },
      hdir_execution_id: snapshot.hdir_execution_id || null,
      checks: {
        total: Number.isFinite(snapshot.jobs_total) && snapshot.jobs_total > 0 ? snapshot.jobs_total : safeTimeline.length || 0,
        passed: Number.isFinite(snapshot.jobs_completed)
          ? snapshot.jobs_completed
          : Math.max(0, Math.max(snapshot.jobs_total || 0, safeTimeline.length) - counts.fail - counts.warn),
        recoverable: counts.warn,
        failed: counts.fail,
        recovered_failures: safeTimeline.filter((entry) => entry.status === "fail" && entry.recovered).length,
      },
      costEstimated: Number(expectedCost.toFixed(4)),
      cost_estimated: Number(expectedCost.toFixed(4)),
      costActual: Number(costActual.toFixed ? costActual.toFixed(4) : costActual),
      cost_actual: Number(costActual.toFixed ? costActual.toFixed(4) : costActual),
      verifiedAt,
      source: "hdir",
      receipt_id: snapshot.receipt_id || undefined,
      contract_version: snapshot.contract_version || runwayConfig.contractVersion || "runway.v1",
      runway_contract_versions: snapshot.runway_contract_versions || {
        frontend: runwayConfig.contractVersion || "runway.v1",
        kernel: "runway.v1"
      },
      reliability: {
        target: Number(((reliabilityTarget01 || effectiveReliability01 || 0) * 100).toFixed(2)),
        achieved: Number((Math.max(0, Math.min(1, effectiveReliability01 || 0)) * 100).toFixed(2)),
      },
      risk: baseProfile.risk_envelope,
      fallback_policy: baseProfile.fallback_policy,
      timeline: safeTimeline.map((entry, idx) => ({
        timeline_id: `${runId}-n${idx + 1}`,
        step_index: idx,
        phase: entry.phase,
        step: entry.step,
        status: entry.status === "ok" ? "pass" : entry.status === "warn" ? "recoverable_issue" : "fail",
        note: entry.text,
        recovered: !!entry.recovered,
        elapsed_ms: Number.isFinite(entry.elapsedMs) ? entry.elapsedMs : 0,
      })),
      signed_receipt_id: snapshot.receipt_id || `hdir-${simpleHash(`${runId}|${safeTimeline.length}|${Date.now()}`)}`,
    };
  }

  function buildReceipt(timeline, startTime, elapsedSeconds, counts, runId, profile, sourceInfo) {
    const recoveredFailureCount = timeline.filter((entry) => entry.status === "fail" && entry.recovered).length;
    const terminalFailCount = timeline.filter((entry) => entry.status === "fail" && !entry.recovered).length;
    const outcome =
      terminalFailCount > 0
        ? "FAIL"
        : counts.warn > 0 || recoveredFailureCount > 0
          ? "PASS_WITH_WARN"
          : "PASS";

    const reliability = computeReliability(profile, counts, elapsedSeconds);
    const retryCount = timeline.filter((entry) => entry.step === "retry").length;
    const warningCount = counts.warn;
    const expectedCost = Number(profile.cost_cap_usd || 0);
    const retryPenalty = retryCount * 0.07;
    const warningPenalty = warningCount * 0.03;
    const recoveredPenalty = recoveredFailureCount * 0.04;
    const elapsedPenalty = Math.max(0, elapsedSeconds / 1200);
    const costActual = Number(
      (expectedCost * (1 + retryPenalty + warningPenalty + recoveredPenalty + elapsedPenalty)).toFixed(4)
    );

    const stepTrace = timeline.map((entry, idx) => ({
      timeline_id: `${runId}-n${idx + 1}`,
      step_index: idx,
      phase: entry.phase,
      step: entry.step,
      status:
        entry.status === "ok"
          ? "pass"
          : entry.status === "warn"
            ? "recoverable_issue"
            : entry.recovered
              ? "recovered_issue"
              : "fail",
      note: entry.text,
      recovered: !!entry.recovered,
      elapsed_ms: Number.isFinite(entry.elapsedMs) ? entry.elapsedMs : 0
    }));

    const outcomeSummary = {
      run_id: runId,
      scenario_id: profile.id,
      result: outcome,
      outputs: {
        label: profile.runType,
        summary: profile.summary,
        checks_identified: profile.failure_modes || [],
        timeline_count: timeline.length
      },
      checks: {
        total: timeline.length,
        passed: counts.ok,
        recoverable: counts.warn,
        failed: terminalFailCount,
        recovered_failures: recoveredFailureCount
      },
      costEstimated: Number(expectedCost.toFixed(4)),
      cost_estimated: Number(expectedCost.toFixed(4)),
      costActual,
      cost_actual: costActual,
      verifiedAt: new Date(startTime).toISOString(),
      verified_at: new Date(startTime).toISOString(),
      source: sourceInfo,
      reliability,
      risk: profile.risk_envelope,
      fallback_policy: profile.fallback_policy,
      timeline: stepTrace,
      signed_receipt_id: `r-${simpleHash(`${runId}|${stepTrace.length}|${Math.round(elapsedSeconds * 1000)}|${costActual}`)}`
    };

    const finalReceipt = {
      runwayRun: {
        runId,
        scenarioId: profile.id,
        phase: "receipt",
        status: outcome,
        stepIndex: timeline.length,
        elapsedMs: Number((elapsedSeconds * 1000).toFixed(0)),
        cost: costActual
      },
      receipt: outcomeSummary
    };

    const serializedReceipt = JSON.stringify(finalReceipt, null, 2);
    receiptBody.classList.add("receipt-fade");
    setTimeout(() => {
      receiptBody.classList.add("visible");
    }, 60);
    receiptBody.textContent = serializedReceipt;
    latestReceiptText = serializedReceipt;
    snapshotLine.textContent = JSON.stringify({
      runId,
      timeline_ids: stepTrace.map((entry) => entry.timeline_id),
      result: outcomeSummary.result,
      costEstimated: outcomeSummary.costEstimated,
      costActual: outcomeSummary.costActual,
      artifact: outcomeSummary.signed_receipt_id
    });
    return finalReceipt;
  }

  function buildRunwayOfflineFailureReceipt(runId, startTime, elapsedSeconds, profile, reason, sourceInfo) {
    const failTimeline = [
      {
        status: "fail",
        phase: "Control plane",
        step: "control_plane",
        text: reason || "Live control plane unavailable",
        elapsedMs: 120
      }
    ];

    return buildReceipt(
      failTimeline,
      startTime,
      elapsedSeconds,
      { total: 1, passed: 0, warn: 0, failed: 1 },
      runId,
      profile,
      sourceInfo
    );
  }

  function runwayEventStatusFromOutcome(outcome) {
    if (outcome === "PASS") {
      return "ok";
    }
    if (outcome === "PASS_WITH_WARN") {
      return "warn";
    }
    return "fail";
  }

  async function fetchRunwayRuntimeContract(requestedMode) {
    try {
      const runtimeSearch = new URLSearchParams(window.location.search || "");
      const baseMode = requestedMode || runwayConfig.mode || "demo";
      const baseApiBase = runwayConfig.apiBaseUrl || "";
      const baseContractVersion = runwayConfig.contractVersion || "runway.v1";

      if (!runtimeSearch.has("runwayMode") && baseMode) {
        runtimeSearch.set("runwayMode", baseMode);
      }

      if (!runtimeSearch.has("runwayApiBaseUrl") && baseApiBase) {
        runtimeSearch.set("runwayApiBaseUrl", baseApiBase);
      }

      if (!runtimeSearch.has("runwayContractVersion") && baseContractVersion) {
        runtimeSearch.set("runwayContractVersion", baseContractVersion);
      }

      const queryString = runtimeSearch.toString();
      const runtimeEndpoint = "/v1/runway/runtime" + (queryString ? `?${queryString}` : "");

      const response = await fetch(runtimeEndpoint, {
        method: "GET",
        headers: {
          Accept: "application/json",
          "x-tenant-id": runwayConfig.tenantId || "tenant-runway-staging"
        }
      });
      const contentType = String(response.headers.get("content-type") || "").toLowerCase();
      const pagesRuntimeUsable = response.ok && contentType.includes("application/json");
      if (pagesRuntimeUsable) {
        const payload = await response.json();
        return {
          mode: payload.mode || payload.runway_mode || "unknown",
          liveBackendConnected:
            payload.live_backend_connection_status ||
            payload.live_backend_status ||
            payload.liveBackendConnectionStatus ||
            payload.status ||
            "unknown",
          contractVersion: deriveContractVersion(payload),
          backendApiBaseUrl:
            payload.backend?.configured_api_base ||
            payload.backend_api_base ||
            payload.backendApiBaseUrl ||
            runwayConfig.apiBaseUrl ||
            null,
          contractVersions: deriveContractVersions(payload),
          ...payload
        };
      }

      // When Pages Functions are unavailable, probe the configured Kernel directly for LIVE.
      if (baseMode === "live" && baseApiBase) {
        try {
          const probe = await fetch(`${baseApiBase.replace(/\/+$/, "")}/v1/runway/runtime`, {
            method: "GET",
            headers: {
              Accept: "application/json",
              "x-tenant-id": runwayConfig.tenantId || "tenant-runway-staging"
            }
          });
          if (probe.ok) {
            const payload = await probe.json();
            return {
              mode: payload.mode || "live",
              liveBackendConnected:
                payload.liveBackendConnectionStatus ||
                payload.live_backend_connection_status ||
                payload.status ||
                "connected",
              contractVersion: deriveContractVersion(payload),
              contractVersions: deriveContractVersions(payload),
              backendApiBaseUrl: baseApiBase,
              ...payload
            };
          }
        } catch (probeError) {
          return {
            mode: "offline",
            liveBackendConnected: "disconnected",
            contractVersion: baseContractVersion,
            backendApiBaseUrl: baseApiBase,
            error: String(probeError && probeError.message ? probeError.message : probeError)
          };
        }
      }

      return {
        mode: "unknown",
        liveBackendConnected: response.status === 503 ? "not_configured" : "disconnected",
        contractVersion: runwayConfig.contractVersion || "runway.v1"
      };
    } catch (error) {
      return {
        mode: "unknown",
        liveBackendConnected: "error",
        contractVersion: runwayConfig.contractVersion || "runway.v1",
        error: String(error && error.message ? error.message : error)
      };
    }
  }

  async function verifyRunwayReceipt(runId, options = {}) {
    if (!runId) {
      return { passed: false, error: "missing_run_id" };
    }

    const verifyContract = options.contractVersion || runwayConfig.contractVersion || "runway.v1";
    const verifyApiBase = options.apiBaseUrl || runwayConfig.apiBaseUrl || "";
    const tenantId = runwayConfig.tenantId || "tenant-runway-staging";
    const backends = [];
    backends.push("");
    if (verifyApiBase) {
      backends.push(verifyApiBase.replace(/\/+$/, ""));
    }

    try {
      let lastError = null;
      for (const backendBase of backends) {
        const verifyUrl = backendBase
          ? `${backendBase}/v1/runway/receipts/verify`
          : "/v1/runway/receipts/verify";
        try {
          const response = await fetch(verifyUrl, {
            method: "POST",
            headers: {
              "content-type": "application/json",
              Accept: "application/json",
              "x-tenant-id": tenantId
            },
            body: JSON.stringify({
              runId,
              contractVersion: verifyContract
            })
          });

          if (!response.ok) {
            lastError = `receipt_verify_${response.status}`;
            try {
              const errorPayload = await response.json();
              if (errorPayload && typeof errorPayload === "object" && errorPayload.code) {
                lastError = `${lastError}:${errorPayload.code}`;
              }
            } catch (_) {
              // no structured error payload available
            }
            continue;
          }

          const payload = await response.json();
          return {
            ...payload,
            backend_target: backendBase || "pages"
          };
        } catch (error) {
          lastError = String(error && error.message ? error.message : error);
          continue;
        }
      }

      return {
        passed: false,
        error: lastError || "receipt_verify_failed",
        backend_target: backends.length > 1 ? "pages_or_backend" : (backends[0] || "pages"),
        checked_backends: backends.map((backend) => (backend || "pages"))
      };
    } catch (error) {
      return { passed: false, error: String(error && error.message ? error.message : error) };
    }
  }

  async function fetchLiveReceiptFromContract(runId, options = {}) {
    if (!runId) {
      return null;
    }

    const apiBase = options.apiBaseUrl || "";
    const tenantId = runwayConfig.tenantId || "tenant-runway-staging";
    const endpoints = [];
    endpoints.push(`/v1/runway/runs/${encodeURIComponent(runId)}/receipt`);
    if (apiBase) {
      endpoints.push(`${apiBase.replace(/\/+$/, "")}/v1/runway/runs/${encodeURIComponent(runId)}/receipt`);
    }

    const headers = {
      Accept: "application/json",
      "x-tenant-id": tenantId,
    };

    for (const endpoint of endpoints) {
      try {
        const response = await fetch(endpoint, {
          method: "GET",
          headers
        });
        if (!response.ok) {
          continue;
        }

        const payload = await response.json();
        if (!payload) {
          continue;
        }

        if (payload.outputs || payload.checks || payload.receipt_id || payload.result || payload.signed_receipt_id) {
          return payload;
        }
      } catch (_) {
        continue;
      }
    }

    return null;
  }

  function setScenarioForRunMode(mode, context) {
    if (!trustLine) {
      return;
    }

    const runtimeConnected = hasLiveBackendConnection(context?.liveBackendConnected || context?.status);

    if (mode === "live") {
      if (runtimeConnected) {
        trustLine.textContent = "Live backend contract is connected. This UI reflects same runway job state in realtime.";
      } else {
        trustLine.textContent =
          "Live backend unavailable in this session. OFFLINE mode is active; live state is not available.";
      }

      return;
    }

    if (mode === "offline") {
      trustLine.textContent =
        String(context?.requestedMode === "live")
          ? "Live backend unavailable. OFFLINE mode is active; no live authority is available."
          : "OFFLINE mode is active.";
      return;
    }

    trustLine.textContent = "DEMO mode: deterministic local replay is simulated in this browser session.";
  }

  function setRunKpiState(progress, total, checks, retryCount, startTime, profile, state) {
    if (runNodes) {
      runNodes.textContent = `${progress} / ${total}`;
    }

    if (runChecksPassed) {
      const passedCount = checks.passed || 0;
      runChecksPassed.textContent = `${passedCount} / ${checks.total || total}`;
    }

    if (runRetriesUsed) {
      runRetriesUsed.textContent = String(retryCount || 0);
    }

    if (runLatency) {
      runLatency.textContent = formatMs(Date.now() - startTime);
    }

    if (runConfidence && profile) {
      const reliability = computeReliability(profile, checks, Math.max(0, (Date.now() - startTime) / 1000));
      runConfidence.textContent = `${reliability.achieved.toFixed(1)}%`;
    }

    if (state && runState) {
      runState.textContent = state;
    }
  }

  function setMetaFromScenario(profile, runtimeContext = null) {
    if (scenarioSummary) {
      scenarioSummary.textContent = profile.summary;
    }

    if (scenarioPain) {
      scenarioPain.textContent = profile.pain;
    }

    if (scenarioSolution) {
      scenarioSolution.textContent = profile.solution;
    }

    scenarioTarget.textContent = `${Number(profile.reliability_target || 0).toFixed(1)}%`;
    scenarioCost.textContent = formatCurrency(profile.cost_cap_usd || 0);
    scenarioRetries.textContent = String(profile.expected_retries || 0);
    scenarioTokens.textContent = String(profile.expected_tokens || 0);
    scenarioCalls.textContent = String(profile.expected_model_calls || 0);
    scenarioRisk.textContent = profile.risk_envelope || "--";
    scenarioFallback.textContent = profile.fallback_policy || "--";

    if (trustLine) {
      const resolvedMode = runtimeContext?.requestedMode || resolveModeRequested();
      const payload = runtimeContext || { mode: resolvedMode, liveBackendConnected: "unknown" };
      setScenarioForRunMode(resolvedMode, payload);
    }

    scenarioButtons.forEach((button) => {
      button.classList.toggle("active", button.dataset.scenario === activeScenario);
    });
  }

  function chooseScenario(nextScenario) {
    activeScenario = scenarioFeed[nextScenario] ? nextScenario : "decision";
    setMetaFromScenario(scenarioFeed[activeScenario], { requestedMode: resolveModeRequested() });
  }

  function applyEndpointMetadata(payload, fallback) {
    if (!payload) {
      return fallback;
    }

    return {
      ...fallback,
      ...payload,
      steps: payload.steps && payload.steps.length ? payload.steps : fallback.steps
    };
  }

  async function fetchRemoteFeed(endpoint, scenarioName) {
    const response = await fetch(`${endpoint}?scenario=${encodeURIComponent(scenarioName)}`, {
      headers: { Accept: "application/json" }
    });

    if (!response.ok) {
      throw new Error(`endpoint_${response.status}`);
    }

    const payload = await response.json();
    if (Array.isArray(payload.feed) && payload.feed.length) {
      return {
        id: payload.id || scenarioName,
        runType: payload.runType || scenarioName,
        summary: payload.summary || "",
        pain: payload.pain || "",
        solution: payload.solution || "",
        reliability_target: payload.reliabilityTarget,
        expected_retries: payload.retries,
        expected_tokens: payload.tokens,
        expected_model_calls: payload.modelCalls,
        risk_envelope: payload.riskEnvelope,
        fallback_policy: payload.fallbackPolicy,
        provider_failover: payload.providerFailover,
        steps: payload.feed,
        cost_cap_usd: payload.costCapUsd,
        failure_modes: payload.failureModes,
        best_solution: payload.bestSolution,
        source_info: payload.source || "api"
      };
    }

    throw new Error("endpoint_no_feed");
  }

  function normalizeExternalFeed(feed, fallbackName) {
    const output = [];

    feed.forEach((item) => {
      if (!item || !item.step || !item.text) {
        return;
      }

      output.push({
        status: normalizeStatus(item.status),
        step: item.step,
        phase: item.phase || item.step,
        text: item.text,
        elapsedMs: Number.isFinite(Number(item.elapsedMs)) ? Number(item.elapsedMs) : 700,
        recovered: item.recovered === true
      });
    });

    if (output.length > 0) {
      return { name: fallbackName, runType: fallbackName, steps: output };
    }

    throw new Error("endpoint_invalid_feed");
  }

  async function runScenario() {
    if (running) {
      return;
    }

    running = true;
    runButton.disabled = true;
    resetButton.disabled = true;

    const baseline = scenarioFeed[activeScenario] || scenarioFeed.decision;
    const executionContext = getExecutionContext();
    let runMode = executionContext.mode;
    const requestedMode = runMode;
    let provider = executionContext.provider;
    const runtimeContract = await fetchRunwayRuntimeContract(requestedMode).catch(() => null);
    const runtimeContext = {
      requestedMode: runMode,
      mode: runtimeContract?.mode || runMode,
      liveBackendConnected: runtimeContract?.liveBackendConnected || "unknown",
      ...runtimeContract
    };
    const liveBackendConnected = hasLiveBackendConnection(runtimeContext.liveBackendConnected);
    let adjustedContextMode = runtimeContext.mode;

    if (runMode === "live") {
      if (liveBackendConnected) {
        const liveApiBase = runtimeContext.backendApiBaseUrl || runwayConfig.apiBaseUrl;
        const liveContractVersion =
          runtimeContext.contract_version || runtimeContext.contractVersion || runwayConfig.contractVersion || "runway.v1";
        const tenantId = runtimeContext.tenant_id || runwayConfig.tenantId || "tenant-runway-staging";
        const liveRuntimeProvider = makeLiveProvider(liveApiBase, liveContractVersion, tenantId);

        if (!liveRuntimeProvider) {
          adjustedContextMode = "offline";
          runMode = "offline";
          provider = null;
        } else {
          provider = liveRuntimeProvider;
          adjustedContextMode = "live";
          runMode = "live";
        }
      } else {
        adjustedContextMode = "offline";
        runMode = "offline";
        provider = null;
      }
    }

    runtimeContext.mode = adjustedContextMode;

    if (runMode !== executionContext.mode) {
      setScenarioForRunMode(runMode, runtimeContext);
      applyModeBadge(runMode);
    }
    let scenarioToRun = baseline;
    let sourceInfo = executionContext.sourceInfo;
    const startTime = Date.now();
    let runId = `NR-${startTime}`;

    clearLogs();
    streamRoot.classList.add("loading");
    const streamSkeleton = document.createElement("p");
    streamSkeleton.className = "stream-skeleton";
    streamSkeleton.textContent = "Initializing deterministic runway...";
    streamRoot.appendChild(streamSkeleton);
    setStatus(
      runMode === "live"
        ? "Starting live runway..."
        : runMode === "offline"
          ? "Starting offline demonstration mode..."
          : "Starting demo runway...",
      runMode === "offline" ? "warn" : "ok"
    );
    runIdBadge.textContent = `Run ID: ${runId}`;
    snapshotLine.textContent = "";
    setScenarioForRunMode(runMode, runtimeContext);

    emitRunEvent({
      runId,
      scenarioId: baseline.id,
      phase: "start",
      status: "ok",
      stepIndex: 0,
      elapsedMs: 0,
      cost: baseline.cost_cap_usd || 0
    });

    try {
      if (runMode === "live" && provider) {
        setMetaFromScenario(scenarioToRun, runtimeContext);

        const liveTimeline = [];
        let snapshot = {};
        let elapsedMs = 0;
        const liveStepCounts = { ok: 0, warn: 0, fail: 0 };
        const liveTimelineIds = new Set();

        const liveResult = await provider.run(scenarioToRun, {
          delay: sleep,
          onStep: async (rawStep) => {
            const step = {
              status: normalizeStatus(rawStep && rawStep.status ? rawStep.status : "ok"),
              phase: rawStep?.phase || rawStep?.step || "Execute",
              step: rawStep?.step || "run-step",
              text: rawStep?.text || "Kernel event received",
              elapsedMs: Number.isFinite(Number(rawStep?.elapsedMs))
                ? Number(rawStep.elapsedMs)
                : 500,
              recovered: rawStep?.recovered === true,
              timeline_id: rawStep?.timeline_id || rawStep?.hdir_sequence || rawStep?.event_id || rawStep?.eventId || null,
              hdir_sequence: Number.isFinite(Number(rawStep?.hdir_sequence || rawStep?.sequence)) ? Number(rawStep.hdir_sequence || rawStep.sequence) : null
            };

            const eventId = step.timeline_id
              ? `timeline:${step.timeline_id}`
              : `hdir:${step.hdir_sequence !== null && step.hdir_sequence !== undefined ? step.hdir_sequence : "na"}:${step.phase}:${step.step}`;
            if (liveTimelineIds.has(eventId)) {
              return;
            }
            liveTimelineIds.add(eventId);

            liveTimeline.push(step);
            liveStepCounts[step.status] += 1;
            const countLength = liveTimeline.length;
            createEntry(step, countLength - 1, Math.max(1, liveTimeline.length), startTime);
            emitRunEvent({
              runId,
              scenarioId: scenarioToRun.id,
              phase: step.phase,
              status: eventStatusFromStep(step.status, step.recovered),
              stepIndex: countLength,
              elapsedMs: step.elapsedMs,
              cost: Number(((scenarioToRun.cost_cap_usd || 0) / Math.max(countLength, 1)).toFixed(4))
            });
        setRunKpiState(
          countLength,
          Math.max(1, countLength),
          {
                total: countLength,
                passed: countLength - liveStepCounts.warn - liveStepCounts.fail,
                warn: liveStepCounts.warn,
                failed: liveStepCounts.fail
              },
              snapshot.retries || 0,
              startTime,
              scenarioToRun,
              "Live running"
            );
          },
          onSnapshot: async (nextSnapshot) => {
            if (!nextSnapshot || typeof nextSnapshot !== "object") {
              return;
            }
            snapshot = nextSnapshot;
            elapsedMs = Number(nextSnapshot.elapsed_ms || nextSnapshot.elapsedMs || elapsedMs || 0);
            if (runNodes) {
              runNodes.textContent = `${snapshot.jobs_completed || 0} / ${snapshot.jobs_total || 0}`;
            }
            if (runChecksPassed) {
              runChecksPassed.textContent = `${snapshot.jobs_completed || 0} / ${snapshot.jobs_total || liveTimeline.length || 0}`;
            }
            if (runRetriesUsed) {
              runRetriesUsed.textContent = String(snapshot.retries || 0);
            }
            if (runConfidence && scenarioToRun) {
              const reliability = computeReliability(scenarioToRun, countTimelineStatus(liveTimeline), (Date.now() - startTime) / 1000);
              runConfidence.textContent = `${reliability.achieved.toFixed(1)}%`;
            }
            if (runLatency) {
              runLatency.textContent = formatMs(Date.now() - startTime);
            }

            if (snapshot.status === "FAILED") {
              setStatus("Live run failed; waiting for terminal event", "bad");
            } else if (snapshot.status === "REVIEW_REQUIRED") {
              setStatus("Live run requires review", "warn");
            } else if (snapshot.status === "COMPLETED") {
              setStatus("Live run completed", "ok");
            } else {
              setStatus("Live run in progress", "ok");
            }
          }
        });

        runId = liveResult.runId || runId;
        runIdBadge.textContent = `Run ID: ${runId}`;
        sourceInfo = liveResult.source || sourceInfo;
        scenarioToRun = liveResult.profile || scenarioToRun;
        setMetaFromScenario(scenarioToRun, { ...runtimeContext, requestedMode: runMode, runId, mode: "live" });

        const timeline = Array.isArray(liveResult.feed) && liveResult.feed.length > 0 ? liveResult.feed : liveTimeline;
        const counts = countTimelineStatus(timeline);
        snapshot = liveResult.snapshot || snapshot || {};
        elapsedMs = Number(liveResult.elapsedMs || elapsedMs || Date.now() - startTime);

        if (runMode !== "offline") {
          applyModeBadge("live");
        }

        const liveReceipt = buildLiveKernelReceipt(runId, snapshot, timeline, scenarioToRun, liveResult.receipt);
        if (!liveResult.receipt) {
          const fetchedReceipt = await fetchLiveReceiptFromContract(runId, {
            mode: runMode,
            contractVersion: runtimeContext.contract_version || runtimeContext.contractVersion || runwayConfig.contractVersion || "runway.v1",
            apiBaseUrl: runtimeContext.backendApiBaseUrl || runwayConfig.apiBaseUrl || ""
          });
          if (fetchedReceipt && typeof fetchedReceipt === "object") {
            liveResult.receipt = fetchedReceipt;
          }
        }

        const receiptToRender = liveResult.receipt ? buildLiveKernelReceipt(runId, snapshot, timeline, scenarioToRun, liveResult.receipt) : liveReceipt;
        const verified = await verifyRunwayReceipt(runId, {
          mode: runMode,
          contractVersion: runtimeContext.contract_version || runtimeContext.contractVersion || runwayConfig.contractVersion || "runway.v1",
          apiBaseUrl: runtimeContext.backendApiBaseUrl || runwayConfig.apiBaseUrl || ""
        });
        if (verified) {
          receiptToRender.verification = {
            ...toVerificationFlag(verified),
            contract_version: runtimeContext.contract_version || runtimeContext.contractVersion || runwayConfig.contractVersion || "runway.v1",
            backend_contracts: runtimeContext.contractVersions || null,
            verifier_contract: {
              path: "POST /v1/runway/receipts/verify",
              route: "/v1/runway/receipts/verify"
            }
          };
        }
        latestReceiptText = JSON.stringify(
          {
            runwayRun: {
              runId,
              scenarioId: scenarioToRun.id,
              phase: "receipt",
              status: runwayEventStatusFromOutcome(receiptToRender.result),
              stepIndex: timeline.length,
              elapsedMs,
              cost: receiptToRender.costActual
            },
            receipt: receiptToRender
          },
          null,
          2
        );
        receiptBody.classList.add("receipt-fade");
        setTimeout(() => receiptBody.classList.add("visible"), 60);
        receiptBody.textContent = latestReceiptText;
        snapshotLine.textContent = JSON.stringify({
          runId,
          source: sourceInfo,
          mode: modeLabel("live"),
          contract: runwayConfig.contractVersion || "runway.v1",
          contractVersions: runtimeContext?.contractVersions || null,
          result: receiptToRender.result,
          timeline_ids: (receiptToRender.timeline || []).map((entry) => entry.timeline_id),
          costEstimated: receiptToRender.costEstimated,
          costActual: receiptToRender.costActual,
          artifact_url: receiptToRender.outputs?.artifact_url || null,
          outcome: receiptToRender.result,
          verified_by_route: Boolean(receiptToRender.verification),
          verification: receiptToRender.verification || null
        });

        const outcome = receiptToRender.result;
        if (outcome === "PASS") {
          setStatus("Completed", "ok");
        } else if (outcome === "PASS_WITH_WARN") {
          setStatus("Completed with warning", "warn");
        } else {
          setStatus("Completed with failure", "bad");
        }

        setRunKpiState(
          timeline.length,
          timeline.length,
          {
            total: Math.max(timeline.length, 1),
            passed: counts.ok,
            warn: counts.warn,
            failed: counts.fail
          },
          snapshot.retries || 0,
          startTime,
          scenarioToRun,
          outcome
        );

        emitRunEvent({
          runId,
          scenarioId: scenarioToRun.id,
          phase: "receipt",
          status: runwayEventStatusFromOutcome(outcome),
          stepIndex: timeline.length,
          elapsedMs,
          cost: receiptToRender.costActual || 0,
          receipt: receiptToRender
        });
        return;
      }

      const demoResult = demoProvider ? await demoProvider.run(activeScenario, {
        onStep: async (step) => {
          const normalized = {
            status: normalizeStatus(step.status),
            phase: step.phase || step.step || "Execute",
            step: step.step || "run-step",
            text: step.text || "Step completed",
            elapsedMs: Number.isFinite(Number(step.elapsedMs)) ? Number(step.elapsedMs) : 700,
            recovered: step.recovered === true
          };
          createEntry(normalized, streamRoot.querySelectorAll(".stream-entry").length, scenarioToRun.steps.length, startTime);
          emitRunEvent({
            runId,
            scenarioId: scenarioToRun.id,
            phase: normalized.phase,
            status: eventStatusFromStep(normalized.status, normalized.recovered),
            stepIndex: streamRoot.querySelectorAll(".stream-entry").length,
            elapsedMs: normalized.elapsedMs,
            cost: Number(((scenarioToRun.cost_cap_usd || 0) / Math.max(scenarioToRun.steps.length, 1)).toFixed(4))
          });
        }
      }) : null;

      if (!demoResult) {
        throw new Error("No local provider available.");
      }

      scenarioToRun = demoResult.profile || scenarioToRun || baseline;
      runId = demoResult.runId || runId;
      runIdBadge.textContent = `Run ID: ${runId}`;
      const endpoint = runButton.dataset.endpoint;
      if (endpoint) {
        sourceInfo = "remote-api";
      }

      const remotePayload = endpoint ? await fetchRemoteFeed(endpoint, activeScenario).catch(() => null) : null;
      if (remotePayload) {
        sourceInfo = remotePayload.source_info || sourceInfo;
        scenarioToRun = applyEndpointMetadata(
          {
            ...remotePayload,
            steps: normalizeExternalFeed(
              remotePayload.steps.map((entry) => ({
                ...entry,
                status: normalizeStatus(entry.status)
              })),
              remotePayload.runType || activeScenario
            ).steps
          },
          scenarioToRun
        );
      }

      const timeline = Array.isArray(demoResult.feed) && demoResult.feed.length > 0
        ? demoResult.feed
        : (scenarioToRun.steps || []).map((entry, idx) => ({
            status: normalizeStatus(entry.status),
            phase: entry.phase || "Execute",
            step: entry.step || `step-${idx + 1}`,
            text: entry.text || "Execution checkpoint",
            elapsedMs: Number(entry.elapsedMs) || 700,
            recovered: entry.recovered === true && normalizeStatus(entry.status) === "fail"
          }));

      setMetaFromScenario(scenarioToRun, { requestedMode: runMode });
      setRunKpiState(0, timeline.length, { total: timeline.length, passed: 0, warn: 0, failed: 0 }, 0, startTime, scenarioToRun, runMode === "offline" ? "OFFLINE" : "Demo");

      let okCount = 0;
      let warnCount = 0;
      let failCount = 0;
      let retryCount = 0;

      for (let i = 0; i < timeline.length; i += 1) {
        const entry = timeline[i];
        if (entry.status === "ok") {
          okCount += 1;
        }
        if (entry.status === "warn") {
          warnCount += 1;
        }
        if (entry.status === "fail" && !entry.recovered) {
          failCount += 1;
        }
        if (entry.status === "fail" && entry.recovered) {
          warnCount += 1;
        }
        if (entry.step === "retry") {
          retryCount += 1;
        }

        setRunKpiState(
          i + 1,
          timeline.length,
          { total: timeline.length, passed: okCount, warn: warnCount, failed: failCount },
          retryCount,
          startTime,
          scenarioToRun,
          runMode === "offline" ? "Offline replay" : "Demo running"
        );
      }

      const elapsedSeconds = (Date.now() - startTime) / 1000;
      const finalized = buildReceipt(
        timeline,
        startTime,
        elapsedSeconds,
        {
          total: timeline.length,
          passed: okCount,
          warn: warnCount,
          failed: failCount
        },
        runId,
        scenarioToRun,
        sourceInfo
      );

      latestReceiptText = JSON.stringify(finalized, null, 2);
      if (receiptBody) {
        receiptBody.textContent = latestReceiptText;
      }

      if (failCount > 0) {
        setStatus("Completed with failures", "bad");
      } else if (warnCount > 0) {
        setStatus("Completed with recovery", "warn");
      } else {
        setStatus("Completed", "ok");
      }

      snapshotLine.textContent = JSON.stringify({
        runId,
        timeline_ids: finalized.receipt.timeline.map((entry) => entry.timeline_id),
        result: finalized.receipt.result,
        costEstimated: finalized.receipt.costEstimated,
        costActual: finalized.receipt.costActual,
        source: sourceInfo,
        mode: runMode
      });

      emitRunEvent({
        runId,
        scenarioId: scenarioToRun.id,
        phase: "receipt",
        status:
          finalized?.receipt?.result === "FAIL"
            ? "fail"
            : finalized?.receipt?.result === "PASS"
              ? "ok"
              : "warn",
        stepIndex: timeline.length,
        elapsedMs: Math.round(elapsedSeconds * 1000),
        cost: finalized?.receipt?.costActual || 0,
        receipt: finalized.receipt
      });

      setRunKpiState(
        timeline.length,
        timeline.length,
        { total: timeline.length, passed: okCount, warn: warnCount, failed: failCount },
        retryCount,
        startTime,
        scenarioToRun,
        finalized?.receipt?.result || "Completed"
      );
    } catch (error) {
      if (requestedMode === "live") {
        runMode = "offline";
        runtimeContext.mode = "offline";
        runtimeContext.requestedMode = requestedMode;
        setScenarioForRunMode("offline", runtimeContext);
        applyModeBadge("offline");
        sourceInfo = "OFFLINE";

        const fallbackReason = String(error && error.message ? error.message : "unknown_error");
        const elapsedSeconds = (Date.now() - startTime) / 1000;
        const failureReason = `Live backend unavailable: ${fallbackReason}`;
        const finalized = buildRunwayOfflineFailureReceipt(
          runId,
          startTime,
          elapsedSeconds,
          baseline,
          failureReason,
          sourceInfo
        );

        latestReceiptText = JSON.stringify(finalized, null, 2);
        if (receiptBody) {
          receiptBody.textContent = latestReceiptText;
        }

        snapshotLine.textContent = JSON.stringify({
          runId,
          timeline_ids: finalized.receipt.timeline.map((entry) => entry.timeline_id),
          result: finalized.receipt.result,
          costEstimated: finalized.receipt.costEstimated,
          costActual: finalized.receipt.costActual,
          source: sourceInfo,
          mode: modeLabel(runMode),
          offline: true
        });

        setStatus("Live backend unavailable. Run blocked in OFFLINE mode.", "bad");
        emitRunEvent({
          runId,
          scenarioId: baseline.id,
          phase: "receipt",
          status: "fail",
          stepIndex: 1,
          elapsedMs: Math.round(elapsedSeconds * 1000),
          cost: finalized?.receipt?.costActual || 0,
          receipt: finalized.receipt
        });

        setRunKpiState(
          1,
          1,
          { total: 1, passed: 0, warn: 0, failed: 1 },
          0,
          startTime,
          baseline,
          finalized?.receipt?.result || "Offline blocked"
        );

        return;
      }

      const fallbackReason = String(error && error.message ? error.message : "unknown_error");
      setStatus("Fallback to local simulator", "warn");
      if (sourceInfo === "local-simulator") {
        sourceInfo = "OFFLINE";
      }

      const fallbackTimeline = [
        {
          status: "warn",
          phase: "Plan",
          step: "control_plane",
          text: `${runMode === "live" ? "Live API unavailable" : "Execution interrupted"}: ${fallbackReason}. Using deterministic local scenario replay.`,
          elapsedMs: 320
        },
        ...baseline.steps
      ];

      setRunKpiState(0, fallbackTimeline.length, { total: fallbackTimeline.length, passed: 0, warn: 0, failed: 0 }, 0, startTime, baseline, "Fallback");

      let okCount = 0;
      let warnCount = 0;
      let failCount = 0;
      let retryCount = 0;

      for (let i = 0; i < fallbackTimeline.length; i += 1) {
        const entry = {
          ...fallbackTimeline[i],
          status: normalizeStatus(fallbackTimeline[i].status),
          recovered: fallbackTimeline[i].recovered === true && normalizeStatus(fallbackTimeline[i].status) === "fail",
          elapsedMs: Number(fallbackTimeline[i].elapsedMs) || 700
        };

        createEntry(entry, i, fallbackTimeline.length, startTime);

        if (entry.status === "ok") {
          okCount += 1;
        }
        if (entry.status === "warn") {
          warnCount += 1;
        }
        if (entry.status === "fail" && !entry.recovered) {
          failCount += 1;
        }
        if (entry.status === "fail" && entry.recovered) {
          warnCount += 1;
        }
        if (entry.step === "retry") {
          retryCount += 1;
        }

        setRunKpiState(
          i + 1,
          fallbackTimeline.length,
          { total: fallbackTimeline.length, passed: okCount, warn: warnCount, failed: failCount },
          retryCount,
          startTime,
          baseline,
          "Fallback"
        );

        emitRunEvent({
          runId,
          scenarioId: baseline.id,
          phase: entry.phase,
          status: eventStatusFromStep(entry.status, entry.recovered),
          stepIndex: i + 1,
          elapsedMs: entry.elapsedMs,
          cost: Number(((baseline.cost_cap_usd || 0) / Math.max(fallbackTimeline.length, 1)).toFixed(4))
        });

        await sleep(entry.elapsedMs || 650);
      }

      const elapsedSeconds = (Date.now() - startTime) / 1000;
      const finalized = buildReceipt(
        fallbackTimeline,
        startTime,
        elapsedSeconds,
        { total: fallbackTimeline.length, passed: okCount, warn: warnCount, failed: failCount },
        runId,
        baseline,
        sourceInfo
      );
      latestReceiptText = JSON.stringify(finalized, null, 2);
      if (receiptBody) {
        receiptBody.textContent = latestReceiptText;
      }

      snapshotLine.textContent = JSON.stringify({
        runId,
        timeline_ids: finalized.receipt.timeline.map((entry) => entry.timeline_id),
        result: finalized.receipt.result,
        costEstimated: finalized.receipt.costEstimated,
        costActual: finalized.receipt.costActual,
        source: sourceInfo,
        mode: modeLabel(runMode)
      });

      setStatus("Fallback completed", "warn");
      emitRunEvent({
        runId,
        scenarioId: baseline.id,
        phase: "receipt",
        status:
          finalized?.receipt?.result === "FAIL"
            ? "fail"
            : finalized?.receipt?.result === "PASS"
              ? "ok"
              : "warn",
        stepIndex: fallbackTimeline.length,
        elapsedMs: Math.round(elapsedSeconds * 1000),
        cost: finalized?.receipt?.costActual || 0,
        receipt: finalized.receipt
      });

      setRunKpiState(
        fallbackTimeline.length,
        fallbackTimeline.length,
        { total: fallbackTimeline.length, passed: okCount, warn: warnCount, failed: failCount },
        retryCount,
        startTime,
        baseline,
        finalized?.receipt?.result || "Fallback complete"
      );
    } finally {
      running = false;
      runButton.disabled = false;
      resetButton.disabled = false;
      streamRoot.classList.remove("loading");
    }
  }

  function clearLogs() {
    streamRoot.classList.remove("loading");
    streamRoot.textContent = "";
    receiptBody.textContent = "No active run. Start a scenario to render a signed output proof.";
    receiptBody.classList.remove("receipt-fade", "visible");
    snapshotLine.textContent = "";
    latestReceiptText = "";
    runIdBadge.textContent = "Run ID: --";
    setStatus("Ready", "ok");

    runNodes.textContent = "0 / 0";
    runChecksPassed.textContent = "0 / 0";
    runRetriesUsed.textContent = "0";
    runLatency.textContent = "--ms";
    runConfidence.textContent = "--%";

    if (copyReceiptHint) {
      copyReceiptHint.textContent = "";
      copyReceiptHint.style.color = "";
    }
  }

  function setCopyHint(message, tone = "ok") {
    if (!copyReceiptHint) {
      return;
    }

    copyReceiptHint.textContent = message;
    copyReceiptHint.style.color =
      tone === "bad"
        ? "#ff8c9f"
        : tone === "warn"
          ? "#ffce7a"
          : "#95ffbc";

    setTimeout(() => {
      if (copyReceiptHint.textContent === message) {
        copyReceiptHint.textContent = "";
        copyReceiptHint.style.color = "";
      }
    }, 1600);
  }

  function setRevealAnimation() {
    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reducedMotion) {
      revealTargets.forEach((el) => el.classList.add("show"));
      return;
    }

    const io = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("show");
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.2 });

    revealTargets.forEach((target) => io.observe(target));
  }

  runButton.addEventListener("click", runScenario);
  resetButton.addEventListener("click", clearLogs);

  if (copyReceipt) {
    copyReceipt.addEventListener("click", async () => {
      if (!latestReceiptText) {
        setCopyHint("No receipt to copy yet", "warn");
        return;
      }

      try {
        await navigator.clipboard.writeText(latestReceiptText);
        setCopyHint("Copied", "ok");
      } catch (error) {
        setCopyHint("Clipboard blocked. Please select and copy manually.", "bad");
      }
    });
  }

  scenarioButtons.forEach((button) => {
    button.addEventListener("click", () => {
      chooseScenario(button.dataset.scenario);
    });
  });

  setRevealAnimation();

  (async () => {
    const requestedMode = resolveModeRequested();
    const runtimeContext = await fetchRunwayRuntimeContract(requestedMode).catch(() => null);
    const runtimeConnected = runtimeContext && hasLiveBackendConnection(runtimeContext.liveBackendConnected);
    const runtimeApiConfigured = Boolean(
      (runtimeContext?.backendApiBaseUrl || runtimeContext?.backend?.configured_api_base || runwayConfig.apiBaseUrl)
    );
    const startupMode =
      requestedMode === "live"
        ? runtimeConnected
          ? "live"
          : "offline"
        : requestedMode;

    const seedContext = {
      requestedMode: startupMode,
      mode: startupMode,
      liveBackendConnected: runtimeContext?.liveBackendConnected || (runtimeConnected ? "connected" : "unknown"),
      contractVersion: runtimeContext?.contractVersion || runwayConfig.contractVersion,
      backendApiBaseUrl: runtimeContext?.backendApiBaseUrl || runwayConfig.apiBaseUrl || null,
      ...runtimeContext
    };

    setMetaFromScenario(scenarioFeed[activeScenario], seedContext);
    applyModeBadge(startupMode);
    clearLogs();
  })();
})();
