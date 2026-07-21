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
  const demoProvider =
    typeof window.DemoRunwayProvider === "function" ? new window.DemoRunwayProvider(scenarioFeed) : null;
  const liveProvider =
    typeof window.LiveRunwayProvider === "function"
      ? new window.LiveRunwayProvider({
          apiBaseUrl: runwayConfig.apiBaseUrl,
          contractVersion: runwayConfig.contractVersion || "runway.v1",
          tenantId: runwayConfig.tenantId || "tenant-runway-staging"
        })
      : null;

  function resolveProvider(scenarioName) {
    const requested = String(runwayConfig.mode || "demo").toLowerCase();
    const modeBadge = document.getElementById("runwayModeBadge");
    if (requested === "live" && scenarioName === "webpage" && liveProvider && runwayConfig.apiBaseUrl) {
      if (modeBadge) modeBadge.textContent = liveProvider.getModeLabel();
      return liveProvider;
    }
    if (modeBadge) {
      modeBadge.textContent = !runwayConfig.apiBaseUrl && requested === "live" ? "OFFLINE" : "DEMO";
    }
    return demoProvider;
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
      costActual,
      verifiedAt: new Date(startTime).toISOString(),
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

  function setMetaFromScenario(profile) {
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
      trustLine.textContent = `What you see is produced by this same UI and this same job state (${profile.runType}).`;
    }

    scenarioButtons.forEach((button) => {
      button.classList.toggle("active", button.dataset.scenario === activeScenario);
    });
  }

  function chooseScenario(nextScenario) {
    activeScenario = scenarioFeed[nextScenario] ? nextScenario : "decision";
    setMetaFromScenario(scenarioFeed[activeScenario]);
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
    let runId = `NR-${Date.now()}`;
    let scenarioToRun = baseline;
    let sourceInfo = "local-simulator";
    const startTime = Date.now();
    const provider = resolveProvider(activeScenario);

    clearLogs();
    streamRoot.classList.add("loading");
    const streamSkeleton = document.createElement("p");
    streamSkeleton.className = "stream-skeleton";
    streamSkeleton.textContent = "Initializing deterministic runway...";
    streamRoot.appendChild(streamSkeleton);
    setStatus("Running", "ok");
    runIdBadge.textContent = `Run ID: ${runId}`;
    snapshotLine.textContent = "";

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
      if (provider && (activeScenario === "webpage" || String(runwayConfig.mode || "").toLowerCase() === "live")) {
        const liveResult = await provider.run(activeScenario, {
          delay: sleep,
          onStep: async (step) => {
            createEntry(step, streamRoot.querySelectorAll(".stream-entry").length, Math.max(1, (scenarioToRun.steps || []).length), startTime);
          },
          onSnapshot: async (snapshot) => {
            if (runNodes) {
              runNodes.textContent = `${snapshot.jobs_completed || 0} / ${snapshot.jobs_total || 0}`;
            }
            if (runChecksPassed) {
              runChecksPassed.textContent = `${snapshot.jobs_completed || 0} / ${snapshot.jobs_total || 0}`;
            }
            if (runRetriesUsed) {
              runRetriesUsed.textContent = String(snapshot.retries || 0);
            }
            if (runConfidence) {
              runConfidence.textContent = `${Math.round((snapshot.reliability || 0) * 1000) / 10}%`;
            }
            if (runLatency) {
              runLatency.textContent = formatMs(Date.now() - startTime);
            }
            setStatus(snapshot.status || "Running", snapshot.status === "FAILED" ? "bad" : "ok");
          }
        });

        runId = liveResult.runId;
        runIdBadge.textContent = `Run ID: ${runId}`;
        sourceInfo = liveResult.source;
        scenarioToRun = liveResult.profile || baseline;
        setMetaFromScenario(scenarioToRun);

        const counts = { ok: 0, warn: 0, fail: 0 };
        (liveResult.feed || []).forEach((step) => {
          counts[step.status] = (counts[step.status] || 0) + 1;
        });
        const elapsedSeconds = Math.max(1, Math.round((liveResult.elapsedMs || Date.now() - startTime) / 1000));
        const snapshot = liveResult.snapshot || {};
        if (runNodes) runNodes.textContent = `${snapshot.jobs_completed || counts.ok} / ${snapshot.jobs_total || (liveResult.feed || []).length}`;
        if (runChecksPassed) runChecksPassed.textContent = `${snapshot.jobs_completed || counts.ok} / ${snapshot.jobs_total || (liveResult.feed || []).length}`;
        if (runRetriesUsed) runRetriesUsed.textContent = String(snapshot.retries || 0);
        if (runConfidence) runConfidence.textContent = `${Math.round((snapshot.reliability || computeReliability(scenarioToRun, counts, elapsedSeconds) / 100) * 1000) / 10}%`;
        if (runLatency) runLatency.textContent = formatMs(liveResult.elapsedMs || Date.now() - startTime);

        const receiptPayload = liveResult.receipt || buildReceipt(
          liveResult.feed || [],
          startTime,
          elapsedSeconds,
          counts,
          runId,
          scenarioToRun,
          sourceInfo
        );
        latestReceiptText = JSON.stringify(receiptPayload, null, 2);
        if (receiptBody) receiptBody.textContent = latestReceiptText;
        snapshotLine.textContent = `source=${sourceInfo}; contract=${runwayConfig.contractVersion || "runway.v1"}; mode=${liveResult.mode}`;
        setStatus(snapshot.status === "COMPLETED" || liveResult.mode === "demo" ? "Completed" : snapshot.status || "Completed", "ok");
        streamRoot.classList.remove("loading");
        running = false;
        runButton.disabled = false;
        resetButton.disabled = false;
        emitRunEvent({
          runId,
          scenarioId: scenarioToRun.id,
          phase: "complete",
          status: "ok",
          stepIndex: (liveResult.feed || []).length,
          elapsedMs: liveResult.elapsedMs || Date.now() - startTime,
          cost: snapshot.estimated_cost_usd || scenarioToRun.cost_cap_usd || 0,
          receipt: receiptPayload
        });
        return;
      }

      const endpoint = runButton.dataset.endpoint;
      if (endpoint) {
        const remotePayload = await fetchRemoteFeed(endpoint, activeScenario);
        if (remotePayload.id) {
          runId = `NR-${remotePayload.id}-${Date.now()}`;
          runIdBadge.textContent = `Run ID: ${runId}`;
        }

        sourceInfo = remotePayload.source_info || "remote-api";
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
          baseline
        );
      }

      const timeline = scenarioToRun.steps.map((entry, idx) => ({
        status: normalizeStatus(entry.status),
        phase: entry.phase || "Execute",
        step: entry.step || `step-${idx + 1}`,
        text: entry.text || "Execution checkpoint",
        elapsedMs: Number(entry.elapsedMs) || 700,
        recovered: entry.recovered === true && normalizeStatus(entry.status) === "fail"
      }));

      setRunKpiState(0, timeline.length, { total: timeline.length, passed: 0, warn: 0, failed: 0 }, 0, startTime, scenarioToRun, "Starting");

      let okCount = 0;
      let warnCount = 0;
      let failCount = 0;
      let retryCount = 0;

      for (let i = 0; i < timeline.length; i += 1) {
        const entry = timeline[i];
        createEntry(entry, i, timeline.length, startTime);

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
          "Running"
        );

        emitRunEvent({
          runId,
          scenarioId: scenarioToRun.id,
          phase: entry.phase,
          status: eventStatusFromStep(entry.status, entry.recovered),
          stepIndex: i + 1,
          elapsedMs: entry.elapsedMs,
          cost: Number(((scenarioToRun.cost_cap_usd || 0) / Math.max(timeline.length, 1)).toFixed(4))
        });

        await sleep(Number(entry.elapsedMs) || 700);
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

      if (failCount > 0) {
        setStatus("Completed with failures", "bad");
      } else if (warnCount > 0) {
        setStatus("Completed with recovery", "warn");
      } else {
        setStatus("Completed", "ok");
      }

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
        cost: finalized?.receipt?.costActual || 0
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
      const fallbackReason = String(error && error.message ? error.message : "unknown_error");
      setStatus("Fallback to local simulator", "warn");
      sourceInfo = "local-simulator";

      const fallbackTimeline = [
        {
          status: "warn",
          phase: "Plan",
          step: "control_plane",
          text: `Live API unavailable (${fallbackReason}). Using deterministic local scenario profile.`,
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
        cost: finalized?.receipt?.costActual || 0
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
    receiptBody.textContent = "No active run. Start a simulation to render a signed output proof.";
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
  setMetaFromScenario(scenarioFeed[activeScenario]);
  clearLogs();
})();
