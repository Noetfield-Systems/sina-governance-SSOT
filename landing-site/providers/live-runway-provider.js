(function (root) {
  const DEFAULT_GOALS = {
    decision: "Produce a deterministic decision brief with ranked recommendations and policy checks.",
    rfp: "Build a full RFP response pack with policy checks, source citations, and fallback evidence.",
    spreadsheet: "Clean a policy-constrained spreadsheet with deterministic transforms and signed diff output.",
    complex_api: "Run a multi-source API workflow with deterministic retries, schema replay, and recovery checkpoints.",
    webpage: "Build and deploy a deterministic webpage with verified HTML/CSS artifact checks and replayable output.",
    "webpage-build-deploy": "Build and deploy a deterministic webpage with verified HTML/CSS artifact checks and replayable output."
  };

  const DEFAULT_GOAL = "Execute a deterministic runway workflow with policy-safe recovery and canonical receipts.";
  const FINAL_STATES = new Set(["COMPLETED", "FAILED", "BLOCKED", "REVIEW_REQUIRED", "CANCELED", "CANCELLED"]);

  class LiveRunwayProvider {
    constructor(config = {}) {
      const incomingBase = typeof config.apiBaseUrl === "string" ? config.apiBaseUrl.trim() : "";
      this.apiBaseUrl = incomingBase.replace(/\/+$/, "");
      this.contractVersion = config.contractVersion || "runway.v1";
      this.tenantId = config.tenantId || "tenant-runway-staging";
      this.mode = "live";
      this.modeHeader = config.mode || "live";
      this.sessionToken = undefined;
      this.sessionSupported = true;
      this.offline = false;
    }

    getModeLabel() {
      return "LIVE";
    }

    _resolveUrl(path) {
      const normalized = String(path || "").startsWith("/") ? path : `/${path}`;
      if (!this.apiBaseUrl) {
        return normalized;
      }

      return `${this.apiBaseUrl}${normalized}`;
    }

    _buildHeaders(incomingHeaders = {}) {
      return {
        "x-tenant-id": this.tenantId,
        "x-runway-contract-version": this.contractVersion,
        "x-runway-mode": this.modeHeader,
        ...incomingHeaders
      };
    }

    _runHeaders(sessionToken, incomingHeaders = {}) {
      const filtered = { ...incomingHeaders };
      if (typeof sessionToken === "string" && sessionToken.trim()) {
        filtered["x-runway-session"] = sessionToken.trim();
      }
      return this._buildHeaders(filtered);
    }

    async _readJson(response) {
      if (!response) {
        return {};
      }

      const raw = await response.text();
      if (!raw) {
        return {};
      }

      try {
        return JSON.parse(raw);
      } catch (_) {
        return { raw };
      }
    }

    _parseEventPayload(raw) {
      if (!raw) {
        return null;
      }
      if (typeof raw === "object") {
        return raw;
      }
      try {
        return JSON.parse(raw);
      } catch (_) {
        return null;
      }
    }

    _extractRunId(payload, response) {
      let runId = String(payload && (payload.run_id || payload.runId || payload.id || "")).trim();
      if (runId) {
        return runId;
      }

      const location = response && (response.headers ? (response.headers.get("location") || response.headers.get("Location")) : "");
      const fromLocation = String(location || "").trim();
      if (!fromLocation) {
        return "";
      }

      const decodedLocation = decodeURIComponent(fromLocation);
      const pathParts = decodedLocation.split("?")[0].split("/");
      return String(pathParts[pathParts.length - 1] || "").trim();
    }

    _normalizeStatus(rawStatus) {
      const normalized = String(rawStatus || "").toLowerCase();
      if (/pass|success/.test(normalized)) {
        return "ok";
      }
      if (/warn|recover|recoverable|retry|fallback|escalat/.test(normalized)) {
        return "warn";
      }
      if (/fail|blocked|error|abort|terminal/.test(normalized)) {
        return "fail";
      }
      return "ok";
    }

    _normalizeEvent(rawEvent) {
      return {
        status: this._normalizeStatus(rawEvent.status || rawEvent.type || rawEvent.message || rawEvent.note || ""),
        step: rawEvent.step || rawEvent.type || rawEvent.name || "run-step",
        phase:
          rawEvent.phase ||
          (typeof rawEvent.type === "string" && rawEvent.type.includes(".")
            ? rawEvent.type.split(".")[0]
            : "run"),
        text: rawEvent.message || rawEvent.note || rawEvent.text || "Kernel event",
        elapsedMs: Number.isFinite(Number(rawEvent.elapsed_ms || rawEvent.elapsedMs))
          ? Number(rawEvent.elapsed_ms || rawEvent.elapsedMs)
          : 500,
        timeline_id: rawEvent.timeline_id || rawEvent.event_id || rawEvent.eventId || null,
        recovered: rawEvent.recovered === true || String(rawEvent.status || "").toLowerCase() === "recovered",
        hdir_sequence: Number.isFinite(Number(rawEvent.hdir_sequence || rawEvent.seq))
          ? Number(rawEvent.hdir_sequence || rawEvent.seq)
          : null
      };
    }

    _isRunFinalStatus(status) {
      return FINAL_STATES.has(String(status || "").toUpperCase());
    }

    _isRunFinal(payload = {}) {
      return this._isRunFinalStatus(payload.status);
    }

    _pollRunState(runId, sessionToken, initialSnapshot = null) {
      let snapshot = initialSnapshot && typeof initialSnapshot === "object" ? initialSnapshot : null;
      if (!runId) {
        return snapshot;
      }

      const maxAttempts = 180;
      return new Promise((resolve) => {
        let attempts = 0;
        const poll = async () => {
          try {
            const stateResponse = await fetch(this._resolveUrl(`/v1/runway/runs/${encodeURIComponent(runId)}`), {
              headers: {
                ...this._runHeaders(sessionToken)
              }
            });
            if (stateResponse.ok) {
              snapshot = await this._readJson(stateResponse);
              if (this._isRunFinal(snapshot && snapshot.status)) {
                resolve(snapshot);
                return;
              }
            }
          } catch (_) {
            // keep waiting for backend
          }

          attempts += 1;
          if (attempts >= maxAttempts) {
            resolve(snapshot);
            return;
          }
          setTimeout(poll, 600);
        };

        poll();
      });
    }

    buildGoal(scenarioName, profile) {
      const key = String(scenarioName || "").toLowerCase();
      if (DEFAULT_GOALS[key]) {
        return DEFAULT_GOALS[key];
      }
      if (profile && profile.summary && typeof profile.summary === "string") {
        return profile.summary;
      }
      return DEFAULT_GOAL;
    }

    async ensureSession() {
      if (this.sessionToken !== undefined) {
        return this.sessionToken;
      }

      if (!this.sessionSupported) {
        return "";
      }

      const response = await fetch(this._resolveUrl("/v1/runway/session"), {
        method: "POST",
        headers: {
          "content-type": "application/json",
          ...this._buildHeaders()
        },
        body: "{}"
      });

      if (response.status === 404 || response.status === 405 || response.status === 501) {
        this.sessionSupported = false;
        this.sessionToken = "";
        return "";
      }

      if (!response.ok) {
        this.offline = true;
        throw new Error(`session_${response.status}`);
      }

      const session = await this._readJson(response);
      const receivedToken = session.session_token || session.sessionToken;
      this.sessionToken = typeof receivedToken === "string" ? receivedToken : "";
      if (!this.sessionToken) {
        this.sessionSupported = false;
      }
      return this.sessionToken || "";
    }

    async _fetchReceipt(runId, sessionToken) {
      const receiptPaths = [
        `/v1/runway/runs/${encodeURIComponent(runId)}/receipt`,
        `/v1/runway/runs/${encodeURIComponent(runId)}/receipt?source=hdir_gateway`
      ];
      for (const path of receiptPaths) {
        try {
          const receiptResponse = await fetch(this._resolveUrl(path), {
            headers: {
              ...this._runHeaders(sessionToken)
            }
          });
          if (!receiptResponse.ok) {
            continue;
          }
          const receipt = await this._readJson(receiptResponse);
          if (receipt && (receipt.outputs || receipt.checks || receipt.receipt_id)) {
            return receipt;
          }
        } catch (_) {
          continue;
        }
      }
      return null;
    }

    _buildRuntimeProfile(scenarioProfile, scenarioName, goal, snapshot) {
      if (scenarioProfile) {
        return scenarioProfile;
      }

      const reliabilityValue = Number.isFinite(Number(snapshot && snapshot.reliability))
        ? Number(snapshot.reliability)
        : 0.95;
      const reliabilityTarget = reliabilityValue > 1 ? reliabilityValue : reliabilityValue * 100;

      return {
        id: "webpage-build-deploy",
        name: "Webpage build + deploy",
        runType: "webpage-build-deploy",
        summary: goal,
        pain: "Landing pages ship without execution proof.",
        solution: "HDIR compiles, executes, verifies, and receipts the webpage lane.",
        reliability_target: Number.isFinite(reliabilityTarget) ? Number(reliabilityTarget.toFixed(2)) : 95,
        cost_cap_usd: Number.isFinite(Number(snapshot && snapshot.estimated_cost_usd))
          ? Number(snapshot.estimated_cost_usd)
          : 1.5,
        expected_retries: Number.isFinite(Number(snapshot && snapshot.retries)) ? Number(snapshot.retries) : 1,
        expected_tokens: Number.isFinite(Number(snapshot && snapshot.expected_tokens)) ? Number(snapshot.expected_tokens) : 1200,
        expected_model_calls: Number.isFinite(Number(snapshot && snapshot.expected_model_calls))
          ? Number(snapshot.expected_model_calls)
          : 8,
        risk_envelope: "Bounded webpage scenario with remote verification gates.",
        fallback_policy: "Controlled retry path with checkpointed evidence artifacts.",
        failure_modes: ["Runtime dependency", "Verification delay", "Provider recovery"]
      };
    }

    async _streamRunEvents(runId, runIdToken, sessionToken, hooks, snapshotRef) {
      const feed = [];
      let after = 0;
      let usedSse = false;

      const consumeEvent = async (rawEvent) => {
        const parsed = this._normalizeEvent(rawEvent);
        if (parsed.hdir_sequence !== null) {
          after = Math.max(after, parsed.hdir_sequence);
        }

        feed.push(parsed);
        if (hooks && typeof hooks.onStep === "function") {
          await hooks.onStep(parsed);
        }
        if (hooks && typeof hooks.onSnapshot === "function") {
          await hooks.onSnapshot(snapshotRef.snapshot);
        }
      };

      if (typeof EventSource !== "undefined") {
        try {
          usedSse = await new Promise((resolve) => {
            const streamUrl = this._resolveUrl(`/v1/runway/runs/${encodeURIComponent(runId)}/events/stream?after=${after}`);
            const source = new EventSource(streamUrl, { withCredentials: false });
            let done = false;

            const finish = (value) => {
              if (done) {
                return;
              }
              done = true;
              source.close();
              resolve(value);
            };

            const handlePayload = async (message) => {
              const parsed = this._parseEventPayload(message && message.data);
              if (!parsed || typeof parsed !== "object") {
                return;
              }

              if (parsed.snapshot && typeof parsed.snapshot === "object") {
                snapshotRef.snapshot = parsed.snapshot;
              }

              if (parsed.timeline && Array.isArray(parsed.timeline)) {
                snapshotRef.snapshot.timeline = parsed.timeline;
              }

              await consumeEvent(parsed);
            };

            source.addEventListener("runway", async (message) => {
              await handlePayload(message);
            });

            source.addEventListener("message", async (message) => {
              await handlePayload(message);
            });

            source.addEventListener("terminal", (message) => {
              const terminalPayload = this._parseEventPayload(message && message.data);
              if (terminalPayload && typeof terminalPayload === "object") {
                snapshotRef.snapshot = terminalPayload.snapshot || terminalPayload;
              }
              finish(true);
            });

            source.onerror = () => finish(false);
            setTimeout(() => finish(false), 180000);
          });
        } catch (_) {
          usedSse = false;
        }
      }

      if (!usedSse) {
        for (let i = 0; i < 240; i += 1) {
          const eventsResponse = await fetch(
            this._resolveUrl(`/v1/runway/runs/${encodeURIComponent(runId)}/events?after=${after}&limit=100`),
            { headers: { ...this._runHeaders(sessionToken) } }
          );
          if (!eventsResponse.ok) {
            throw new Error(`events_${eventsResponse.status}`);
          }

          const page = await this._readJson(eventsResponse);
          for (const event of Array.isArray(page.events) ? page.events : []) {
            await consumeEvent(event);
          }

          const snapshotResponse = await fetch(this._resolveUrl(`/v1/runway/runs/${encodeURIComponent(runId)}`), {
            headers: { ...this._runHeaders(sessionToken) }
          });

          if (snapshotResponse.ok) {
            snapshotRef.snapshot = await this._readJson(snapshotResponse);
            if (hooks && typeof hooks.onSnapshot === "function") {
              await hooks.onSnapshot(snapshotRef.snapshot);
            }

            if (this._isRunFinalStatus(snapshotRef.snapshot && snapshotRef.snapshot.status)) {
              break;
            }
          }

          await new Promise((resolve) => setTimeout(resolve, 500));
        }
      } else if (!this._isRunFinal(snapshotRef.snapshot && snapshotRef.snapshot.status)) {
        snapshotRef.snapshot = await this._pollRunState(runId, sessionToken, snapshotRef.snapshot);
      }

      return { feed, transport: usedSse ? "sse" : "poll" };
    }

    async run(profileOrScenario, hooks) {
      const scenarioProfile = typeof profileOrScenario === "object" && profileOrScenario !== null ? profileOrScenario : null;
      const scenarioName = scenarioProfile
        ? scenarioProfile.id || scenarioProfile.runType || scenarioProfile.name || "webpage-build-deploy"
        : String(profileOrScenario || "decision");
      const normalizedScenario = String(scenarioName || "webpage-build-deploy").toLowerCase();
      const resolvedRunType = normalizedScenario === "webpage" ? "webpage-build-deploy" : normalizedScenario;
      const goal = this.buildGoal(scenarioName, scenarioProfile);
      const started = Date.now();
      const snapshotRef = { snapshot: {} };
      const sessionToken = await this.ensureSession();

      try {
        const createPayload = {
          scenario: resolvedRunType,
          goal,
          mode: "live",
          run_type: resolvedRunType,
          scenario_profile: {
            name: scenarioName,
            id: scenarioProfile && (scenarioProfile.id || scenarioProfile.runType) ? (scenarioProfile.id || scenarioProfile.runType) : scenarioName,
            reliability_target: scenarioProfile && scenarioProfile.reliability_target,
            cost_cap_usd: scenarioProfile && scenarioProfile.cost_cap_usd
          }
        };

        const createResponse = await fetch(this._resolveUrl("/v1/runway/runs"), {
          method: "POST",
          headers: {
            "content-type": "application/json",
            ...this._runHeaders(sessionToken, {
              "idempotency-key": `browser-${Date.now()}-${Math.random().toString(16).slice(2)}`
            })
          },
          body: JSON.stringify(createPayload)
        });
        if (!createResponse.ok) {
          this.offline = createResponse.status >= 500;
          throw new Error(`create_${createResponse.status}`);
        }

        snapshotRef.snapshot = await this._readJson(createResponse);
        const runId = this._extractRunId(snapshotRef.snapshot, createResponse);
        if (!runId) {
          throw new Error("run_id_missing");
        }

        const approveResponse = await fetch(this._resolveUrl(`/v1/runway/runs/${encodeURIComponent(runId)}/approve`), {
          method: "POST",
          headers: {
            "content-type": "application/json",
            ...this._runHeaders(sessionToken)
          },
          body: "{}"
        });
        if (!approveResponse.ok && approveResponse.status !== 404) {
          throw new Error(`approve_${approveResponse.status}`);
        }
        if (approveResponse.ok) {
          snapshotRef.snapshot = await this._readJson(approveResponse);
        }

        const { feed, transport } = await this._streamRunEvents(runId, runId, sessionToken, hooks, snapshotRef);
        const finalStatus = snapshotRef.snapshot && snapshotRef.snapshot.status ? snapshotRef.snapshot.status : "UNKNOWN";
        const runProfile = this._buildRuntimeProfile(scenarioProfile, scenarioName, goal, snapshotRef.snapshot);
        const receipt = await this._fetchReceipt(runId, sessionToken);

        if (!this._isRunFinalStatus(finalStatus) && transport !== "poll") {
          snapshotRef.snapshot = await this._pollRunState(runId, sessionToken, snapshotRef.snapshot);
        }

        return {
          runId,
          source: "hdir-gateway",
          mode: "live",
          profile: runProfile,
          feed,
          snapshot: snapshotRef.snapshot,
          receipt,
          finalStatus,
          transport,
          elapsedMs: Date.now() - started
        };
      } catch (error) {
        this.offline = true;
        throw error;
      }
    }
  }

  root.LiveRunwayProvider = LiveRunwayProvider;
})(window);
